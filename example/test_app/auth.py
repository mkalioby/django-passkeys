from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User

def loginView(request):
    context={}
    if request.method=="POST":
        user=authenticate(request, username=request.POST["username"],password=request.POST["password"])
        if user:
            login(request, user)
            return HttpResponseRedirect(reverse('home'))
        context["invalid"]=True
    return render(request, "login.html", context)

# def create_session(request,username):
#     user=User.objects.get(username=username)
#     user.backend='django.contrib.auth.backends.ModelBackend'
#     login(request, user)
#     return HttpResponseRedirect(reverse('home'))


def logoutView(request):
    logout(request)
    return  render(request,"logout.html",{})