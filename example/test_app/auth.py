from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login,logout

def loginView(request):
    context={}
    if request.method=="POST":
        user=authenticate(request, username=request.POST["username"],password=request.POST["password"])
        if user:
            login(request, user)
            if request.POST.get("next",""):
                return redirect(request.POST["next"])
            return redirect('home') # pragma: no cover
        context["invalid"]=True
    return render(request, "login.html", context)

# def create_session(request,username):
#     user=User.objects.get(username=username)
#     user.backend='django.contrib.auth.backends.ModelBackend'
#     login(request, user)
#     return HttpResponseRedirect(reverse('home'))


def logoutView(request):
    logout(request) # pragma: no cover
    return  render(request,"logout.html",{}) # pragma: no cover