from django.contrib import admin
from .models import User

admin.site.register(User)  # Регистрируем модель User в админке
# Register your models here.
