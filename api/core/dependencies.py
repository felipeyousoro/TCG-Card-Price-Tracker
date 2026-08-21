from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .auth.session.dependencies import (
    get_current_session_data,
    get_current_superuser,
    get_current_user,
    get_optional_user,
    get_session_from_cookie,
    get_session_manager,
)
from .auth.session.manager import SessionManager
from .auth.session.schemas import SessionData
from .database.session import async_session

# Database
AsyncSessionDep = Annotated[AsyncSession, Depends(async_session)]

# Users
CurrentUserDep = Annotated[dict[str, Any], Depends(get_current_user)]
CurrentSuperUserDep = Annotated[dict[str, Any], Depends(get_current_superuser)]
OptionalUserDep = Annotated[dict[str, Any] | None, Depends(get_optional_user)]

# Sessions
SessionManagerDep = Annotated[SessionManager, Depends(get_session_manager)]
CurrentSessionDataDep = Annotated[SessionData, Depends(get_current_session_data)]
OptionalSessionDataDep = Annotated[SessionData | None, Depends(get_session_from_cookie)]
