from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


def login_view(request):
    context = {}
    if request.method == "POST":
        user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
        if user:
            login(request, user)
            return HttpResponseRedirect(reverse('home'))
        context["invalid"] = True
    return render(request, "login.html", context)


def logout_view(request):
    logout(request)
    return render(request, "logout.html", {})