import requests
import re
import json
from typing import List, Dict
from bs4 import BeautifulSoup

def scrap_card(url: str = "") -> List[Dict[str, str]]:
    response = requests.get(url)
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