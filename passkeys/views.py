from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import UserPasskey


@login_required
def index(request):  # noqa
    keys = UserPasskey.objects.filter(user=request.user)  # pragma: no cover
    return render(request, 'passkeys/passkeys.html', {"keys": keys})  # pragma: no cover


@require_http_methods(["POST"])
@csrf_exempt
@login_required
def delete(request):
    pk = request.POST.get("id")
    if pk is None:
        return HttpResponse("Error: You are missing a key", status=403)

    key = UserPasskey.objects.filter(user=request.user, pk=pk).first()

    if key is None:
        return HttpResponse("Unknown key.", status=403)

    key.delete()

    return HttpResponse("Key successfully deleted.")


@require_http_methods(["POST"])
@csrf_exempt
@login_required
def toggle(request):
    pk = request.POST.get("id")
    if pk is None:
        return HttpResponse("Error: You are missing a key", status=403)

    key = UserPasskey.objects.filter(user=request.user, pk=pk).first()

    if key is None:
        return HttpResponse("Unknown key.", status=403)

    key.enabled = not key.enabled
    key.save()

    return HttpResponse("OK")
