"""Enums for stock transactions and holdings."""

from enum import StrEnum


class TransactionType(StrEnum):
    """Whether a recorded event is a purchase or a sale."""

    BUY = "buy"
    SELL = "sell"


class ItemType(StrEnum):
    """Catalog kind referenced by a stock line or holding."""

    CARD = "card"
    PRODUCT = "product"
