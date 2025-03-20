from datetime import date
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from current_data_controller import CurrentDataController
from sentiment import SentimentAnalysis
from historical_data_controller import HistoricalDataController

@csrf_exempt
def get_sentiment(request, coin):
    sentiment_analysis = SentimentAnalysis()

    sentiment = sentiment_analysis.process_sentiment_call(coin)

    if sentiment:
        label, score = sentiment
        today = date.today().strftime("%Y-%m-%d")
        key = f"{coin.upper()}_{today}"
        return JsonResponse({key: {"label": label, "score": score}})
    else:
        return JsonResponse({"error": "Unable to fetch sentiment data"}, status=500)

@csrf_exempt
def get_current_data(request, coins):
    """
    Takes a string of coin symbols in a shape: 'BTC', 'ETH', 'UNI'
    """
    current_data = CurrentDataController()

    if coins:
        coins_list = coins.split(',')
    else:
        return JsonResponse({"error": "Invalid input parameters."}, status=500)

    data = current_data.process_current_data_call(coins_list)
    
    if data:
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse({"error": "Unable to fetch current data"}, status=500)
    
@csrf_exempt
def get_historical_data(request, coins, threshold=7):
    """
    Takes a string of coin symbols in a shape: 'BTC', 'ETH', 'UNI'
    """
    data_controller = HistoricalDataController()
    if coins and threshold:
        coins_list = coins.split(',')
    else:
        return JsonResponse({"error": "Invalid input parameters."}, status=500)
    try:
        data = data_controller.process_historical_data_call(coins_list, threshold)

        if data:
            return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({"error": "Unable to fetch historical data"}, status=500)

