from decimal import Decimal
from typing import List, Dict

from sqlalchemy.orm import Session

from models import Card, CardVersion, Collection, Rarity, CardStock, GameName, SupplierName
from scripts.scraper.ligaonepiece_card import scrap_card
from scripts.scraper.ligaonepiece_collection import scrap_collection


class ScrapLiga:
    def __init__(self, session: Session):
        self.session = session

    def scrap_collection(self, url: str) -> None:
        scraped_data = scrap_collection(url)
        processed_data = self.__process_scraped_collection(scraped_data)

        for data in processed_data:
            collection = self.session.query(Collection).filter_by(name=data['colecao']).first()
            if not collection:
                collection = Collection(game_id=GameName.ONE_PIECE.value, name=data['colecao'])
                self.session.add(collection)
                self.session.commit()

            card = self.session.query(Card).filter_by(
                code=data['codigo'],
                collection_id=collection.id
            ).first()
            if not card:
                card = Card(code=data['codigo'], rarity=data['rarity'], collection_id=collection.id)
                self.session.add(card)
                self.session.commit()

            card_version = self.session.query(CardVersion).filter_by(
                name=data['codigo_completo'],
                card_id=card.id
            ).first()
            if not card_version:
                card_version = CardVersion(
                    name=data['nome'],
                    code=data['codigo_completo'],
                    card_id=card.id
                )
                self.session.add(card_version)
                self.session.commit()

    def __build_card_url(self, card: CardVersion) -> str:
        base_url = "https://www.ligaonepiece.com.br/?view=cards/card&card=" + card.name
        return base_url

    def scrap_card(self, card: CardVersion) -> None:
        url = self.__build_card_url(card)
        scraped_data = scrap_card(url)
        print(scraped_data, url, card.name, card)
        scraped_data = self.__process_scraped_card(scraped_data)

        card_stock = CardStock(
            card_version_id=card.id,
            supplier_id=SupplierName.LIGA_ONE_PIECE.value,
            lowest_price=scraped_data['lowest_price'],
            avg_price=scraped_data['avg_price']
        )

        self.session.add(card_stock)
        self.session.commit()

    def __process_scraped_card(self, scraped_data: List[Dict[str, str]]) -> Dict[str, Decimal]:
        lowest_price = None
        avg_price = None

        for item in scraped_data:
            p = item.get('p')
            m = item.get('m')
            if p and lowest_price is None or (Decimal(p) < lowest_price):
                lowest_price = Decimal(p)
            if m and avg_price is None or (Decimal(m) < avg_price):
                avg_price = Decimal(m)

        return {
            'lowest_price': lowest_price,
            'avg_price': avg_price
        }

    def __process_scraped_collection(self, scraped_data: List[Dict[str, str]]) -> List[Dict]:
        processed_data = []
        for item in scraped_data:
            rarity_int = item.get('iR', -1)
            rarity_str = Rarity.from_int(rarity_int)
            if rarity_str is None or rarity_str == Rarity.DON.label:
                continue

            processed_data.append({
                'nome': item.get('nEN'),
                'colecao': item.get('sN', '').split('-')[0],
                'codigo': '-'.join(item.get('sN', '').split('-')[:2]),
                'codigo_completo': item.get('sN', ''),
                'rarity': rarity_str,
            })
        return processed_data
