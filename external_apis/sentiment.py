import json
import requests
from datetime import datetime, timedelta
from utils import Utils
from huggingface_hub import InferenceClient
from transformers import AutoTokenizer
from together import Together

class SentimentAnalysis:
    def __init__(self):
        self.utils = Utils()

    
    def get_latest_sentiment(self, sentiment_data, coin):

        if not sentiment_data:
            return None
        
        coin_entries = {}

        for key, data in sentiment_data.items():
            if key.startswith(coin):
                coin_entries[key] = data

        if not coin_entries:
            print(f"No cache found for {coin}.")
            return None

        latest_date = None

        for entry in coin_entries:
            date_string = key.split('_')[1]
            current_date = datetime.strptime(date_string, "%Y-%m-%d")

            if latest_date is None or current_date > latest_date:
                latest_key = key
                latest_date = current_date
        
        if latest_key:
            return {latest_key: coin_entries[latest_key]}
        else:
            return None
    

    def sentiment_cache_outdated(self, sentiment_data, coin, threshold=7):

        if sentiment_data:
            print(f"Sentiment data: {sentiment_data}")
            sentiment = self.get_latest_sentiment(sentiment_data, coin)
            if sentiment:
                key, data = next(iter(sentiment.items()))
            else:
                print("No sentiment cache found")
                return True

        else:
            print("Cache outdated")
            return True
        
        if key and data:
            key = key.strip()
            date = key.split("_")[1]
            date = datetime.strptime(date, "%Y-%m-%d")

            current_date = datetime.now()

            if current_date - date > datetime.timedelta(days=threshold):
                print("Cache outdated")
                return True
        
        print("Cache is still valid")
        return False


    def fetch_latest_news(self, coin, n):

        api_key = 'ed8f80b85fcd4bfe9a3e16973bb088b3'
        url = 'https://newsapi.org/v2/everything'

        try:
            coin_id = self.utils.get_coin_id_from_symbol(coin)
        except ValueError as e:
            print(f"Error getting coin ID. {e}")
            return None

        params = {
            'q': f"{coin} {coin_id} price analysis performance",
            'apiKey': api_key,
            'pageSize': n,
            'language': 'en',
            'sortBy': 'publishedAt',
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            news_data = response.json()
            if news_data['articles']:
                return news_data['articles'] # Return articles only
        else: 
            print(f"Error fetching data: {response.status_code}")
            return None


    def accumulate_news_data(self, articles, max_tokens=100):
        if not articles:
            return None

        tokenizer = AutoTokenizer.from_pretrained('yiyanghkust/finbert-tone')

        accumulated_text = ""
        total_tokens = 0

        for article in articles:
            if 'description' in article and article['description']:
                description = article['description']
            else:
                description = ""
        
            if description:
                tokens = tokenizer.tokenize(description)
                token_count = len(tokens)

                if token_count + total_tokens < max_tokens:
                    accumulated_text += description + " "
                    total_tokens += token_count
                else:
                    return accumulated_text.strip()
                
        return accumulated_text.strip()         

    def analyze_sentiment(self, text):
        # api_token = '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'
        # sentiment_model_url = 'https://yiyanghkust/finbert-tone'

        client = InferenceClient(
        provider="hf-inference",
        api_key="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"
        )

        try:
            result = client.text_classification(
            model="yiyanghkust/finbert-tone",
            text=text
            )

            # print(type(result))
            # print(type(result[0]))
            # print(dir(result[0]))

            # print(result)

            highest_label = None
            highest_score = -float('inf')

            for element in result:
                if element.score > highest_score:
                    highest_score = element.score
                    highest_label = element.label

            return highest_label, highest_score

        except Exception as e:
            print(f"Error during sentiment analysis: {e}")
            return None

    def process_sentiment_call(self, coin):
        if not self.utils.is_valid_coin(coin):
            raise ValueError("Invalid coin symbol.")

        try:
            sentiment_data = self.utils.load_cache("sentiment_cache.json")
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            return None

        if self.sentiment_cache_outdated(sentiment_data, coin):
            articles = self.fetch_latest_news(coin, 5)
            text =  self.accumulate_news_data(articles=articles, max_tokens=400)
            text = self.summarize(coin, text)
            print(text)
            if text.strip() == 'Error':
                raise ValueError(f"Error with processing {coin} data.")
            
            if text:
                sentiment = self.analyze_sentiment(text)
                if sentiment:
                    score, label = sentiment
                    # print(sentiment)
                    self.save_sentiment_cache(coin, label, score)
                    return sentiment
                else:
                    print("Error analyzing sentiment")
                    return None
            else:
                print("No sentiment to analyze")
                return None
        else:
            return self.get_latest_sentiment(sentiment_data, coin)


    def save_sentiment_cache(self, coin, score, label, filename="sentiment_cache.json"):
        date = datetime.today().strftime('%Y-%m-%d')

        sentiment_data = {
            f"{coin}_{date}": {
                "label": label,
                "score" : score
            }
        }

        existing_data ={}
        try:
            existing_data = self.utils.load_cache("sentiment_cache.json")
        except FileNotFoundError as e:
            print("Cache file not found")
        except json.JSONDecodeError as e:
            print("Error saving sentiment cache.")

            
        if existing_data:
            existing_data.update(sentiment_data)
            try:
                with open(filename, "w") as f:
                    json.dump(existing_data, f, indent=4)
                    print("Sentiment cache saved successfully")
            except IOError as e:
                print("Error saving sentiment cache.")
            except Exception as e:
                print("Unexpected error saving sentiment cache.")
        else:
            try:
                with open(filename, "w") as f:
                    json.dump(sentiment_data, f, indent=4)
                    print("Sentiment cache saved successfully")
            except IOError as e:
                print("Error saving sentiment cache.")
            except Exception as e:
                print("Unexpected error saving sentiment cache.")

    def summarize(self, coin, text):
        client = Together()

        completion = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        messages=[{"role": "user", "content": f"Please summarize the following text about {coin} in a concise manner, focusing only on {coin} data and excluding data about other coins. Include current price data, exclude past price data; if no current data mentioned, just try to catch overall situation of a {coin}.Try to keep it at around one sentence long. If no text about {coin} is provided, return a single word 'Error'. Please consider that your summarized text will be passed to finBERT directly with no transformation, so really try to make a short and concise summary, only return a summary:\n\n{text}"}],
        )

        return completion.choices[0].message.content

