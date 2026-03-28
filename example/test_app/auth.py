from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.serializers import Serializer, CharField
from rest_framework.views import APIView

from passkeys.api.token_backends import get_token_response

def loginView(request):
    context={}
    if request.method=="POST":
        user=authenticate(request, username=request.POST["username"],password=request.POST["password"])
        if user:
            login(request, user)
            if request.POST.get("next",""):
                return redirect(request.POST["next"])
            return redirect('template') # pragma: no cover
        context["invalid"]=True
    return render(request, "login.html", context)

# def create_session(request,username):
#     user=User.objects.get(username=username)
#     user.backend='django.contrib.auth.backends.ModelBackend'
#     login(request, user)
#     return HttpResponseRedirect(reverse('home'))


def logoutView(request):
    logout(request) # pragma: no cover
    return  render(request,"logout.html",{}) # pragma: no cover


class LoginSerializer(Serializer):
    username = CharField()
    password = CharField()


class LoginAPIView(APIView):
    """
    Username + password login API.

    Returns the same token format as passkey authentication
    (JWT, DRF Token, or session depending on project config).
    Use this to get an initial token before registering passkeys.
    """

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
        )
        if user is None:
            raise AuthenticationFailed("Invalid username or password")
        token_data = get_token_response(user, request)
        return Response({
            'user_id': user.pk,
            'username': user.get_username(),
            **token_data,
        })