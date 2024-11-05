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
    let urlBase = '/passkeys/';

    if (location.protocol !== 'https:') {
        console.error("Passkeys must work under secure context.");
    }

    const modalElem = document.querySelector('#django-passkeys-modal');
    if (modalElem !== null) {
        modalElem.addEventListener('hidden.bs.modal', event => {
            window.location.href = urlBase;
        });
    }


    window.conditionalUI = false;
    window.conditionUIAbortController = new AbortController();
    window.conditionUIAbortSignal = conditionUIAbortController.signal;


    const urlAuthBegin = () => `${urlBase}auth/begin/`;
    const urlKeyToggle = () => `${urlBase}toggle/`;
    const urlKeyDelete = () => `${urlBase}del/`;
    const urlRegBegin = () => `${urlBase}reg/begin/`;
    const urlRegComplete = () => `${urlBase}reg/complete/`;


    /**
     * change the base url for the passkeys app
     *
     * @param url
     */
    const init = function (url) {
        baseUrl = "";
        if (!baseUrl.endsWith('/')) {
            baseUrl += '/;'
        }
    }

    const publicKeyCredentialToJSON = function (pubKeyCred) {
        if (pubKeyCred instanceof Array) {
            let arr = [];
            for (let i of pubKeyCred)
                arr.push(publicKeyCredentialToJSON(i));

            return arr;
        }

        if (pubKeyCred instanceof ArrayBuffer) {
            return base64url.encode(pubKeyCred);
        }

        if (pubKeyCred instanceof Object) {
            let obj = {};

            for (let key in pubKeyCred) {
                obj[key] = publicKeyCredentialToJSON(pubKeyCred[key]);
            }

            return obj;
        }

        return pubKeyCred;
    }


    const checkConditionalUI = function (form) {
        if (window.PublicKeyCredential && PublicKeyCredential.isConditionalMediationAvailable) {
            // Check if conditional mediation is available.
            PublicKeyCredential.isConditionalMediationAvailable().then((result) => {
                window.conditionalUI = result;
                if (window.conditionalUI) {
                    authn(form, true);
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

    /**
     * start the authentication process
     *
     * @param loginFormId
     * @param conditionalUI
     */
    const authn = function (loginFormId, conditionalUI = false) {
        fetch(urlAuthBegin(), {
            method: 'GET',
        }).then(function (response) {
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
                window.conditionUIAbortController.abort();
            }

            return navigator.credentials.get(options);
        }).then(function (assertion) {
            const passkeysInput = document.querySelector("#id_passkeys");
            if (passkeysInput === null) {
                console.error("Did you add the 'passkeys' hidden input field")
                return
            }
            passkeysInput.value = JSON.stringify(publicKeyCredentialToJSON(assertion));

            const loginForm = document.getElementById(loginFormId);

            if (loginForm === null) {
                console.error("Did you pass the correct form id to auth function")
                return;
            }

            loginForm.submit()
        });
    }


    /**
     * Check if the platform supports passkeys.
     *
     * @param success_func
     * @param fail_func
     */
    const checkPasskeysSupport = function (success_func, fail_func) {
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

    /**
     * (De-)activate a passkey.
     *
     * @param id
     */
    const keyToggle = function (id) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch(urlKeyToggle(), {
                method: "post",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: `id=${id}`
            }
        ).then(response => response.text()).then((response) => {
            if (response === "Error")
                document.querySelector("#toggle_" + id).toggle();
        }).catch(() => {
            document.querySelector("#toggle_" + id).toggle();
        })
    }

    /**
     * Confirm deleting a passkey.
     *
     * @param id
     * @param name
     */
    const keyDeleteConfirm = function (id, name) {
        const title = "Delete passkey";
        const body = `
            <p>Are you sure you want to delete '${name}'?</p> 
            <p>You may lose access to this system if this your only 2FA.</p>
            `;

        const button = document.createElement('button');
        button.setAttribute('class', 'btn btn-danger btn-action');
        button.onclick = () => keyDelete(id);
        button.innerText = "Confirm";

        showModal(title, body, button);
    }

    /**
     * Delete a passkey.
     *
     * @param id
     */
    const keyDelete = function (id) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        fetch(urlKeyDelete(), {
            method: "post",
            headers: {
                "X-CSRFToken": csrfToken,
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: `id=${id}`
        })
            .then(response => response.text())
            .then(data => {
                const title = "Confirm delete";
                const body = '<p class="alert alert-success">The key has been deleted successfully.</p>'
                updateModal(title, body);
            });
    }


    const makeCredReq = function (makeCredReq) {
        makeCredReq.publicKey.challenge = base64url.decode(makeCredReq.publicKey.challenge);
        makeCredReq.publicKey.user.id = base64url.decode(makeCredReq.publicKey.user.id);

        for (let excludeCred of makeCredReq.publicKey.excludeCredentials) {
            excludeCred.id = base64url.decode(excludeCred.id);
        }

        return makeCredReq
    }

    /**
     * Start passkey registration
     */
    const beginReg = function () {
        fetch(urlRegBegin(), {}).then(function (response) {
            if (response.ok) {
                return response.json().then(function (req) {
                    return makeCredReq(req)
                });
            }
            throw new Error('Error getting registration data!');
        }).then(function (options) {
            //options.publicKey.attestation="direct"
            return navigator.credentials.create(options);
        }).then(function (attestation) {
            attestation["key_name"] = document.getElementById("key_name").value;
            return fetch(urlRegComplete(), {
                    method: 'POST',
                    body: JSON.stringify(publicKeyCredentialToJSON(attestation))
                }
            );
        }).then(function (response) {
            const stat = response.ok ? 'successful' : 'unsuccessful';
            return response.json()
        }).then(function (res) {
            if (res["status"] === 'OK') {
                const title = "Register new passkey";
                const body = '<p class="alert alert-success">Passkey was successfully registered.</p>';
                updateModal(title, body);
            } else {
                const title = "Register new passkey";
                const body = `<p class="alert alert-danger">Passkey registration failed!</p><p>${res["message"]}</p>`;
                updateModal(title, body);
            }
        }, function (reason) {
            const title = "Register new passkey";
            const body = `<p class="alert alert-danger">Passkey registration failed!</p><p>${reason}</p>`;
            updateModal(title, body);
        });
    }

    /**
     * Open passkey registration dialog.
     */
    const registration = function () {
        const title = "Register new passkey"
        const body = `
                <p>Please enter a name for your new token.</p>
                <input type="text" placeholder="e.g Laptop, PC" id="key_name" class="form-control"/>
                `;

        const button = document.createElement('button');
        button.setAttribute('class', 'btn btn-primary btn-action');
        button.onclick = beginReg;
        button.innerText = "Start";

        showModal(title, body, button);
    }

    /**
     * Update and show the passkey modal.
     *
     * @param title
     * @param body
     * @param actionButton
     */
    const showModal = function (title, body, actionButton) {
        updateModal(title, body, actionButton);
        const modal = new bootstrap.Modal('#django-passkeys-modal', {});
        modal.show();
    }

    /**
     * Update the already visible passkey modal.
     *
     * @param title
     * @param body
     * @param actionButton
     */
    const updateModal = function (title, body, actionButton) {
        // update title
        const titleElem = document.querySelector('#django-passkeys-modal .modal-title');
        titleElem.innerText = title;

        // update body
        const bodyElem = document.querySelector('#django-passkeys-modal .modal-body');
        bodyElem.innerHTML = body;

        // remove existing action buttons
        for (let button of document.querySelectorAll('#django-passkeys-modal .btn-action')) {
            button.remove();
        }

        // insert action button
        if (actionButton) {
            const footer = document.querySelector('#django-passkeys-modal .modal-footer');
            footer.prepend(actionButton);
        }
    }

    // create the global DjangoPasskey variable
    if (typeof window.DjangoPasskeys === 'undefined') {
        window.DjangoPasskeys = {
            'init': init,
            'checkConditionalUI': checkConditionalUI,
            'authn': authn,
            'checkPasskeysSupport': checkPasskeysSupport,
            'keyToggle': keyToggle,
            'keyDeleteConfirm': keyDeleteConfirm,
            'registration': registration,
        }
    }
})();