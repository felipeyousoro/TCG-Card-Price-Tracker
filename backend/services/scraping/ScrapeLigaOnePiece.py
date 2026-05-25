from decimal import Decimal
from typing import List, Dict

from sqlalchemy.orm import Session

from models import OnePieceCard, OnePieceCardVersion, Collection, Rarity, OnePieceCardStock, GameName, SupplierName
from scripts.scraper.ligaonepiece_scraper import scrape_card, scrape_collection


class ScrapeLigaOnePiece:
    def __init__(self, session: Session):
        self.session = session

    def scrape_collection(self, url: str) -> None:
        scraped_data = scrape_collection(url)
        processed_data = self.__process_scraped_collection(scraped_data)

        for data in processed_data:
            collection = self.session.query(Collection).filter_by(name=data['colecao_original']).first()
            if not collection:
                collection = Collection(game_id=GameName.ONE_PIECE.value, name=data['colecao_original'])
                self.session.add(collection)
                self.session.commit()

            card = self.session.query(OnePieceCard).filter_by(
                code=data['codigo'],
                collection_id=collection.id
            ).first()
            if not card:
                card = OnePieceCard(code=data['codigo'], rarity=data['rarity'], collection_id=collection.id)
                self.session.add(card)
                self.session.commit()

            card_version = self.session.query(OnePieceCardVersion).filter_by(
                name=data['codigo_print'],
                card_id=card.id
            ).first()
            if not card_version:
                card_version = OnePieceCardVersion(
                    name=data['nome'],
                    code=data['codigo_print'],
                    collection_print=data['colecao'],
                    card_id=card.id
                )
                self.session.add(card_version)
                self.session.commit()

    def __build_card_url(self, card: OnePieceCardVersion) -> str:
        base_url = "https://www.ligaonepiece.com.br/?view=cards/card&card=" + card.name.replace("&", "%26") + '&ed=' + card.collection_print + '&num=' + card.code
        return base_url

    def scrape_card(self, card: OnePieceCardVersion) -> None:
        url = self.__build_card_url(card)
        print(url)
        scraped_data = scrape_card(url)

        scraped_data = self.__process_scraped_card(scraped_data)

        card_stock = OnePieceCardStock(
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
            p = item['p']
            m = item['m']
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
            rarity_int = item.get('raridade', -1)
            rarity_str = Rarity.from_int(rarity_int)
            if rarity_str is None or rarity_str == Rarity.DON.label:
                continue

            processed_data.append({
                'nome': item.get('nome'),
                'colecao': item.get('colecao'),
                'colecao_original': item.get('codigo', '').split('-')[0],
                'codigo': '-'.join(item.get('codigo', '').split('-')[:2]),
                'codigo_print': item.get('codigo', ''),
                'rarity': rarity_str,
            })

            # print(item)
        return processed_data
