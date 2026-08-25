from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .enums import ProductCategory


class ProductRead(BaseModel):
    """Full product catalog row."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: ProductCategory
    set_name: str | None = None
    image_url: str | None = None
    created_by_user_id: int | None = None
    created_at: datetime
    updated_at: datetime | None = Field(default=None)


class ProductListItem(BaseModel):
    """Slim product row for search results."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: ProductCategory
    set_name: str | None = None
    image_url: str | None = None


class ProductCreate(BaseModel):
    """Payload to add a shared catalog product."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=200)
    category: ProductCategory = ProductCategory.OTHER
    set_name: str | None = Field(default=None, max_length=200)
    image_url: str | None = None
