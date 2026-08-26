class TcgcsvClient:
    """URL builders for tcgcsv.com TCGPlayer group endpoints."""

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
