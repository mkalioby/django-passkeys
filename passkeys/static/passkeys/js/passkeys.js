(function () {
    'use strict';

    let chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_';

    // Use a lookup table to find the index.
    let lookup = new Uint8Array(256);
    for (let i = 0; i < chars.length; i++) {
        lookup[chars.charCodeAt(i)] = i;
    }

    let encode = function (arraybuffer) {
        let bytes = new Uint8Array(arraybuffer),
            i, len = bytes.length, base64url = '';

        for (i = 0; i < len; i += 3) {
            base64url += chars[bytes[i] >> 2];
            base64url += chars[((bytes[i] & 3) << 4) | (bytes[i + 1] >> 4)];
            base64url += chars[((bytes[i + 1] & 15) << 2) | (bytes[i + 2] >> 6)];
            base64url += chars[bytes[i + 2] & 63];
        }

        if ((len % 3) === 2) {
            base64url = base64url.substring(0, base64url.length - 1);
        } else if (len % 3 === 1) {
            base64url = base64url.substring(0, base64url.length - 2);
        }

        return base64url;
    };

    let decode = function (base64string) {
        let bufferLength = base64string.length * 0.75,
            len = base64string.length, i, p = 0,
            encoded1, encoded2, encoded3, encoded4;

        let bytes = new Uint8Array(bufferLength);

        for (i = 0; i < len; i += 4) {
            encoded1 = lookup[base64string.charCodeAt(i)];
            encoded2 = lookup[base64string.charCodeAt(i + 1)];
            encoded3 = lookup[base64string.charCodeAt(i + 2)];
            encoded4 = lookup[base64string.charCodeAt(i + 3)];

            bytes[p++] = (encoded1 << 2) | (encoded2 >> 4);
            bytes[p++] = ((encoded2 & 15) << 4) | (encoded3 >> 2);
            bytes[p++] = ((encoded3 & 3) << 6) | (encoded4 & 63);
        }

        return bytes.buffer
    };

    let methods = {
        'decode': decode,
        'encode': encode
    }

    /**
     * Exporting and stuff
     */
    if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
        module.exports = methods;

    } else {
        if (typeof define === 'function' && define.amd) {
            define([], function () {
                return methods
            });
        } else {
            window.base64url = methods;
        }
    }
})();

(function () {
    let baseUrl = '/passkeys/'

    const passkeyModalDiv = document.querySelector('#passkey-modal');
    let passkeyModal;

    if (passkeyModalDiv) {
        passkeyModal = new bootstrap.Modal('#passkey-modal', {});
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

    const urlAuthBegin = () => baseUrl + 'auth/begin/';

    const urlAuthComplete = () => baseUrl + 'auth/complete/';

    /** HELPER FUNCTIONS **/

    const publicKeyCredentialToJSON = (pubKeyCred) => {
        if (pubKeyCred instanceof Array) {
            let arr = [];
            for (let i of pubKeyCred)
                arr.push(publicKeyCredentialToJSON(i));

            return arr
        }

        if (pubKeyCred instanceof ArrayBuffer) {
            return base64url.encode(pubKeyCred)
        }

        if (pubKeyCred instanceof Object) {
            let obj = {};

            for (let key in pubKeyCred) {
                obj[key] = publicKeyCredentialToJSON(pubKeyCred[key])
            }

            return obj
        }

        return pubKeyCred
    }

    /*
     * KEY MANAGEMENT RELATED FUNCTIONS
     */

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
        const url = `${urlKeyDelete()}${id}/`
        const csrf_token = document.querySelector("[name=csrfmiddlewaretoken]").value;

        fetch(url, {
            method: "delete",
            headers: {"X-CSRFToken": csrf_token}
        }).then(response => {
            if (response.ok) {
                passkeyModalResult("success", "Successfully deleted passkey.");
            } else {
                passkeyModalResult("danger", "Could not delete passkey.");
            }
        });
    }


    const keyToggle = function (id) {
        const url = `${urlKeyToggle()}${id}/`;
        const csrf_token = document.querySelector("[name=csrfmiddlewaretoken]").value;

        fetch(url, {
            method: "post",
            headers: {"X-CSRFToken": csrf_token}
        }).then(response => {
            if (response.ok) {
                // TODO
            } else {
                // TODO
            }
        })
    }

    /*
    * LOGIN RELATED FUNCTIONS
     */


    const checkConditionalUI = function () {
        window.conditionUIAbortController = new AbortController();
        window.conditionUIAbortSignal = conditionUIAbortController.signal;

        if (window.PublicKeyCredential && PublicKeyCredential.isConditionalMediationAvailable) {
            // Check if conditional mediation is available.
            PublicKeyCredential.isConditionalMediationAvailable().then((result) => {
                if (result === true) {
                    authn(true)
                }
            });
        }
    }

    const getAssertReq = function (getAssert) {
        getAssert.publicKey.challenge = base64url.decode(getAssert.publicKey.challenge);

        for (let allowCred of getAssert.publicKey.allowCredentials) {
            allowCred.id = base64url.decode(allowCred.id);
        }

        return getAssert;
    }

    const authn = function (conditionalUI = false) {
        fetch(urlAuthBegin(), {method: 'GET'}).then(function (response) {
            if (response.ok) {
                return response.json().then(function (req) {
                    return getAssertReq(req)
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

            let loginForm = document.getElementById('loginForm');
            if (loginForm === null || loginForm === undefined) {
                console.error("Login form id invalid!")
                return;
            }

            loginForm.submit()
        }, function (error) {
            console.error(error);
        });
    }

    /*
    * EXPORTS
     */

    if (typeof window.DjangoPasskey === 'undefined') {
        window.DjangoPasskey = {
            'init': init,
            'checkPasskeySupport': checkPasskeySupport,
            'keyCreate': keyCreate,
            'keyDelete': keyDelete,
            'keyToggle': keyToggle,
            'checkConditionalUI': checkConditionalUI,
            'authn': authn
        }
    }

})();
