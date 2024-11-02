function djangoPasskey() {
    let baseUrl = '/passkeys/'

    const passkeyModalDiv = document.querySelector('#passkey-modal');
    if (passkeyModalDiv) {
        const passkeyModal = new bootstrap.Modal('#passkey-modal', {});
        // reload page after the create/delete modal is closed
        passkeyModalDiv.addEventListener('hidden.bs.modal', event => {
            window.location.reload();
        });
    }

    const init = function (url) {
        baseUrl = url;
        if (!baseUrl.endsWith('/')) {
            baseUrl = baseUrl + '/';
        }
    }

    // All urls derive from baseUrl
    const homeUrl = () => baseUrl;

    const urlRegistrationBegin = () => baseUrl + 'reg/begin/';

    const urlRegistrationComplete = () => baseUrl + 'reg/complete/';

    const urlKeyDelete = () => baseUrl + 'delete/';

    const urlKeyToggle = () => baseUrl + 'toggle/';

    // KEY MANAGEMENT RELATED FUNCTIONS

    const checkPasskeySupport = function (success_func, fail_func) {
        PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable()
            .then((available) => {
                if (available) {
                    success_func();
                } else {
                    fail_func();
                }
            })
    }

    const makeCredReq = function (request) {
        request.publicKey.challenge = base64url.decode(request.publicKey.challenge);
        request.publicKey.user.id = base64url.decode(request.publicKey.user.id);

        for (let excludeCred of request.publicKey.excludeCredentials) {
            excludeCred.id = base64url.decode(excludeCred.id);
        }
        return request
    }

    const beginRegistration = function () {
        fetch(urlRegistrationBegin(), {}).then(function (response) {
            if (response.ok) {
                return response.json().then(function (req) {
                    return makeCredReq(req)
                });
            }
            throw new Error('Error getting registration data!');
        }).then(function (options) {
            return navigator.credentials.create(options);
        }).then(function (attestation) {
            attestation["key_name"] = document.getElementById("key_name").value;
            return fetch(urlRegistrationComplete(), {
                    method: 'POST',
                    body: JSON.stringify(publicKeyCredentialToJSON(attestation))
                }
            );
        }).then(function (response) {
            const stat = response.ok ? 'successful' : 'unsuccessful';
            // TODO: what if unsuccessful?
            return response.json()
        }).then(function (res) {
            if (res["status"] === 'OK') {
                passkeyModalResult("success", "Registered successfully");
            } else {
                passkeyModalResult("danger", res["message"]);
            }
        }, function (reason) {
            passkeyModalResult("danger", reason);
        })
    }

    const passkeyModalShow = function (title, body, button) {
        document.querySelector("#passkey-modal .modal-title").innerText = title;
        document.querySelector("#passkey-modal .modal-body").innerHTML = body;

        for (let btn of document.querySelectorAll('#passkey-modal .btn-action')) {
            btn.remove();
        }
        document.querySelector("#passkey-modal .modal-footer").prepend(button);

        passkeyModal.show();
    }

    const passkeyModalResult = function (level, message) {
        const alert = document.createElement("div");
        alert.setAttribute("class", "alert alert-" + level);
        alert.innerHTML = message;

        const body = document.querySelector("#passkey-modal .modal-body");
        body.innerHTML = '';
        body.appendChild(alert);

        const btn = document.querySelector('#passkey-modal .btn-action');
        if (level === "success") {
            btn.remove();
        } else {
            btn.innerText = "Retry";
            btn.setAttribute('class', 'btn btn-warning btn-action');
        }

    }

    const keyCreate = function () {
        const title = "Create a new passkey"
        let body = `
            <p>Please enter a name for your new token</p>
            <p><input type="text" placeholder="e.g Laptop, PC" id="key_name" class="form-control"/></p>
            <div class="result"></div>
            `;

        const button = document.createElement('button');
        button.setAttribute('class', 'btn btn-primary btn-action');
        button.onclick = beginRegistration;
        button.innerText = "Start";

        passkeyModalShow(title, body, button);
    }

    const keyDelete = function (id, name) {
        const title = "Delete passkey";
        const body = `
            <p>Are you sure you want to delete the passkey "${name}"?</p> 
            <p>You may lose access to your system if this your only 2FA.</p>
            `;

        const button = document.createElement('button');
        button.setAttribute('class', 'btn btn-danger btn-action');
        button.onclick = () => keyDeleteConfirm(id);
        button.innerText = "Confirm";
        document.querySelector("#passkey-modal .modal-footer").prepend(button);

        passkeyModalShow(title, body, button);
    }


    const keyDeleteConfirm = function (id) {
        fetch(urlKeyDelete(), {
            method: "post",
            headers: {"X-CSRFToken": "{{csrf_token}}", "Content-Type": "application/x-www-form-urlencoded",},
            body: `id=${id}`
        })
            .then(response => response.text())
            .then(data => {
                document.querySelector("#passkey-modal .modal-body").innerText = data;
                document.querySelector("#passkey-modal .btn-action").remove();
            });
    }


    const keyToggle = function (id) {
        fetch(urlKeyToggle(), {
                method: "post",
                headers: {"X-CSRFToken": "{{csrf_token}}", "Content-Type": "application/x-www-form-urlencoded"},
                body: `id=${id}`
            }
        ).then(response => response.text()).then((response) => {
            if (response === "Error")
                document.querySelector("#toggle_" + id).toggle();
        }).catch(() => {
            document.querySelector("#toggle_" + id).toggle();
        })
    }

    return {
        'init': init,
        'checkPasskeySupport': checkPasskeySupport,
        'keyCreate': keyCreate,
        'keyDelete': keyDelete,
        'keyToggle': keyToggle
    }
}

var DjangoPasskey;

if (typeof (DjangoPasskey) === "undefined") {
    DjangoPasskey = djangoPasskey();
}
