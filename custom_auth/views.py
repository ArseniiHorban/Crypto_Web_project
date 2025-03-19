
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.conf import settings
from .forms import RegisterForm, CustomAuthenticationForm
from django.contrib.auth.decorators import login_required
import requests

#function to verify captcha
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
    return render(request, 'home.html')