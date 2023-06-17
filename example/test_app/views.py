from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required()
def home(request): # pragma: no cover
    print(request.session['passkey'])
    return render(request,"home.html",{})

@login_required()
def registered(request): # pragma: no cover
    return render(request,"home.html",{"registered":True})
