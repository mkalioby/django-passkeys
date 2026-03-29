function check_passkey(platform_authenticator = true,success_func, fail_func)
{
    {% if request.session.passkey.cross_platform != False %}
    if (platform_authenticator)
    {
        PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable()
  .then((available) => {
    if (available) {
      success_func();
    }
    else{
        fail_func();
    }
    })
  }
    success_func();
    {% endif%}
}

function check_passkeys(success_func, fail_func)
{
    PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable()
  .then((available) => {
    if (available) {
      success_func();
    } else {
      fail_func()
    }
  }).catch((err) => {
    // Something went wrong
    console.error(err);
  });
}