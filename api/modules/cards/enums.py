"""Enums for the shared card catalog."""

from enum import StrEnum


class CardGame(StrEnum):
    """TCG whose identity row lives on the shared card table."""

    OPTCG = "optcg"
    MTG = "mtg"
    POKEMON = "pokemon"
