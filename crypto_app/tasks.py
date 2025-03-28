import threading
import requests
import datetime
from dateutil.relativedelta import relativedelta
from django.core.cache import cache
import logging
import time

# Set up logging
logger = logging.getLogger(__name__)

# Глобальная переменная для проверки, запущен ли поток
_task_thread_started = False

# Function to fetch data with retries on rate limit (429) errors
def fetch_with_retry(url, params=None, retries=5, delay=120, api_name="API"):
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 429:
                logger.error(f"{api_name} rate limit exceeded, retrying in {delay} seconds... (Attempt {attempt + 1}/{retries})")
                time.sleep(delay)
                continue
            if response.status_code != 200:
                logger.error(f"Failed to fetch data from {api_name}: {url}, Status: {response.status_code}, Response: {response.text}")
                return None
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request to {api_name} failed: {url}, Error: {str(e)}")
            time.sleep(delay)
            continue
    logger.error(f"Failed to fetch data from {api_name} after {retries} retries: {url}")
    return None

# Mapping of CoinGecko coin IDs to Binance trading pairs
BINANCE_PAIRS = {
    'bitcoin': 'BTCUSDT',
    'ethereum': 'ETHUSDT',
    'binancecoin': 'BNBUSDT',
    'solana': 'SOLUSDT',
    'ripple': 'XRPUSDT',
    'cardano': 'ADAUSDT',
    'dogecoin': 'DOGEUSDT',
    'tron': 'TRXUSDT',
    'avalanche-2': 'AVAXUSDT',
}

