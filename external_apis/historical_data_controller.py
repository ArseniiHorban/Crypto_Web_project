import json
import os
import requests
from datetime import datetime
from utils import Utils

class HistoricalDataController:
    def __init__(self):
        self.utils = Utils()

    
    def transform_historical_data_json(self, data):
        converted_data = {"data": []}

        for entry in data["prices"]:
            timestamp = entry[0]
            price = entry[1]
            price= self.utils.format_large_number(price)
            date = self.utils.convert_date(timestamp)
            converted_data["data"].append({"date": date, "price": price})

        return converted_data
    

    def fetch_historical_data(self, coin):

        try:
            coin_id = self.utils.get_coin_id_from_symbol(coin)
            # print(coin_id)
        except ValueError as e:
            print(e)
            return None
        
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?x_cg_api_key=CG-UDyebs4JZzozMgnKC33tQUrq"
        # print(url)

        headers = {"accept": "application/json"}
        params = {
            "vs_currency":"usd", "days":"365", "interval":"daily"
        }

        response = requests.get(url, headers=headers,params=params)
        # print(response.text)

        if response.status_code == 200:
            print("Historical data fetched successfully")
            return response.json()
        else:
            print(f"Error fetching data: {response.status_code}")
            return None


    def save_historical_data_cash(self, coin_symbol, data):
        
        filename = f"{coin_symbol}"
    
        file_path = os.path.join("historical_data_cache", filename)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
            print(f"Historical cache updated for {coin_symbol}.")

        
    def historical_cash_outdated(self, data, coin_symbol, threshold):
        """
        Coin as symbol, e.g. BTC, ETH etc.
        Threshold in days
        """

        if data:
            today = datetime.now()

            latest_date_str = data['data'][-1]['date']  
            latest_date = datetime.strptime(latest_date_str, '%Y-%m-%d')  # Convert to datetime object
            
            delta_days = (today - latest_date).days

            if delta_days > threshold:
                return True
            else:
                print(f"The cache for {coin_symbol} is up to date. Last data was {delta_days} days ago.")
                return False  # Cache is up to date
        else:
            return True


    def process_historical_data_call(self, coins, threshold=7):
        result = {}

        for coin_symbol in coins:
            if not self.utils.is_valid_coin(coin_symbol):
                print(f"Invalid coin symbol {coin_symbol}.")
                result[coin_symbol] = None
                continue

            try:
                data = self.utils.load_cache(f"{coin_symbol}", "historical_data_cache")
            except Exception as e:
                print(f"Failed to load cache for {coin_symbol}")
                result[coin_symbol] = None
                continue

            if self.historical_cash_outdated(data, coin_symbol, threshold):
                
                try:
                    new_data = self.fetch_historical_data(coin_symbol)

                    if not new_data:
                        print("Failed to fetch new data.")
                        result[coin_symbol] = None
                        continue
                except Exception as e:
                    print(f"Error fetching new data: {e}")
                    result[coin_symbol] = None
                    continue
                
                new_data = self.transform_historical_data_json(new_data)
                self.save_historical_data_cash(coin_symbol, new_data)
                result[coin_symbol] = new_data
            else:
                result[coin_symbol] = data

        return result

