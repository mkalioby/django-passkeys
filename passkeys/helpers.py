from django.conf import settings
from django.http import HttpResponseRedirect


def is_login_page(request):
    login_url = request.build_absolute_uri(settings.LOGIN_URL)
    return  request.META.get('HTTP_REFERER',None) ==  login_url

def get_redirection_url(request):
    return HttpResponseRedirect(request.META['HTTP_REFERER'].replace(request.META.get("HTTP_ORIGIN",""),""))