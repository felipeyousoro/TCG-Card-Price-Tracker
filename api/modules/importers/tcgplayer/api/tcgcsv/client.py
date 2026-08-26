import asyncio
import logging

import httpx

from ......common.exceptions import ImporterFetchError, ValidationError

logger = logging.getLogger(__name__)

_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
}


class TcgcsvClient:
    """HTTP client for tcgcsv.com TCGPlayer group endpoints."""

    def __init__(self, base_url: str, timeout: float) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    @property
    def timeout(self) -> float:
        return self._timeout

    def products_url(self, category_id: int, group_id: int) -> str:
        """TCGCSV products list for a TCGPlayer category/group."""
        return f"{self._base_url}/tcgplayer/{category_id}/{group_id}/products"

    def prices_url(self, category_id: int, group_id: int) -> str:
        """TCGCSV prices list for a TCGPlayer category/group."""
        return f"{self._base_url}/tcgplayer/{category_id}/{group_id}/prices"

    async def fetch_products(self, category_id: int, group_id: int) -> list[dict[str, object]]:
        """Fetch the TCGCSV products list for one TCGPlayer group."""
        url = self.products_url(category_id, group_id)
        try:
            async with httpx.AsyncClient(
                timeout=self._timeout,
                follow_redirects=True,
                headers=_BROWSER_HEADERS,
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = await asyncio.to_thread(response.json)
        except httpx.HTTPError as exc:
            message = _http_error_message(category_id, group_id, exc)
            logger.warning("%s", message)
            raise ImporterFetchError(message) from exc

        if not isinstance(data, dict):
            raise ValidationError("TCGCSV products response must be a JSON object")
        if not data.get("success"):
            errors = data.get("errors") or []
            raise ImporterFetchError(
                f"TCGCSV products request was unsuccessful for {category_id}/{group_id}: {errors}"
            )
        results = data.get("results")
        if not isinstance(results, list):
            raise ValidationError("TCGCSV products response must include a results list")
        return results


def _http_error_message(category_id: int, group_id: int, exc: httpx.HTTPError) -> str:
    parts = [
        f"Failed to fetch TCGCSV products for {category_id}/{group_id}",
        type(exc).__name__,
    ]
    if isinstance(exc, httpx.HTTPStatusError):
        parts.append(f"status={exc.response.status_code}")
    detail = str(exc).strip()
    if detail:
        parts.append(detail[:500])
    return ": ".join(parts)
