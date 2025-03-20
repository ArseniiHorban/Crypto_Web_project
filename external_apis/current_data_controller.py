import json
import requests
import datetime
from utils import Utils

class CurrentDataController:
    def __init__(self):
        self.utils = Utils

    def fetch_current_data(coins):
        """
        Coins must be an array of strings representing coin symbol. E.g. BTC, ETH etc. Shape must be ["ETH", "BTC"]
        """
        data = {}

        coins_string = ""
        for i, coin in enumerate(coins):
            coin = coin.strip()
            coin += "-USD"

            if i == len(coins) - 1:
                coins_string += coin
            else:
                coins_string += coin + ","
            
        print(coins_string)
        instruments = coins_string.strip()

        response = requests.get('https://data-api.coindesk.com/index/cc/v1/latest/tick',
            params={"market":"cadli","instruments":f"{instruments}","apply_mapping":"true","api_key":"98226db4d42acd057a29115cbd705a22a9594c12b42531a071c13297301ef4dd"},
            headers={"Content-type":"application/json; charset=UTF-8"}
        )

        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print("Error fetching current coin data.")
            print(response.status_code)
            return None

        
    def extract_field(data, field_key, target_field):
        """
        Extract a specific field (e.g., 'CURRENT_HOUR_VOLUME') from a nested JSON structure
        for a given field_key (e.g., 'BTC-USD').
        """
        # Check if the field_key exists in the data
        if field_key in data['Data']:
            # Extract the target_field from the nested dictionary
            return data['Data'][field_key].get(target_field, None)
        return None

    def transform_current_data(self, data, coins):
        transformed_data = {"cryptos": []}

        for coin in coins:
            coin_key = coin + "-USD"
            try:
                name = self.utils.get_coin_id_from_symbol(coin)
            except ValueError as e:
                print("Cannot transform data for invalid coin.")
                continue

            price = self.utils.extract_field(data, coin_key, "VALUE")
            directVol = self.utils.extract_field(data, coin_key, 'CURRENT_HOUR_VOLUME_DIRECT')
            totalVol = self.utils.extract_field(data, coin_key, "CURRENT_HOUR_QUOTE_VOLUME")
            topTierVol = self.utils.extract_field(data, coin_key, "CURRENT_HOUR_QUOTE_VOLUME_TOP_TIER")

            transformed_data["cryptos"].append({
                "name": name,
                "price": self.utils.format_large_number(price),
                "directVol": self.utils.format_large_number(directVol),
                "totalVol": self.utils.format_large_number(totalVol),
                "topTierVol": self.utils.format_large_number(topTierVol)
            })

        return transformed_data

    def process_current_data_call(self, coins):
        data = self.fetch_current_data(coins)
        transformed_data = self.transform_current_data(data, coins)
        return transformed_data
    