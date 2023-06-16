from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .models import UserPasskey

@login_required
def index(request,enroll=False):
    keys = UserPasskey.objects.filter(user=request.user)
    return render(request,'PassKeys.html',{"keys":keys,"enroll":enroll})


@login_required
@require_POST
def delKey(request):
    key=UserPasskey.objects.get(user=request.user, id=request.POST["id"])
    key.delete()
    return HttpResponse("Deleted Successfully")

@login_required
def toggleKey(request):
    id=request.GET["id"]
    q=UserPasskey.objects.filter(user=request.user, id=id)
    if q.count()==1:
        key=q[0]
        key.enabled=not key.enabled
        key.save()
        return HttpResponse("OK")
    return HttpResponse("Error")
