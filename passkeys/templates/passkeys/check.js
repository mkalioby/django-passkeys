function check_passkey(platform_authenticator, success_func, fail_func) {
    {% if request.session.passkey.cross_platform != False %}
    if (platform_authenticator) {
        PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable()
            .then(function(available) {
                if (available) {
                    success_func();
                } else if (fail_func) {
                    fail_func();
                }
            });
        return;
    }
    success_func();
    {% endif %}
}

function check_passkeys(success_func, fail_func) {
    PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable()
        .then(function(available) {
            if (available) {
                success_func();
            } else {
                fail_func();
            }
        }).catch(function(err) {
            console.error(err);
        });
}
