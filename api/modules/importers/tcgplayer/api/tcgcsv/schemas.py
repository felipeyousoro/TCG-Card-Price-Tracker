from pydantic import BaseModel, ConfigDict, Field


class TcgcsvExtendedField(BaseModel):
    """One named extra field on a TCGCSV product."""

    model_config = ConfigDict(extra="ignore")

    name: str
    value: str | None = None


class TcgcsvProduct(BaseModel):
    """Raw TCGCSV product payload for one TCGPlayer SKU."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    product_id: int = Field(alias="productId")
    name: str
    image_url: str | None = Field(default=None, alias="imageUrl")
    extended_data: list[TcgcsvExtendedField] = Field(default_factory=list, alias="extendedData")
