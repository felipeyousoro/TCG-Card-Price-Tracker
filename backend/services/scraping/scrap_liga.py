from typing import List, Dict

from sqlalchemy.orm import Session

from models import Card, CardVersion, Collection, Rarity
from scripts.scraper.ligaonepiece_list import scrap_list


class ScrapLiga:
    def __init__(self, session: Session):
        self.session = session

    def scrap_and_insert(self, url: str) -> None:
        scraped_data = scrap_list(url)
        processed_data = self.process_scraped_data(scraped_data)

        for data in processed_data:
            collection = self.session.query(Collection).filter_by(name=data['colecao']).first()
            if not collection:
                # TODO, trocar game_id por ENUM
                collection = Collection(game_id=1, name=data['colecao'])
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

    def process_scraped_data(self, scraped_data: List[Dict[str, str]]) -> List[Dict]:
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
