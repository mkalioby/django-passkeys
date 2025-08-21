{% load static %}
<script type="application/javascript" src="{% static 'passkeys/js/base64url.js' %}"></script>
<script type="application/javascript" src="{% static 'passkeys/js/helpers.js' %}"></script>
<script type="text/javascript">
    window.allow_immediate=true;
    async function checkImmediateMediationAvailability() {
    if (!window.allow_immediate)
        return [false, false];
    try {
    const capabilities = await PublicKeyCredential.getClientCapabilities();
    if (capabilities.immediateGet && window.PasswordCredential) {
    console.log("Immediate Mediation with passwords supported.");
    return [true, true];
} else if (capabilities.immediateGet) {
    console.log("Immediate Mediation without passwords supported.");
    return [true, false];
} else {
    console.log("Immediate Mediation unsupported.");
    return [false, false];}
} catch (error) {
    console.error("Error getting client capabilities:", error);
    return [false, false];
}
}

function tryLogin(formid)
    {
        window.loginForm = formid;
        if ($("#inputUsername").val() != "" && $("#inputPassword").val() != "")
            $("#" + formid).submit();
        options = {};
        status = checkImmediateMediationAvailability();
        if (status[0] && window.allow_immediate)
        {
            start_authn(formid, false);
        }
    }
    window.conditionalUI = false;
    window.conditionUIAbortController = new AbortController();
    window.conditionUIAbortSignal = conditionUIAbortController.signal;
    function checkConditionalUI(form) {
        if (window.PublicKeyCredential && PublicKeyCredential.isConditionalMediationAvailable) {
        // Check if conditional mediation is available.
        PublicKeyCredential.isConditionalMediationAvailable().then((result) => {
        window.conditionalUI = result;
        if (window.conditionalUI) {
        start_authn(form,true)
    }
});
}
}

    var GetAssertReq = (getAssert) => {
    getAssert.publicKey.challenge = base64url.decode(getAssert.publicKey.challenge);

    for(let allowCred of getAssert.publicKey.allowCredentials) {
    allowCred.id = base64url.decode(allowCred.id);
}

    return getAssert
}

    function start_authn(form, conditionalUI = false)
    {
        window.loginForm = form;
        fetch('{% url 'passkeys:auth_begin' %}', {
        method: 'GET',
    }).then(function(response) {
        if(response.ok) {
        return response.json().then(function (req){
        return GetAssertReq(req)
    });
    }
        throw new Error('No credential available to authenticate!');
    }).then(function(options) {
        if (conditionalUI) {
            options.mediation = 'conditional';
            options.signal = window.conditionUIAbortSignal;
        }
        else
        {
        window.conditionUIAbortController.abort('Stopping conditional UI');
        options.mediation = 'immediate';
        options.password = true;
        }
        console.log(options)
        return navigator.credentials.get(options);
    }).then(function(assertion) {
        if (assertion.type == "password"){
            $("#inputUsername").val(assertion.id);
            $("#inputPassword").val(assertion.password);
            $("#" + window.loginForm).submit();
            return;
    }
        pk = $("#passkeys")
        if (pk.length == 0)
    {
        console.error("Did you add the 'passkeys' hidden input field")
        return
    }
        pk.val(JSON.stringify(publicKeyCredentialToJSON(assertion)));
        x= document.getElementById(window.loginForm)
        if (x === null || x === undefined)
    {
        console.error("Did you pass the correct form id to auth function")
        return;
    }
        x.submit()

    }).catch(function (err)
    {

        if (err.toString() === 'NotAllowedError: No immediate discoverable credentials are found.') {
        window.allow_immediate = false;
        tryLogin(window.loginForm);
    }
        else {
        console.error("Authentication failed: " + err);
    }

    });
        $(document).ready(function () {
        if (location.protocol != 'https:') {
        console.error("Passkeys must work under secure context")
    }
    });
    }
    function authn(form)
    {
        start_authn(form, false)
    }

</script>