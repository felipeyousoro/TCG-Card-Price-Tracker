from fastapi import APIRouter

from ....core.auth.routes import router as auth_router
from ....modules.importers.optcgapi.routes import router as optcgapi_importer_router
from ....modules.user.routes import router as users_router

router = APIRouter(prefix="/v1")
router.include_router(users_router, prefix="/users")
router.include_router(auth_router, prefix="/auth")
router.include_router(optcgapi_importer_router, prefix="/importers/optcgapi")
