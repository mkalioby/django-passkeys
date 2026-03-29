{% load static %}
<script type="application/javascript" src="{% static 'passkeys/js/base64url.js' %}"></script>
<script type="application/javascript" src="{% static 'passkeys/js/helpers.js' %}"></script>
<script type="text/javascript">
    window.allow_password={% if allow_password %}true{% else %}false{% endif %};
    async function checkImmediateMediationAvailability() {
    // if (!window.allow_immediate)
    //     return [false, false];
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
        usernamefield = document.getElementById("username");
        passwordfield = document.getElementById("password");
        window.loginForm = formid;
        if (usernamefield.value != "" && passwordfield.value != "") {
        document.getElementById(formid).submit();
    }
        options = {};
        status = await checkImmediateMediationAvailability();
        if (status[0])
        {
            start_authn(formid, false);
        }
        else{
           if (usernamefield.value == "")
            usernamefield.focus();
           else if (passwordfield.value == "")
            passwordfield.focus();
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
        options.uiMode = 'immediate';
        options.password = window.allow_password;
        }
        console.log(options)
        return navigator.credentials.get(options);
    }).then(function(assertion) {
        if (assertion.type == "password"){
            document.getElementById("username").value = assertion.id;
            document.getElementById("password").value = assertion.password;
            document.getElementById(window.loginForm).submit();
            return;
    }
        pk = document.getElementById("passkeys")
        if (pk  === null || pk === undefined )
    {
        console.error("Did you add the 'passkeys' hidden input field")
        return
    }
        pk.value = JSON.stringify(publicKeyCredentialToJSON(assertion));
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
        // window.allow_immediate = false;
        no_credentials_found()
        //tryLogin(window.loginForm);

    }
        else if(err.toString() === "NotAllowedError: An allowCredentials is not allowed with immediate mediation.")
    {
        // window.allow_immediate = false;
        // window.href = "{%url 'login'%}"
    }
        else {
        console.error("Authentication failed: " + err);
    }

    });
    }
        document.addEventListener('DOMContentLoaded',function () {
        if (location.protocol != 'https:') {
        console.error("Passkeys must work under secure context")
    }
    })
    function authn(form)
    {
        start_authn(form, false)
    }

</script>