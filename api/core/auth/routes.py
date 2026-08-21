import inspect
from typing import Any

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel, Field

from .http_exceptions import UnauthorizedException
from .session.dependencies import authenticate_user
from ..config.settings import get_settings
from ..dependencies import (
    AsyncSessionDep,
    CurrentSessionDataDep,
    OptionalSessionDataDep,
    SessionManagerDep,
)
from ...modules.user.crud import crud_users

settings = get_settings()
# logger = get_logger()

router = APIRouter(tags=["Authentication"])


class LoginRequest(BaseModel):
    """Username and password submitted by the admin shell."""

    username: str = Field(min_length=1, max_length=20)
    password: str = Field(min_length=1)


@router.post(
    "/login",
    summary="User Login",
    description="""
            Authenticates a user and creates a new session.

            This endpoint accepts username and password credentials and verifies them.
            On successful authentication:
            - A new session is created
            - A session ID is set as an HTTP-only cookie
            - A CSRF token is generated for protection against CSRF attacks

            The endpoint is protected by rate limiting to prevent brute force attacks.
            After multiple failed attempts, further login attempts will be temporarily blocked.
            """,
    responses={
        200: {"description": "Login successful, session created"},
        401: {"description": "Authentication failed or rate limit exceeded"},
        429: {"description": "Too many login attempts, try again later"},
    },
    response_description="CSRF token for use in subsequent requests",
)
async def login(
        request: Request,
        response: Response,
        form_data: LoginRequest,
        db: AsyncSessionDep,
        session_manager: SessionManagerDep,
) -> dict[str, str]:
    """Login endpoint to get session cookies.

    The session ID is set as an HTTP-only cookie.
    The CSRF token is set as a regular cookie and returned in the response.
    This endpoint is protected by rate limiting to prevent brute force attacks.
    """
    ip_address = request.client.host if request.client and hasattr(request.client, "host") else "unknown"

    is_allowed, attempts_remaining = await session_manager.track_login_attempt(
        ip_address=ip_address, username=form_data.username, success=False
    )

    if not is_allowed:
        # logger.warning(f"Login rate limit exceeded for {form_data.username} from IP {ip_address}")
        raise UnauthorizedException("Too many failed login attempts. Please try again later.")

    user = await authenticate_user(username=form_data.username, password=form_data.password, db=db)

    if user is None:
        # logger.warning(f"Failed login attempt for {form_data.username} from IP {ip_address}")
        raise UnauthorizedException("Incorrect username or password")

    try:
        await session_manager.track_login_attempt(ip_address=ip_address, username=form_data.username, success=True)

        session_id, csrf_token = await session_manager.create_session(
            request=request,
            user_id=user["id"],
            metadata={
                "login_type": "password",
                "username": user["username"],
            },
        )

        session_manager.set_session_cookies(
            response=response,
            session_id=session_id,
            csrf_token=csrf_token,
            secure=settings.SESSION_SECURE_COOKIES,
            path="/",
        )

        return {"csrf_token": csrf_token}

    except Exception as e:
        # logger.error(f"Error during login: {str(e)}", exc_info=True)
        raise UnauthorizedException("An error occurred during login")


@router.post(
    "/logout",
    summary="User Logout",
    description="""
            Terminates the current user session.

            This endpoint:
            - Invalidates the active session in the storage backend
            - Clears all session-related cookies from the client

            After logout, the user will need to authenticate again to access
            protected resources. Any existing session tokens will no longer be valid.
            """,
    responses={200: {"description": "Logout successful, session terminated"},
               401: {"description": "Not authenticated"}},
    response_description="Confirmation of successful logout",
)
async def logout(
        request: Request,
        response: Response,
        session_data: CurrentSessionDataDep,
        session_manager: SessionManagerDep,
) -> dict[str, str]:
    """Logout endpoint to terminate the session and clear cookies."""
    await session_manager.terminate_session(session_data.session_id)
    session_manager.clear_session_cookies(response)

    return {"message": "Logged out successfully"}


@router.post(
    "/refresh-csrf",
    summary="Refresh CSRF Token",
    description="""
            Generates a new CSRF token for the current session.

            This endpoint should be called to obtain a fresh CSRF token when:
            - The current token is about to expire
            - After a certain period of inactivity
            - When increased security is needed for sensitive operations

            The new token is returned in the response and also set as a cookie.
            """,
    responses={200: {"description": "New CSRF token generated successfully"},
               401: {"description": "Not authenticated"}},
    response_description="The new CSRF token for the session",
)
async def refresh_csrf_token(
        request: Request,
        response: Response,
        session_data: CurrentSessionDataDep,
        session_manager: SessionManagerDep,
) -> dict[str, str]:
    """Generate a new CSRF token for the current session."""
    csrf_token = await session_manager.regenerate_csrf_token(
        user_id=session_data.user_id,
        session_id=session_data.session_id,
    )

    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        max_age=int(session_manager.session_timeout.total_seconds()),
        path="/",
        httponly=False,
        secure=settings.SESSION_SECURE_COOKIES,
        samesite="lax",
    )

    return {"csrf_token": csrf_token}


def _is_provider_valid(provider_value: Any, expected_provider: str) -> bool:
    """Check if a provider value matches the expected provider name.

    This handles different types of values (strings, objects, mocks) safely.

    Args:
        provider_value: The provider value to check (could be a string, object, or mock)
        expected_provider: The expected provider name (e.g., "google" or "github")

    Returns:
        bool: True if the provider is valid, False otherwise
    """
    if provider_value is None:
        return False

    if isinstance(provider_value, str):
        return provider_value.lower() == expected_provider.lower()

    if hasattr(provider_value, "name") and isinstance(getattr(provider_value, "name", None), str):
        name_value: str = getattr(provider_value, "name")
        return name_value.lower() == expected_provider.lower()

    if inspect.iscoroutine(provider_value) or inspect.isawaitable(provider_value):
        return expected_provider.lower() in str(provider_value).lower()

    try:
        return expected_provider.lower() in str(provider_value).lower()
    except Exception:
        return False


@router.get("/check-auth")
async def check_auth(
        session_data: OptionalSessionDataDep,
        db: AsyncSessionDep,
) -> dict[str, Any]:
    """
    Check if the user is authenticated and return basic user information.

    This is useful for clients to verify authentication status and can be used
    with both cookie-based and API-based authentication.

    Args:
        session_data: The session data if the user is authenticated

    Returns:
        Authentication status and user information if authenticated
    """
    if not session_data:
        return {"authenticated": False, "message": "Not authenticated"}

    try:
        user = await crud_users.get(db=db, id=session_data.user_id)

        if not user:
            return {"authenticated": False, "message": "User not found"}

        return {
            "authenticated": True,
            "user": {
                "id": user["id"],
                "username": user["username"],
            },
            "session": {
                "created_at": session_data.created_at.isoformat() if session_data.created_at else None,
                "last_activity": session_data.last_activity.isoformat() if session_data.last_activity else None,
            },
        }
    except Exception as e:
        # logger.error(f"Error checking authentication: {str(e)}", exc_info=True)
        return {"authenticated": False, "message": "Error checking authentication status"}
