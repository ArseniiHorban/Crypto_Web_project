import json
from django.core.cache import cache
import requests

def fetch_with_cache(url, cache_key, cache_duration):
    """
    Fetches data from cache or makes an API request if the cache is stale.
    Args:
        url (str): The API URL to fetch data from.
        cache_key (str): The key to store/retrieve data in cache.
        cache_duration (int): Cache duration in seconds.
    Returns:
        dict: The fetched data.
    """
    cached_data = cache.get(cache_key)
    if cached_data:
        return json.loads(cached_data)

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    cache.set(cache_key, json.dumps(data), cache_duration)
    return data