from fastapi import APIRouter

from ....core.auth.routes import router as auth_router
from ....modules.cards.routes import router as cards_router
from ....modules.dashboard.routes import router as dashboard_router
from ....modules.favorites.routes import router as favorites_router
from ....modules.importers.routes import router as importers_router
from ....modules.optcg.routes import router as optcg_router
from ....modules.products.routes import router as products_router
from ....modules.stock.routes import router as stock_router
from ....modules.user.routes import router as users_router

router = APIRouter(prefix="/v1")
router.include_router(users_router, prefix="/users")
router.include_router(auth_router, prefix="/auth")
router.include_router(importers_router)
router.include_router(cards_router)
router.include_router(optcg_router)
router.include_router(products_router)
router.include_router(stock_router)
router.include_router(dashboard_router)
router.include_router(favorites_router)
