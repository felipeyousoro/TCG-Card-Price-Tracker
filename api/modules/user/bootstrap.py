"""Startup helpers for the default admin account."""

import logging

from ...core.auth.utils import get_password_hash
from ...core.config.settings import get_settings
from ...core.database.session import local_session
from .crud import crud_users
from .models import User

logger = logging.getLogger(__name__)


async def ensure_admin_user() -> None:
    """Create the configured admin user when it does not already exist."""
    settings = get_settings()
    username = (settings.ADMIN_USERNAME or "admin").strip().lower()
    password = settings.ADMIN_PASSWORD or "admin"
    name = settings.ADMIN_NAME or "Admin"

    async with local_session() as db:
        exists = await crud_users.exists(db=db, username=username)
        if exists:
            return

        db.add(
            User(
                name=name,
                username=username,
                hashed_password=get_password_hash(password),
            )
        )
        await db.commit()
        logger.info("Seeded admin user '%s'", username)
