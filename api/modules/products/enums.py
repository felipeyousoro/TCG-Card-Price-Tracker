"""Enums for the shared product catalog."""

from enum import StrEnum


class ProductCategory(StrEnum):
    """Kind of sealed or bulk product a user can stock."""

    BOX = "box"
    CASE = "case"
    PACK = "pack"
    STARTER_DECK = "starter_deck"
    OTHER = "other"
