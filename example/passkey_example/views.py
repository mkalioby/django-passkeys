from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render

from passkey_example.forms import MyAuthenticationForm


class MyLoginView(LoginView):
    form_class = MyAuthenticationForm
    template_name = 'login.html'


class MyLogoutView(LogoutView):
    template_name = 'logout.html'


@login_required()
def home(request):  # pragma: no cover
    return render(request, "home.html", {})
