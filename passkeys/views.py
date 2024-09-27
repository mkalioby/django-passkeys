from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .models import UserPasskey

@login_required
def index(request,enroll=False): # noqa
    keys = UserPasskey.objects.filter(user=request.user) # pragma: no cover
    return render(request,'passkeys/passkeys.html',{"keys":keys,"enroll":enroll}) # pragma: no cover

@require_http_methods(["POST"])
@login_required
def delKey(request):
    id=request.POST.get("id")
    if not id:
        return HttpResponse("Error: You are missing a key", status=403)
    key=UserPasskey.objects.get(id=id)
    if key.user.pk == request.user.pk:
        key.delete()
        return HttpResponse("Deleted Successfully")
    return HttpResponse("Error: You own this token so you can't delete it", status=403)

@require_http_methods(["POST"])
@login_required
def toggleKey(request):
    id=request.POST.get("id")
    if not id:
        return HttpResponse("Error: You are missing a key", status=403)
    q=UserPasskey.objects.filter(user=request.user, id=id)
    if q.count()==1:
        key=q[0]
        key.enabled=not key.enabled
        key.save()
        return HttpResponse("OK")
    return HttpResponse("Error: You own this token so you can't toggle it", status=403)
