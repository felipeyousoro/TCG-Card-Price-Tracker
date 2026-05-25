from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Text,
    DECIMAL
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Rarity(Enum):
    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    SR = 4
    PROMO = 5
    LEADER = 6
    SECRET = 7
    DON = 8

    @property
    def label(self) -> str:
        labels = {
            1: "Common",
            2: "Uncommon",
            3: "Rare",
            4: "SR",
            5: "Promo",
            6: "Leader",
            7: "Secret",
            8: "Don",
        }

        return labels.get(self.value)

    @classmethod
    def from_int(cls, rarity_int: int) -> str | None:
        try:
            rarity = cls(rarity_int)
            return rarity.label
        except ValueError:
            return None

class GameName(Enum):
    ONE_PIECE = 1

    @property
    def label(self) -> str:
        labels = {
            1: "One Piece",
        }
        return labels.get(self.value)

    @classmethod
    def from_int(cls, game_int: int) -> str | None:
        try:
            game = cls(game_int)
            return game.label
        except ValueError:
            return None

class SupplierName(Enum):
    LIGA_ONE_PIECE = 1

    @property
    def label(self) -> str:
        labels = {
            1: "Liga One Piece",
        }
        return labels.get(self.value)

    @classmethod
    def from_int(cls, supplier_int: int) -> str | None:
        try:
            supplier = cls(supplier_int)
            return supplier.label
        except ValueError:
            return None

class Game(Base):
    __tablename__ = "game"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    collections = relationship("Collection", back_populates="game")


class Collection(Base):
    __tablename__ = "collection"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    game_id = Column(Integer, ForeignKey("game.id"), nullable=False)
    game = relationship("Game", back_populates="collections")

    cards = relationship("OnePieceCard", back_populates="collection")


class OnePieceCard(Base):
    __tablename__ = "onepiece_card"

    id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False)
    rarity = Column(String, nullable=False)

    collection_id = Column(Integer, ForeignKey("collection.id"), nullable=False)
    collection = relationship("Collection", back_populates="cards")

    versions = relationship("OnePieceCardVersion", back_populates="card")


class Supplier(Base):
    __tablename__ = "supplier"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    stocks = relationship("OnePieceCardStock", back_populates="supplier")


class OnePieceCardVersion(Base):
    __tablename__ = "onepiece_card_version"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)
    collection_print = Column(String, nullable=False)

    card_id = Column(Integer, ForeignKey("onepiece_card.id"), nullable=False)
    card = relationship("OnePieceCard", back_populates="versions")

    stocks = relationship("OnePieceCardStock", back_populates="card_version")


class OnePieceCardStock(Base):
    __tablename__ = "onepiece_card_stock"

    id = Column(Integer, primary_key=True)

    lowest_price = Column(DECIMAL, nullable=False)
    avg_price = Column(DECIMAL, nullable=False)

    card_version_id = Column(Integer, ForeignKey("onepiece_card_version.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("supplier.id"), nullable=False)

    card_version = relationship("OnePieceCardVersion", back_populates="stocks")
    supplier = relationship("Supplier", back_populates="stocks")
