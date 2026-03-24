from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login,logout

from passkeys.helpers import is_login_page, get_redirection_url

def loginView(request):
    context={}
    if request.method=="POST":
        user=authenticate(request, username=request.POST["username"],password=request.POST["password"])
        if user:
            login(request, user)
            if not is_login_page(request):
                return get_redirection_url(request)
            return redirect('home')
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