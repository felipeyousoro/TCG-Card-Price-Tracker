import json
import re
from typing import List, Dict

import requests
from bs4 import BeautifulSoup


def scrap_list(url: str = "") -> List[Dict[str, str]]:
    if not url:
        return []

    response = requests.get(url)
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
                            'nEN': card.get('nEN', ''),
                            'sN': card.get('sN', ''),
                            'sSigla': card.get('sSigla', ''),
                            'iR': card.get('iR', 0)
                        })
                    break
                except json.JSONDecodeError:
                    continue

    return result