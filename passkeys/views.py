from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from .models import UserPasskey

@login_required
def index(request,enroll=False): # noqa
    keys = UserPasskey.objects.filter(user=request.user) # pragma: no cover
    return render(request,'passkeys/manage.html',{"keys":keys,"enroll":enroll}) # pragma: no cover


@login_required
def delKey(request):
    keys=UserPasskey.objects.filter(id=request.POST["id"], user=request.user)
    if keys.count()==1:
        key = keys[0]
        key.delete()
        return HttpResponse("Deleted Successfully")
    return HttpResponse("Error: You don't own this token so you can't delete it", status=403)

@login_required
def toggleKey(request):
    keys=UserPasskey.objects.filter(user=request.user, id=request.POST["id"])
    if keys.count()==1:
        key = keys[0]
        key.enabled=not key.enabled
        key.save()
        return HttpResponse("OK")
    return HttpResponse("Error: You don't own this token so you can't toggle it", status=403)
