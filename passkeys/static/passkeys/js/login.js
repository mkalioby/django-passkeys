window.conditionalUI = false;
window.conditionUIAbortController = new AbortController();
window.conditionUIAbortSignal = conditionUIAbortController.signal;

function checkConditionalUI() {
    if (window.PublicKeyCredential && PublicKeyCredential.isConditionalMediationAvailable) {
        // Check if conditional mediation is available.
        PublicKeyCredential.isConditionalMediationAvailable().then((result) => {
            window.conditionalUI = result;
        });
    }
}

var GetAssertReq = (getAssert) => {
    getAssert.publicKey.challenge = base64url.decode(getAssert.publicKey.challenge);

    for (let allowCred of getAssert.publicKey.allowCredentials) {
        allowCred.id = base64url.decode(allowCred.id);
    }

    return getAssert
}

async function get_credential(options, allow_password = false) {
    options = GetAssertReq(options)
    // if (window.conditionUIAbortController) {
    //     window.conditionUIAbortController.abort('Stopping conditional UI');
    // }
    options.uiMode = 'immediate';
    options.password = allow_password;
    data = {}
    assertion = await navigator.credentials.get(options)
    data = {'type': assertion.type}
    if (assertion.type == "password") {
        data.username = assertion.id;
        data.password = assertion.password;
    } else
        data.credential = publicKeyCredentialToJSON(assertion);
    return data;
    // })
}

document.addEventListener('DOMContentLoaded', function () {
    if (location.protocol != 'https:') {
        console.error("Passkeys must work under secure context")
    }
})