def fetch_trending_coins():
    logger.info("Starting fetch_trending_coins")
    try:
        # Fetch total market volume (from CoinGecko)
        total_volume = cache.get('total_volume')
        if total_volume is None or total_volume == 0:
            response = fetch_with_retry('https://api.coingecko.com/api/v3/global', api_name="CoinGecko")
            if response and response.status_code == 200:
                total_volume = response.json()['data']['total_volume']['usd']
                cache.set('total_volume', total_volume, 15 * 60)
                logger.info(f"Successfully cached total volume: {total_volume}")
            else:
                logger.error("Failed to fetch total market volume")
                total_volume = 0
                cache.set('total_volume', total_volume, 15 * 60)

        # Fetch top coins by market cap (from CoinGecko)
        top_coins = cache.get('top_coins')
        if top_coins is None or not top_coins:
            logger.info("Fetching top coins by market cap")
            top_coins_url = (
                'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd'
                '&order=market_cap_desc&per_page=10&page=1'
                '&sparkline=false&price_change_percentage=1h%2C24h%2C7d%2C14d%2C30d%2C200d%2C1y'
            )
            response = fetch_with_retry(top_coins_url, api_name="CoinGecko")
            if not response or response.status_code != 200:
                logger.error(f"Failed to fetch top coins: {response.status_code if response else 'No response'}")
                top_coins = []
                cache.set('top_coins', top_coins, 15 * 60)
                return
            top_coins_data = response.json()

            top_coins = []
            for coin in top_coins_data:
                top_coins.append({
                    'id': coin['id'],
                    'name': coin['name'],
                    'symbol': coin['symbol'].upper(),
                    'current_price': coin['current_price'],
                    'total_volume': coin['total_volume'],
                    'circulating_supply': coin['circulating_supply'],
                    'market_cap': coin['market_cap'],
                    'price_change_24h': coin['price_change_percentage_24h'],
                    'price_change_7d': coin['price_change_percentage_7d_in_currency'],
                    'price_change_30d': coin['price_change_percentage_30d_in_currency'],
                    'price_change_1y': coin['price_change_percentage_1y_in_currency'],
                    'ath': coin['ath'],
                    'ath_date': coin['ath_date'],
                    'atl': coin['atl'],
                    'atl_date': coin['atl_date'],
                    'image': coin['image'],
                })
            cache.set('top_coins', top_coins, 15 * 60)
            logger.info(f"Successfully cached top coins: {len(top_coins)} coins")
        else:
            logger.info("Top coins already in cache, but will refresh anyway")

        # Fetch Bitcoin stats (from CoinGecko)
        bitcoin_stats = cache.get('bitcoin_stats')
        if bitcoin_stats is None or all(value == 0 for value in bitcoin_stats.values() if isinstance(value, (int, float))):
            for coin in top_coins:
                if coin['id'] == 'bitcoin':
                    bitcoin_stats = {
                        'price_change_24h': coin['price_change_24h'],
                        'price_change_7d': coin['price_change_7d'],
                        'price_change_30d': coin['price_change_30d'],
                        'price_change_1y': coin['price_change_1y'],
                        'market_cap': coin['market_cap'],
                        'total_volume': coin['total_volume'],
                        'ath': coin['ath'],
                        'ath_date': datetime.datetime.strptime(coin['ath_date'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d"),
                        'atl': coin['atl'],
                        'atl_date': datetime.datetime.strptime(coin['ath_date'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d"),
                    }
                    cache.set('bitcoin_stats', bitcoin_stats, 15 * 60)
                    logger.info("Successfully cached Bitcoin stats")
                    break
            if not bitcoin_stats:
                bitcoin_stats = {
                    'price_change_24h': 0,
                    'price_change_7d': 0,
                    'price_change_30d': 0,
                    'price_change_1y': 0,
                    'market_cap': 0,
                    'total_volume': 0,
                    'ath': 0,
                    'ath_date': 'N/A',
                    'atl': 0,
                    'atl_date': 'N/A',
                }
                cache.set('bitcoin_stats', bitcoin_stats, 15 * 60)
                logger.warning("Bitcoin stats not found, using fallback")

        # Fetch historical data for each coin (from Binance)
        historical_data = cache.get('historical_data')
        if historical_data is None or not historical_data:
            historical_data = {}
            for coin in top_coins:
                coin_id = coin['id']
                cache_key = f'historical_{coin_id}_365'
                cached_historical = cache.get(cache_key)
                if cached_historical and cached_historical['dates']:
                    historical_data[coin_id] = cached_historical
                    continue

                # Skip Tether (USDT) and USD Coin (USDC) as they don't have meaningful trading pairs
                if coin_id in ['tether', 'usd-coin']:
                    logger.info(f"Skipping historical data for {coin_id} (stablecoin), using static data")
                    end_date = datetime.datetime.now()
                    start_date = end_date - datetime.timedelta(days=365)
                    dates = [(start_date + datetime.timedelta(days=x)).strftime('%Y-%m-%d') for x in range(365)]
                    prices = [1.0] * 365  # Stablecoin price is ~1 USD
                    historical = {
                        'dates': dates,
                        'prices': prices
                    }
                    cache.set(cache_key, historical, 15 * 60)
                    historical_data[coin_id] = historical
                    continue

                # Map CoinGecko coin ID to Binance trading pair
                symbol = BINANCE_PAIRS.get(coin_id)
                if not symbol:
                    logger.warning(f"No Binance trading pair found for {coin_id}, skipping historical data")
                    historical_data[coin_id] = {'dates': [], 'prices': []}
                    continue
                # Calculate timestamps for the last 365 days
                end_time = int(time.time() * 1000)  # Current time in milliseconds
                start_time = end_time - (365 * 24 * 60 * 60 * 1000)  # 365 days ago in milliseconds

                # Fetch historical data from Binance
                binance_url = 'https://api.binance.com/api/v3/klines'
                params = {
                    'symbol': symbol,
                    'interval': '1d',  # Daily interval
                    'startTime': start_time,
                    'endTime': end_time,
                    'limit': 365  # Maximum 1000, but we need 365 days
                }
                response = fetch_with_retry(binance_url, params=params, api_name="Binance", delay=60)
                if not response or response.status_code != 200:
                    logger.error(f"Failed to fetch historical data for {coin_id} from Binance: {response.status_code if response else 'No response'}")
                    historical_data[coin_id] = {'dates': [], 'prices': []}
                    continue

                binance_data = response.json()
                historical = {
                    'dates': [],
                    'prices': []
                }
                for entry in binance_data:
                    # Binance returns: [open_time, open, high, low, close, volume, ...]
                    timestamp = entry[0]  # Open time in milliseconds
                    close_price = float(entry[4])  # Close price
                    date = datetime.datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
                    historical['dates'].append(date)
                    historical['prices'].append(close_price)

                cache.set(cache_key, historical, 15 * 60)
                historical_data[coin_id] = historical
                logger.info(f"Successfully fetched historical data for {coin_id} from Binance")
                time.sleep(1)  # Small delay to avoid hitting Binance rate limits

            cache.set('historical_data', historical_data, 15 * 60)
            logger.info(f"Successfully cached historical data for {len(historical_data)} coins")

        # Fetch Bitcoin chart data for 1, 7, and 365 days (from Binance instead of CoinGecko)
        days = [1, 7, 365]
        bitcoin_chart_data = cache.get('bitcoin_chart_data')
        if bitcoin_chart_data is None or not all(bitcoin_chart_data.get(day, {}).get('prices') for day in days):
            bitcoin_chart_data = {}
            for day in days:
                cache_key = f'bitcoin_chart_{day}'
                cached_chart_data = cache.get(cache_key)
                if cached_chart_data and cached_chart_data['prices']:
                    bitcoin_chart_data[day] = cached_chart_data
                    continue

                # Calculate timestamps for the requested period
                end_time = int(time.time() * 1000)  # Current time in milliseconds
                start_time = end_time - (day * 24 * 60 * 60 * 1000)  # 'day' days ago in milliseconds

                # Use appropriate interval based on the time period
                interval = '1h' if day <= 7 else '1d'  # Hourly for 1 and 7 days, daily for 365 days
                limit = day * 24 if interval == '1h' else day  # Number of data points (24 hours per day for hourly)

                # Fetch Bitcoin chart data from Binance
                binance_url = 'https://api.binance.com/api/v3/klines'
                params = {
                    'symbol': 'BTCUSDT',
                    'interval': interval,
                    'startTime': start_time,
                    'endTime': end_time,
                    'limit': min(limit, 1000)  # Binance has a limit of 1000 data points per request
                }
                response = fetch_with_retry(binance_url, params=params, api_name="Binance", delay=60)
                if not response or response.status_code != 200:
                    logger.error(f"Failed to fetch Bitcoin chart data for {day} days from Binance: {response.status_code if response else 'No response'}")
                    bitcoin_chart_data[day] = {'labels': [], 'prices': []}
                    continue

                binance_data = response.json()
                chart_data = {
                    'labels': [],
                    'prices': []
                }
                for entry in binance_data:
                    timestamp = entry[0]  # Open time in milliseconds
                    close_price = float(entry[4])  # Close price
                    date = datetime.datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d %H:%M' if interval == '1h' else '%Y-%m-%d')
                    chart_data['labels'].append(date)
                    chart_data['prices'].append(close_price)

                cache.set(cache_key, chart_data, 15 * 60)
                bitcoin_chart_data[day] = chart_data
                logger.info(f"Successfully fetched Bitcoin chart data for {day} days from Binance")
                time.sleep(1)  # Small delay to avoid hitting Binance rate limits

            cache.set('bitcoin_chart_data', bitcoin_chart_data, 15 * 60)
            logger.info("Successfully cached Bitcoin chart data")

    except Exception as e:
        logger.error(f"Error in fetch_trending_coins: {str(e)}")

def schedule_task():
    # Run the task every 15 minutes
    while True:
        logger.info("Scheduling fetch_trending_coins")
        # Clear cache to force refresh
        cache.delete('total_volume')
        cache.delete('top_coins')
        cache.delete('bitcoin_stats')
        cache.delete('historical_data')
        cache.delete('bitcoin_chart_data')
        for coin in cache.get('top_coins', []):
            cache.delete(f'historical_{coin["id"]}_365')
        for day in [1, 7, 365]:
            cache.delete(f'bitcoin_chart_{day}')
        fetch_trending_coins()
        logger.info("Sleeping for 15 minutes...")
        threading.Event().wait(900)

# Запускаем поток только один раз
def start_background_task():
    global _task_thread_started
    if not _task_thread_started:
        logger.info("Starting timer for fetch_trending_coins")
        thread = threading.Thread(target=schedule_task, daemon=True)
        thread.start()
        _task_thread_started = True