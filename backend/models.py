from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Rarity(Enum):
    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    SR = 4
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
            6: "Leader",
            7: "Secret",
            8: "Don"
        }
        return labels.get(self.value, "Common")

    @classmethod
    def from_int(cls, rarity_int: int) -> str:
        try:
            rarity = cls(rarity_int)
            return rarity.label
        except ValueError:
            return cls.COMMON.label


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

    cards = relationship("Card", back_populates="collection")


class Card(Base):
    __tablename__ = "card"

    id = Column(Integer, primary_key=True)
    code = Column(String, nullable=False)
    rarity = Column(String, nullable=False)

    collection_id = Column(Integer, ForeignKey("collection.id"), nullable=False)
    collection = relationship("Collection", back_populates="cards")

    versions = relationship("CardVersion", back_populates="card")


class Supplier(Base):
    __tablename__ = "supplier"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    stocks = relationship("CardStock", back_populates="supplier")


class CardVersion(Base):
    __tablename__ = "card_version"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)

    card_id = Column(Integer, ForeignKey("card.id"), nullable=False)
    card = relationship("Card", back_populates="versions")

    stocks = relationship("CardStock", back_populates="card_version")


class CardStock(Base):
    __tablename__ = "card_stock"

    id = Column(Integer, primary_key=True)

    card_version_id = Column(Integer, ForeignKey("card_version.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("supplier.id"), nullable=False)

    url = Column(Text, nullable=False)

    card_version = relationship("CardVersion", back_populates="stocks")
    supplier = relationship("Supplier", back_populates="stocks")
