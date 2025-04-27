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
from custom_auth.views import CustomLoginView, register, home, admin_panel, portfolio, add_portfolio_item, delete_portfolio_item
from django.contrib.auth.views import LogoutView
from crypto_app.tasks import start_background_task

# Start the background task for fetching coin data
start_background_task()

# This is the main URL configuration for the project.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', CustomLoginView.as_view(), name='login'),  # root URL
    path('login/', CustomLoginView.as_view(), name='login'), # login URL
    path('register/', register, name='register'), # registration URL
    path('logout/', LogoutView.as_view(), name='logout'),# logout URL
    path('home/', home, name='authenticated_home'), # authenticated home URL
    path('admin-panel/', admin_panel, name='admin_panel'),# admin panel URL
    path('portfolio/', portfolio, name='portfolio'), # portfolio URL
    path('portfolio/add/', add_portfolio_item, name='add_portfolio_item'), # add portfolio item URL
    path('portfolio/delete/<int:item_id>/', delete_portfolio_item, name='delete_portfolio_item'), # delete portfolio item URL
    path('auth/', include('social_django.urls', namespace='social')) # OAuth2 URLs 
]