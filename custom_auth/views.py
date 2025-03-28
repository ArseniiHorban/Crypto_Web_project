from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.conf import settings
from .forms import RegisterForm, CustomAuthenticationForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import User, Portfolio
import requests
import logging
import datetime
import numpy as np
from django.core.cache import cache

# Set up logging
logger = logging.getLogger(__name__)

# Function to verify reCAPTCHA response
def verify_recaptcha(request):
    recaptcha_response = request.POST.get('g-recaptcha-response')
    data = {
        'secret': settings.RECAPTCHA_PRIVATE_KEY,
        'response': recaptcha_response
    }
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    result = r.json()
    return result.get('success', False)

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'auth.html'

    def post(self, request, *args, **kwargs):
        if not verify_recaptcha(request):
            form = self.get_form()
            form.add_error(None, 'Please verify you are not a robot')
            return self.form_invalid(form)
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recaptcha_public_key'] = settings.RECAPTCHA_PUBLIC_KEY
        context['is_login'] = True
        return context

    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated and user.is_staff:
            logger.info('User is admin -> redirecting to admin panel')
            return reverse_lazy('admin_panel')
        logger.info('User is regular -> redirecting to home page')
        return reverse_lazy('authenticated_home')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if not verify_recaptcha(request):
            form.add_error(None, 'Please verify you are not a robot')
            return render(request, 'auth.html', {
                'form': form,
                'recaptcha_public_key': settings.RECAPTCHA_PUBLIC_KEY,
                'is_login': False
            })
        if form.is_valid():
            form.save()
            logger.info('User registered successfully')
            return redirect('login')
        return render(request, 'auth.html', {
            'form': form,
            'recaptcha_public_key': settings.RECAPTCHA_PUBLIC_KEY,
            'is_login': False
        })
    else:
        form = RegisterForm()
    return render(request, 'auth.html', {
        'form': form,
        'recaptcha_public_key': settings.RECAPTCHA_PUBLIC_KEY,
        'is_login': False
    })

@login_required
def home(request):
    top_coins = cache.get('top_coins', [])
    historical_data = cache.get('historical_data', {})
    bitcoin_chart_data = cache.get('bitcoin_chart_data', {1: {'labels': [], 'prices': []}, 7: {'labels': [], 'prices': []}, 365: {'labels': [], 'prices': []}})
    total_volume = cache.get('total_volume', 0)
    bitcoin_stats = cache.get('bitcoin_stats', {
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
    })

    top_coins_display = []
    for coin in top_coins[:10]:
        coin_id = coin['id']
        historical = historical_data.get(coin_id, {'dates': [], 'prices': []})
        top_coins_display.append({
            'id': coin_id,
            'name': coin['name'],
            'current_price': coin['current_price'],
            'total_volume': coin['total_volume'],
            'circulating_supply': coin['circulating_supply'],
            'market_cap': coin['market_cap'],
            'price_change_24h': coin['price_change_24h'],
            'chart_data': {
                'labels': historical['dates'][-30:],
                'prices': historical['prices'][-30:]
            }
        })

    trending_display = []
    for coin in top_coins[:6]:
        trending_display.append({
            'name': coin['name'],
            'symbol': coin['symbol'],
            'image': coin['image'],
            'price_change_24h': coin['price_change_24h']
        })

    days = int(request.GET.get('days', 7))
    chart_data = bitcoin_chart_data.get(days, {'labels': [], 'prices': []})

    return render(request, 'home.html', {
        'top_coins': top_coins_display,
        'total_volume': total_volume,
        'bitcoin_stats': bitcoin_stats,
        'trending_coins': trending_display,
        'bitcoin_chart_data': bitcoin_chart_data,
        'historical_data': historical_data,
    })

@login_required
def admin_panel(request):
    if not request.user.is_staff:
        logger.warning(f"User {request.user.username} attempted to access admin panel without permission")
        return HttpResponseForbidden("You are not authorized to access this page.")

    users = User.objects.all()

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        user = User.objects.get(id=user_id)
        
        if action == 'block':
            user.is_active = False
            user.save()
            logger.info(f"User {user.username} blocked by admin {request.user.username}")
        elif action == 'unblock':
            user.is_active = True
            user.save()
            logger.info(f"User {user.username} unblocked by admin {request.user.username}")
        elif action == 'delete':
            user.delete()
            logger.info(f"User {user.username} deleted by admin {request.user.username}")
        return redirect('admin_panel')

    return render(request, 'admin_panel.html', {'users': users})

