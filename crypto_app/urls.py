"""
URL configuration for crypto_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views 
from django.shortcuts import redirect # for redirecting to/from login page
from django.contrib.auth.decorators import login_required # for login required decorator

from custom_auth.views import CustomLoginView, register, home
from external_apis.views import get_sentiment, get_current_data, get_historical_data

urlpatterns = [
    path('admin/', admin.site.urls), #Admin page
    path('auth/', include('social_django.urls', namespace='social')), #Oauth2 url
    path('login/', CustomLoginView.as_view(), name='login'),  #authentification page
    path('register/', register, name='register'),  # Registration page
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),  # logout
    path('dashboard/', lambda request: redirect('home'), name='dashboard'),  # Перенаправляем с /dashboard/ на /home/ (чтобы сохранить совместимость с текущим LOGIN_REDIRECT_URL)
    path('', lambda request: redirect('login'), name='home'),  # Перенаправляем неавторизованных на login
    path('home/', login_required(home), name='authenticated_home'),  # Защищённый (там декоратор login required) маршрут для home 

    path('sentiment/<str:coin>/', get_sentiment, name='get_sentiment'),
    path('current-data/<str:coins>/', get_current_data, name='get_current_data'),
    path('historical-data/<str:coins>/<int:threshold>/', get_historical_data, name='get_historical_data')
    
]

