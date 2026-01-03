import json
import requests
from pathlib import Path
from typing import List

API_BASE_URL = "http://localhost:8000"
ENDPOINT = "/scrap-list-liga"
JSON_FILE = "listas_liga.json"


def load_urls_from_json(file_path: Path) -> List[str]:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('urls', [])


def call_scrap_endpoint(url: str) -> dict:
    endpoint_url = f"{API_BASE_URL}{ENDPOINT}"
    payload = {"url": url}
    
    try:
        response = requests.post(endpoint_url, json=payload)
        response.raise_for_status()
        return {
            "status": "success",
            "url": url,
            "response": response.json()
        }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "url": url,
            "error": str(e)
        }


def main():
    print(f"Loading URLs from {JSON_FILE}")
    urls = load_urls_from_json(JSON_FILE)
    
    if not urls:
        print("No URLs found in the JSON file.")
        return
    
    print(f"Found {len(urls)} URLs to process.\n")
    
    results = []
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Processing: {url}")
        result = call_scrap_endpoint(url)
        results.append(result)
        
        if result["status"] == "success":
            print(f"  ✓ Success: {result['response'].get('message', 'OK')}")
        else:
            print(f"  ✗ Error: {result['error']}")
        print()
    
    successful = sum(1 for r in results if r["status"] == "success")
    failed = len(results) - successful
    
    print("=" * 50)
    print(f"Summary: {successful} successful, {failed} failed")
    print("=" * 50)


if __name__ == "__main__":
    main()

