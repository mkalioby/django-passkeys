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


@login_required
@require_http_methods(["DELETE"])
def delete(request, pk):
    key = UserPasskey.objects.filter(user=request.user, pk=pk).first()

    if key is None:
        return HttpResponse("", status=400)

    key.delete()

    return HttpResponse("")


@require_http_methods(["POST"])
@login_required
def toggle(request, pk):
    key = UserPasskey.objects.filter(user=request.user, pk=pk).first()

    if key is None:
        return HttpResponse("", status=400)

    key.enabled = not key.enabled
    key.save()

    return HttpResponse("")
