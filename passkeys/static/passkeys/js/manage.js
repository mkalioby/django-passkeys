function PasskeyManager(baseUrl) {
    const homeUrl = baseUrl;
    const reqBeginUrl = baseUrl + 'reg/begin/';
    const regCompleteUrl = baseUrl + 'reg/complete/';
    const deleteUrl = baseUrl + 'delete/';
    const toggleUrl = baseUrl + 'toggle/';

    const check_passkey_support = function (success_func, fail_func) {
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
        console.log("---");
        console.log(request);
        return request
    }

    const beginRegistration = function () {

        fetch(reqBeginUrl, {}).then(function (response) {
            if (response.ok) {
                return response.json().then(function (req) {
                    console.log("ok!");
                    return makeCredReq(req)
                });
            }
            throw new Error('Error getting registration data!');
        }).then(function (options) {
            console.log("create");
            return navigator.credentials.create(options);
        }).then(function (attestation) {
            console.log("attestation");
            attestation["key_name"] = document.getElementById("key_name").value;
            return fetch(regCompleteUrl, {
                    method: 'POST',
                    body: JSON.stringify(publicKeyCredentialToJSON(attestation))
                }
            );
        }).then(function (response) {
            console.log("stat");
            const stat = response.ok ? 'successful' : 'unsuccessful';
            console.log(stat);
            return response.json()
        }).then(function (res) {
            console.log("result");
            if (res["status"] === 'OK') {
                document.getElementById("res").innerHTML = "<div class='alert alert-success'>Registered Successfully, <a href='.'> Refresh</a></div>";
            } else {
                document.getElementById("res").innerHTML = "<div class='alert alert-danger'>Registration Failed as " + res["message"] + ", <a href='javascript:void(0)' onclick='begin_reg()'> try again </a> </div>";
            }

        }, function (reason) {
            console.log("fail");
            document.getElementById("res").innerHTML = "<div class='alert alert-danger'>Registration Failed as " + reason + ", <a href='javascript:void(0)' onclick='begin_reg()'> try again </a> </div>";
        })
    }


    const start = function () {
        document.getElementById("modal-title").innerText = "Enter a token name"
        document.getElementById("modal-body").innerHTML = `<p>Please enter a name for your new token</p>
                                <input type="text" placeholder="e.g Laptop, PC" id="key_name" class="form-control"/><br/><div id="res"></div>`;
        document.getElementById("actionBtn")?.remove();
        const button = document.createElement('button');
        button.id = 'actionBtn';
        button.setAttribute('class', 'btn btn-success');
        button.onclick = beginRegistration;
        button.innerText = "Start";
        document.getElementById("modal-footer").prepend(button);

        const popUpModal = new bootstrap.Modal('#popUpModal', {});
        popUpModal.show();
    }

    const deleteKey = function (id, name) {
        document.getElementById("modal-title").innerText = "Confirm Delete";
        document.getElementById("modal-body").innerHTML = "Are you sure you want to delete '" + name + "'? you may lose access to your system if this your only 2FA." + `<div id="res"></div>`;
        document.getElementById("actionBtn")?.remove();

        const button = document.createElement('button');
        button.id = 'actionBtn';
        button.setAttribute('class', 'btn btn-danger');
        button.onclick = () => confirmDelete(id);
        button.innerText = "Confirm Deletion";
        document.getElementById("modal-footer").prepend(button);

        const popUpModal = new bootstrap.Modal('#popUpModal', {});
        popUpModal.show();
        $("#modal-footer").prepend(button);
        $("#popUpModal").modal('show');
    }


    const confirmDelete = function (id) {
        fetch(deleteUrl, {
            method: "post",
            headers: {"X-CSRFToken": "{{csrf_token}}", "Content-Type": "application/x-www-form-urlencoded",},
            body: `id=${id}`
        })
            .then(response => response.text())
            .then(data => {
                alert(data);
                window.location = homeUrl
            });
    }


    const toggleKey = function (id) {
        fetch(toggleUrl, {
                method: "post",
                headers: {"X-CSRFToken": "{{csrf_token}}", "Content-Type": "application/x-www-form-urlencoded",},
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
        'check_passkey_support': check_passkey_support,
        'start': start,
        'delete': deleteKey,
        'toggle': toggleKey
    }
}