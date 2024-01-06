from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render

from .models import UserPasskey


@login_required
def index(request, enroll=False):  # noqa
    keys = UserPasskey.objects.filter(user=request.user)  # pragma: no cover
    return render(request, "PassKeys.html", {"keys": keys, "enroll": enroll})  # pragma: no cover


@login_required
def delKey(request):
    key = get_object_or_404(UserPasskey, id=request.GET["id"], user=request.user)
    key.delete()
    return HttpResponse("Deleted Successfully")


@login_required
def toggleKey(request):
    key = UserPasskey.objects.filter(id=request.GET["id"], user=request.user).first()
    if key is not None:
        key.enabled = not key.enabled
        key.save(update_fields=["enabled"])
        return HttpResponse("OK")
    return HttpResponseForbidden("Error: You own this token so you can't toggle it")
