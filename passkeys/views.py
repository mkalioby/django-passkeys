from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST

from .models import UserPasskey


@login_required
def index(request, enroll=False):  # noqa
    keys = UserPasskey.objects.filter(user=request.user)  # pragma: no cover
    return render(request, 'passkeys/manage.html', {"keys": keys, "enroll": enroll})  # pragma: no cover


@login_required
@require_POST
def del_key(request):
    key = get_object_or_404(UserPasskey, id=request.POST["id"])
    if key.user_id != request.user.pk:
        raise PermissionDenied("You don't own this token so you can't delete it")
    key.delete()
    return HttpResponse("Deleted Successfully")


@login_required
@require_POST
def toggle_key(request):
    key = get_object_or_404(UserPasskey, user=request.user, id=request.POST["id"])
    key.enabled = not key.enabled
    key.save(update_fields=['enabled'])
    return HttpResponse("OK")
