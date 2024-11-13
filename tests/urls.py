from django.urls import path, include

urlpatterns = [
    path("passkeys/", include("passkeys.urls")),
]
