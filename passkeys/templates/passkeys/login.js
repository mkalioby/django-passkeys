{% load static %}
<script type="application/javascript" src="{% static 'passkeys/js/base64url.js' %}"></script>
<script type="application/javascript" src="{% static 'passkeys/js/helpers.js' %}"></script>
<script type="text/javascript">
    window.conditionalUI = false;
    window.conditionUIAbortController = new AbortController();
    window.conditionUIAbortSignal = conditionUIAbortController.signal;

    function checkConditionalUI(form) {
        if (window.PublicKeyCredential && PublicKeyCredential.isConditionalMediationAvailable) {
            PublicKeyCredential.isConditionalMediationAvailable().then(function(result) {
                window.conditionalUI = result;
                if (window.conditionalUI) {
                    startAuthn(form, true);
                }
            });
        }
    }

    function decodeAssertionRequest(getAssert) {
        getAssert.publicKey.challenge = base64url.decode(getAssert.publicKey.challenge);
        for (let allowCred of getAssert.publicKey.allowCredentials) {
            allowCred.id = base64url.decode(allowCred.id);
        }
        return getAssert;
    }

    function startAuthn(form, conditionalUI) {
        window.loginForm = form;
        fetch('{% url "passkeys:auth_begin" %}', {
            method: 'GET',
        }).then(function(response) {
            if (response.ok) {
                return response.json().then(function(req) {
                    return decodeAssertionRequest(req);
                });
            }
            throw new Error('No credential available to authenticate!');
        }).then(function(options) {
            if (conditionalUI) {
                options.mediation = 'conditional';
                options.signal = window.conditionUIAbortSignal;
            } else {
                window.conditionUIAbortController.abort();
            }
            return navigator.credentials.get(options);
        }).then(function(assertion) {
            const pk = $("#passkeys");
            if (pk.length === 0) {
                console.error("Did you add the 'passkeys' hidden input field");
                return;
            }
            pk.val(JSON.stringify(publicKeyCredentialToJSON(assertion)));
            const loginForm = document.getElementById(window.loginForm);
            if (!loginForm) {
                console.error("Did you pass the correct form id to authn function");
                return;
            }
            loginForm.submit();
        });

        $(document).ready(function() {
            if (location.protocol !== 'https:') {
                console.warn("Passkeys require a secure context (HTTPS)");
            }
        });
    }

    function authn(form) {
        startAuthn(form, false);
    }
</script>