@login_required
def portfolio(request):
    portfolio_items = Portfolio.objects.filter(user=request.user)
    top_coins = cache.get('top_coins', [])
    historical_data = cache.get('historical_data', {})

    # Prepare data for portfolio allocation chart
    tickers = [item.ticker.lower() for item in portfolio_items]
    quantities = [float(item.quantity) for item in portfolio_items]
    labels = []
    for item in portfolio_items:
        ticker = item.ticker.lower()
        coin = next((coin for coin in top_coins if coin['symbol'].lower() == ticker), None)
        if coin:
            name = item.name if item.name else coin['name']
            label = f"{name} ({coin['symbol']})"
        else:
            label = item.name if item.name else ticker.upper()
        labels.append(label)

    # Calculate current value of each coin (quantity * current price)
    allocations = []
    total_value = 0
    for ticker, quantity in zip(tickers, quantities):
        coin = next((coin for coin in top_coins if coin['symbol'].lower() == ticker), None)
        if coin:
            current_price = coin['current_price']
            value = quantity * current_price
            allocations.append(value)
            total_value += value
        else:
            allocations.append(0)

    # Convert values to percentages
    if total_value > 0:
        allocations = [(value / total_value) * 100 for value in allocations]
    else:
        allocations = [0] * len(tickers)

    # Calculate portfolio value over time (Portfolio Growth)
    portfolio_value = {}
    if historical_data and tickers:
        # Find dates from the first available coin's historical data
        dates = None
        for ticker in tickers:
            coin = next((coin for coin in top_coins if coin['symbol'].lower() == ticker), None)
            if coin and coin['id'] in historical_data and historical_data[coin['id']]['dates']:
                dates = historical_data[coin['id']]['dates']
                break

        if dates:
            for date in dates:
                total_value = 0
                for ticker, quantity in zip(tickers, quantities):
                    coin = next((coin for coin in top_coins if coin['symbol'].lower() == ticker), None)
                    if coin and coin['id'] in historical_data and date in historical_data[coin['id']]['dates']:
                        price = historical_data[coin['id']]['prices'][historical_data[coin['id']]['dates'].index(date)]
                        total_value += quantity * price
                if total_value > 0:
                    portfolio_value[date] = total_value

    # Convert portfolio_value to lists for Chart.js
    portfolio_dates = list(portfolio_value.keys())
    portfolio_values = list(portfolio_value.values())

    # Calculate performance metrics (Sharpe Ratio, Volatility, Max Drawdown)
    performance = {'sharpe_ratio': 0, 'annual_volatility': 0, 'max_drawdown': 0}
    if portfolio_value:
        returns = []
        values = list(portfolio_value.values())
        for i in range(1, len(values)):
            daily_return = (values[i] - values[i-1]) / values[i-1]
            returns.append(daily_return)
        
        if returns:
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            performance['sharpe_ratio'] = (mean_return / std_return) * np.sqrt(252) if std_return != 0 else 0
            performance['annual_volatility'] = std_return * np.sqrt(252) * 100
            peak = values[0]
            trough = values[0]
            max_drawdown = 0
            for value in values:
                if value > peak:
                    peak = value
                    trough = value
                elif value < trough:
                    trough = value
                drawdown = (peak - trough) / peak
                max_drawdown = max(max_drawdown, drawdown)
            performance['max_drawdown'] = -max_drawdown * 100

    # Calculate Annual Returns
    annual_returns = []
    if portfolio_value:
        years = sorted(set(date[:4] for date in portfolio_value.keys()))
        initial_balance = 10000
        for year in years:
            year_dates = [date for date in portfolio_value.keys() if date.startswith(year)]
            if not year_dates:
                continue
            year_values = [portfolio_value[date] for date in year_dates]
            start_value = year_values[0]
            end_value = year_values[-1]
            portfolio_return = ((end_value - start_value) / start_value) * 100 if start_value != 0 else 0
            portfolio_balance = initial_balance * (1 + portfolio_return / 100)

            annual_returns.append({
                'year': year,
                'portfolio_return': portfolio_return,
                'portfolio_balance': portfolio_balance,
            })
            initial_balance = portfolio_balance

    return render(request, 'portfolio.html', {
        'portfolio': portfolio_items,
        'performance': performance,
        'portfolio_value': portfolio_value,
        'portfolio_dates': portfolio_dates,
        'portfolio_values': portfolio_values,
        'annual_returns': annual_returns,
        'available_coins': top_coins,
        'labels': labels,
        'allocations': allocations,
    })

@login_required
def add_portfolio_item(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker')
        name = request.POST.get('name')
        quantity = request.POST.get('quantity')  # Теперь запрашиваем quantity вместо allocation

        top_coins = cache.get('top_coins', [])
        if not any(coin['symbol'] == ticker.upper() for coin in top_coins):
            logger.warning(f"User {request.user.username} tried to add unavailable coin: {ticker}")
            return render(request, 'portfolio.html', {
                'portfolio': Portfolio.objects.filter(user=request.user),
                'error': 'Selected currency is not available.'
            })

        Portfolio.objects.create(
            user=request.user,
            ticker=ticker,
            name=name,
            quantity=float(quantity)
        )
        logger.info(f"User {request.user.username} added portfolio item: {ticker} with quantity {quantity}")
    return redirect('portfolio')

@login_required
def delete_portfolio_item(request, item_id):
    item = Portfolio.objects.get(id=item_id, user=request.user)
    item.delete()
    logger.info(f"User {request.user.username} deleted portfolio item: {item.ticker}")
    return redirect('portfolio')