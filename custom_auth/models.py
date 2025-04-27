from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolio')
    ticker = models.CharField(max_length=10)  # e.g., "BTC" for Bitcoin
    name = models.CharField(max_length=100)   # e.g., "Bitcoin"
    quantity = models.FloatField()            # Amount of coins in the portfolio

    class Meta:
        verbose_name = 'Portfolio'
        verbose_name_plural = 'Portfolios'

    def __str__(self):
        return f"{self.user.username}'s {self.name} ({self.ticker})"