{% load static %}
<script type="application/javascript" src="{% static 'passkeys/js/base64url.js' %}"></script>
<script type="application/javascript" src="{% static 'passkeys/js/helpers.js' %}"></script>
<script type="text/javascript">
    window.conditionalUI=false;
    window.conditionUIAbortController = new AbortController();
    window.conditionUIAbortSignal = conditionUIAbortController.signal;
    function checkConditionalUI(form) {
    if (window.PublicKeyCredential && PublicKeyCredential.isConditionalMediationAvailable) {
    // Check if conditional mediation is available.
    PublicKeyCredential.isConditionalMediationAvailable().then((result) => {
    window.conditionalUI = result;
    if (window.conditionalUI) {
    pk_login(form,true)
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
        function authn(form)
        {
            window.conditionUIAbortController.abort();
            pk_login(form,false);
        }

        function pk_login(form,conditionalUI)
        {
            window.loginForm=form;
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
            options.mediation= 'conditional';
            options.signal = conditionUIAbortSignal;
        }
        console.log(options)
      return navigator.credentials.get(options);
    }).then(function(assertion) {
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

        }).catch(function(err) {})
    $(document).ready(function () {
        if (location.protocol != 'https:') {
            console.error("Passkeys must work under secure context")
        }
    });
        }


    </script>