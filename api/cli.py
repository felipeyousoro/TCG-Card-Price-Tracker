import asyncio

import typer

from .common.exceptions import ImporterFetchError, ValidationError
from .core.database.session import local_session
from .modules.importers.base import ImportResult
from .modules.importers.registry import get_importer

app = typer.Typer(help="TCG Card Price Tracker management commands.", no_args_is_help=True)


@app.callback()
def _root() -> None:
    """TCG Card Price Tracker management commands."""
    return None


async def _import_all_sets(source: str) -> ImportResult:
    importer = get_importer(source)
    async with local_session() as db:
        return await importer.import_all_sets(db)


@app.command("import-all-sets")
def import_all_sets(
    source: str = typer.Option(..., "--source", help="Importer source key, e.g. optcgapi"),
) -> None:
    """Import missing OPTCG catalog cards from a registered source."""
    try:
        result = asyncio.run(_import_all_sets(source))
    except (ValidationError, ImporterFetchError) as exc:
        typer.secho(str(exc), fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(
        f"Imported from {result.source}: fetched={result.fetched} "
        f"inserted={result.inserted} skipped={result.skipped}"
    )


def main() -> None:
    app()
