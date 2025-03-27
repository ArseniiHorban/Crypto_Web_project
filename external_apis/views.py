from datetime import date
import json
from django.http import JsonResponse
from current_data_controller import CurrentDataController
from sentiment import SentimentAnalysis
from historical_data_controller import HistoricalDataController
from portfolio import Portfolio


def get_sentiment(request, coin):
    sentiment_analysis = SentimentAnalysis()
    try:
        sentiment = sentiment_analysis.process_sentiment_call(coin)
    except ValueError as e:
        return JsonResponse({"error": "Invalid coin symbol."}, status=500)

    if sentiment:
        label, score = sentiment
        today = date.today().strftime("%Y-%m-%d")
        key = f"{coin.upper()}_{today}"
        return JsonResponse({key: {"label": label, "score": score}})
    else:
        return JsonResponse({"error": "Unable to fetch sentiment data"}, status=500)


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
    


def get_portfolio_analysis(request, assets, weights, initial_investment=10000):
    """
    Takes assets, weights, and initial investment as parameters and returns portfolio analysis.
    Assets must be in shape assets=BTC,ETH,UNI
    Weights must be in shape weights=60,30,10
    Initial investment must be in shape initial_investment=10000
    """
    assets_list = assets.split(',')
    weights_list = weights.split(',')
    weights_list = [int(w) for w in weights_list]

    # Ensure weights sum up to 100
    total_weight = sum(weights_list)
    if total_weight != 100:
        return JsonResponse({"error": "Weights must sum to 100."}, status=400)
    
    # Prepare assets_with_weights dictionary
    assets_with_weights = {}
    for i in range(len(assets_list)):
        assets_with_weights[assets_list[i]] = weights_list[i]


    # Create portfolio instance and analyze
    portfolio = Portfolio(assets_with_weights, initial_investment)
    try:
        analysis = portfolio.analyze()
        return JsonResponse(analysis, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
