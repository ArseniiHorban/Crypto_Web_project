from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.conf import settings
import requests

def login_view(request):
    return render(request, 'custom_auth/login.html')

@login_required
def dashboard(request):
    return render(request, 'custom_auth/dashboard.html', {'user': request.user})



def login_view(request):
    if request.method == 'POST':
        recaptcha_response = request.POST.get('g-recaptcha-response')
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY, #ссылается на переменную из settings.py файла
            'response': recaptcha_response
        }
        r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = r.json()
        if result['success']:
            return HttpResponseRedirect('/auth/login/google-oauth2/')
    return render(request, 'custom_auth/login.html', {'RECAPTCHA_PUBLIC_KEY': settings.RECAPTCHA_PUBLIC_KEY}) #и это тоде ссылка