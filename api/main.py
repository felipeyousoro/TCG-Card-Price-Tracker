from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from .core.app_factory import create_application, lifespan_factory
from .core.config.settings import get_settings
from .core.security import validate_production_security
from .interfaces.api import router
from .modules.importers.jobs.service import fail_stale_sync_jobs
from .modules.user.bootstrap import ensure_admin_user
# from .admin.initialize import create_admin_interface

settings = get_settings()


@asynccontextmanager
async def lifespan_with_security(app: FastAPI) -> AsyncGenerator[None, None]:
    """Custom lifespan that includes security validation."""
    if settings.PRODUCTION_SECURITY_VALIDATION_ENABLED:
        validate_production_security(settings)

    default_lifespan = lifespan_factory(settings)

    async with default_lifespan(app):
        await fail_stale_sync_jobs()
        await ensure_admin_user()
        yield


app = create_application(
    router=router,
    settings=settings,
    lifespan=lifespan_with_security,
    create_tables_on_startup=None,
    enable_cors=None,
    cors_origins=None,
    enable_docs_in_production=None,
    docs_production_dependency=None,
    enable_gzip=None,
    openapi_prefix=None,
    title="TCG Card Price Tracker",
    summary="API for tracking One Piece TCG card data and prices",
    description="""
    # TCG Card Price Tracker

    Modular FastAPI backend for OPTCG card data:

    * Vertical-slice modules and a clean core layer
    * Session-based auth
    * OPTCG card catalog
    """,
    version="0.1.0",
    contact={
        "name": "Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "identifier": "MIT",
    },
    openapi_tags=None,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
# create_admin_interface(app)


@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    """Health check endpoint for monitoring and load balancers."""
    return {"status": "healthy"}