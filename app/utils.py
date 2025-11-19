from datetime import datetime
from dotenv import load_dotenv
import os
import requests


def load_dotenv_safe():
    try:
        load_dotenv()
    except Exception:
        pass


def now_iso():
    return datetime.utcnow().isoformat() + "Z"


def fetch_google_search_results(query, api_key, search_engine_id):
    """
    Fetch search results from Google Custom Search API.

    Args:
        query (str): The search query.
        api_key (str): Google API key.
        search_engine_id (str): Google Custom Search Engine ID.

    Returns:
        list: A list of search result dictionaries with 'title' and 'url'.
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": api_key,
        "cx": search_engine_id,
        "num": 5,  # Limit to 5 results
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        print('Google Custom Search API response:', data)  # DEBUG LOG
        results = []
        for item in data.get("items", []):
            link = item.get("link")
            # Only include valid web URLs
            if isinstance(link, str) and link.strip().lower().startswith(('http://', 'https://')):
                results.append({
                    "title": item.get("title"),
                    "url": link,
                })
        if not results:
            print('No valid web URLs found in API response.')
        return results

    except Exception as e:
        print(f"Error fetching search results: {e}")
        return []
