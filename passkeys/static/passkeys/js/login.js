class PassKeyLogin {
    constructor(baseUrl, loginFormId) {
        this.baseUrl = baseUrl;
        this.loginFormId = loginFormId;
    }


    checkConditionalUI() {
        const that = this;

        window.conditionUIAbortController = new AbortController();
        window.conditionUIAbortSignal = conditionUIAbortController.signal;

        if (window.PublicKeyCredential && PublicKeyCredential.isConditionalMediationAvailable) {
            // Check if conditional mediation is available.
            PublicKeyCredential.isConditionalMediationAvailable().then((result) => {
                if (result === true) {
                    that.authn(true)
                }
            });
        }
    }

    getAssertReq(getAssert) {
        getAssert.publicKey.challenge = base64url.decode(getAssert.publicKey.challenge);

        for (let allowCred of getAssert.publicKey.allowCredentials) {
            allowCred.id = base64url.decode(allowCred.id);
        }

        return getAssert;
    }

    function

    authn(conditionalUI = false) {
        const that = this;
        const url = this.baseUrl + 'auth/begin/';

        fetch(url, {method: 'GET'}).then(function (response) {
            if (response.ok) {
                return response.json().then(function (req) {
                    return that.getAssertReq(req)
                });
            }
            throw new Error('No credential available to authenticate!');
        }).then(function (options) {
            if (conditionalUI) {
                options.mediation = 'conditional';
                options.signal = window.conditionUIAbortSignal;

            } else {
                window.conditionUIAbortController.abort()
            }

            return navigator.credentials.get(options);
        }).then(function (assertion) {
            let pk = document.querySelector("#passkeys");

            if (pk.length === 0) {
                console.error("The login form does not contain a passkeys input field!")
                return
            }
            pk.value = JSON.stringify(publicKeyCredentialToJSON(assertion));

            let loginForm = document.getElementById(that.loginFormId);
            if (loginForm === null || loginForm === undefined) {
                console.error("Login form id invalid!")
                return;
            }

            loginForm.submit()
        }, function (error) {
            console.error(error);
        });
    }
}
