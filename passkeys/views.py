from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .models import UserPasskey


@login_required
def index(request, enroll=False):  # noqa
    keys = UserPasskey.objects.filter(user=request.user)  # pragma: no cover
    return render(request, 'passkeys/passkeys.html', {"keys": keys, "enroll": enroll})  # pragma: no cover


@require_http_methods(["POST"])
@login_required
def delKey(request):
    pk = request.POST.get("id")
    if not pk:
        return HttpResponse("Error: You are missing a key", status=403)

    key = UserPasskey.objects.filter(user=request.user, pk=pk).first()

    if key is None:
        return HttpResponse("Error: You own this token so you can't delete it", status=403)

    key.delete()
    return HttpResponse("Deleted Successfully")


@require_http_methods(["POST"])
@login_required
def toggleKey(request):
    pk = request.POST.get("id")
    if not pk:
        return HttpResponse("Error: You are missing a key", status=403)

    key = UserPasskey.objects.filter(user=request.user, pk=pk).first()

    if key is None:
        return HttpResponse("Error: You own this token so you can't toggle it", status=403)

    key.enabled = not key.enabled
    key.save()
    return HttpResponse("OK")
