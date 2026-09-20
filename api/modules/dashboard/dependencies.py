from typing import Annotated

from fastapi import Depends

from .service import DashboardService


def get_dashboard_service() -> DashboardService:
    return DashboardService()


DashboardServiceDep = Annotated[DashboardService, Depends(get_dashboard_service)]
