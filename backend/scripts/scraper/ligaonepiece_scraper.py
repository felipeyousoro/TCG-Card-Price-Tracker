import json
import re
from typing import List, Dict

import requests
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:151.0) Gecko/20100101 Firefox/151.0"

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})


def scrape_collection(url: str = "") -> List[Dict[str, str]]:
    if not url:
        return []

    response = session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')

    script_tags = soup.find_all('script', type='text/javascript')
    result = []
    for script_tag in script_tags:
        if script_tag.string:
            script_content = script_tag.string
            match = re.search(
                r'var\s+cardsjson\s*=\s*(\[\{.*?}]);',
                script_content,
                re.DOTALL
            )

            if match:
                json_str = match.group(1)
                try:
                    cards_data = json.loads(json_str)
                    for card in cards_data:
                        result.append({
                            'nome': card.get('nEN', ''),
                            'codigo': card.get('sN', ''),
                            'colecao': card.get('sSigla', ''),
                            'raridade': card.get('iR', 0),
                            'url_imagem': card.get('sP', '')
                        })
                    break
                except json.JSONDecodeError:
                    continue

    return result


def scrape_card(url: str = "") -> List[Dict[str, str]]:
    response = session.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    script_tags = soup.find_all('script', type='text/javascript')
    result = []
    for script_tag in script_tags:
        if script_tag.string:
            script_content = script_tag.string
            match = re.search(r'var cards_editions = (\[.*?\]);', script_content, re.DOTALL)
            if match:
                json_str = match.group(1)
                cards_data = json.loads(json_str)
                if cards_data and len(cards_data) > 0:
                    card = cards_data[0]
                    if 'price' in card:
                        prices = card['price']
                        print(prices)
                        for price_info in normalize_prices(prices):
                            result.append(price_info)
                break
    return result


def normalize_prices(prices):
    normalized = []

    if isinstance(prices, dict):
        iterable = prices.values()
    elif isinstance(prices, list):
        iterable = prices
    else:
        return []

    for item in iterable:
        if isinstance(item, list):
            if not item:
                continue
            item = item[0]

        if not isinstance(item, dict):
            continue

        normalized.append({
            'p': item.get('p'),
            'm': item.get('m'),
            'g': item.get('g')
        })

    return normalized
