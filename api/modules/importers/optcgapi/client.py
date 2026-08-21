import httpx

from ....common.exceptions import ImporterFetchError, ValidationError

ALL_SET_CARDS_PATH = "/api/allSetCards/"


class OptcgApiClient:
    """HTTP client for optcgapi.com catalog endpoints."""

    def __init__(self, base_url: str, timeout: float) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def fetch_all_set_cards(self) -> list[dict[str, object]]:
        """Fetch the full all-sets card list from optcgapi."""
        url = f"{self._base_url}{ALL_SET_CARDS_PATH}"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            raise ImporterFetchError("Failed to fetch all set cards from optcgapi") from exc

        if not isinstance(data, list):
            raise ValidationError("optcgapi allSetCards response must be a JSON list")
        return data
