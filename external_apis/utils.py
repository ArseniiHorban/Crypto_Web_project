import json
import os
import requests
from datetime import datetime

class Utils:

    @staticmethod
    def get_coin_id_from_symbol(coin_symbol):

        coin_map = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "LTC": "litecoin",
        "XRP": "ripple",
        "DOGE": "dogecoin",
        "BCH": "bitcoin-cash",
        "ADA": "cardano",
        "SOL": "solana",
        "DOT": "polkadot",
        "BNB": "binancecoin",
        "MATIC": "matic-network",
        "LINK": "chainlink",
        "UNI": "uniswap",
        "AVAX": "avalanche-2",
        "TRX": "tron",
        "ETHW": "ethereum-poW",
        "SHIB": "shiba-inu",
        "DOGE": "dogecoin",
        "ICP": "internet-computer", 
        "VET": "vechain",
        "XTZ": "tezos",
        "FIL": "filecoin",
        "AAVE": "aave",
        "EGLD": "elrond-erd-2",
        "LUNA": "terra-luna",
        "FTM": "fantom",
        "KSM": "kusama",
        "RUNE": "thorchain",
        "LDO": "lido-dao",
        "HNT": "helium",
        "MKR": "maker",
        "SUSHI": "sushi",
        "CRO": "crypto-com-chain", 
        }

        if coin_symbol.upper() not in coin_map:
            raise ValueError(f"Invalid coin symbol: {coin_symbol}")

        return coin_map[coin_symbol.upper()]


    @staticmethod
    def convert_date(timestamp):
        readable_date = datetime.fromtimestamp(timestamp / 1000)  # Convert ms to seconds
        return readable_date.strftime('%Y-%m-%d')
    
    @staticmethod
    def load_cache(filename, folder="."):

        if not os.path.exists(folder):
            raise FileNotFoundError(f"Folder does not exist.")
        
        # Construct the full path
        filepath = os.path.join(folder, filename)

        if not os.path.exists(filepath):
            print(f"File '{filename}' does not exist. Creating a new file.")
            with open(filepath, 'w') as file:
                file.write('')  # Creates an empty file if no default data is provided

        try:
            with open(filepath, 'r') as file:
                content = file.read().strip()
                if not content:
                    # print("The file is empty.")
                    return None
                else:
                    print("Cache loaded")
                    return json.loads(content)
        
        except FileNotFoundError:
            raise FileNotFoundError(f"File does not exist.")
        except json.JSONDecodeError:
            raise json.JSONDecodeError(f"The file is not valid JSON.")
        
    @staticmethod
    def format_large_number(number):
        if number >= 1e9:
            return f"${number / 1e9:.2f}B"
        elif number >= 1e6:
            return f"${number / 1e6:.2f}M"
        else:
            return f"${number:.2f}"
        
    @staticmethod
    def is_valid_coin(coin_symbol):
        valid_coins = {
            'BTC', 'ETH', 'XRP', 'ADA', 'DOGE', 'SOL', 'DOT', 'BNB', 'LTC', 'MATIC',
            'AVAX', 'TRX', 'LINK', 'XLM', 'NEAR', 'ATOM', 'ALGO', 'VET', 'FTM',
            'ICP', 'HBAR', 'FIL', 'GRT', 'XTZ', 'EGLD', 'SAND', 'MANA', 'AXS', 'ENJ',
            'CHZ', 'ZIL', 'KSM', 'BCH', 'ETC', 'EOS', 'ZEC', 'XMR', 'DASH', 'QTUM',
            'UNI'
        }
        
        return coin_symbol in valid_coins