from fastcrud import FastCRUD

from .models import Card

crud_cards: FastCRUD = FastCRUD(Card)
