#этот файл это форма для регистрации пользователя, которая наследуется от UserCreationForm
#чтобы использовать встроенные методы валидации формы Django
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User  #Custom user model from models.py


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True) # making email field required

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2'] # fields to be displayed in the form 
                                                                 # password1 and password2 are for password and password confirmation


class CustomAuthenticationForm(AuthenticationForm):
    pass  # Оставляем пустой 
