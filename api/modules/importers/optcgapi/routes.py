from fastapi import APIRouter

from ....common.utils.error_handler import handle_exception
from ....core.auth.http_exceptions import HTTPException
from ....core.dependencies import AsyncSessionDep, CurrentUserDep
from ..base import ImportResult
from .dependencies import OptcgApiImporterDep

router = APIRouter(tags=["Importers"])


@router.post(
    "/all-sets",
    response_model=ImportResult,
    summary="Import all OPTCG set cards from optcgapi",
    description="""
            Fetches the full card catalog from optcgapi.com and inserts rows
            that do not already exist for the same card name and set.

            Existing matches are skipped. Prices from the source are not stored.
            """,
    responses={
        200: {"description": "Import finished with inserted and skipped counts"},
        401: {"description": "Not authenticated"},
        502: {"description": "Failed to fetch data from optcgapi"},
    },
    response_description="Inserted, skipped, and fetched counts for this import run",
)
async def import_all_sets(
    db: AsyncSessionDep,
    _: CurrentUserDep,
    importer: OptcgApiImporterDep,
) -> ImportResult:
    """Import missing OPTCG catalog cards from optcgapi.com."""
    try:
        return await importer.import_all_sets(db)
    except Exception as exc:
        http_exception = handle_exception(exc)
        if http_exception:
            raise http_exception
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
