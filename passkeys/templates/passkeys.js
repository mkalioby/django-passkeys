{% load static %}
<script type="application/javascript" src="{% static 'passkeys/js/base64url.js' %}"></script>
<script type="application/javascript" src="{% static 'passkeys/js/helpers.js' %}"></script>
<script type="text/javascript">
var GetAssertReq = (getAssert) => {
           getAssert.publicKey.challenge = base64url.decode(getAssert.publicKey.challenge);

            for(let allowCred of getAssert.publicKey.allowCredentials) {
                allowCred.id = base64url.decode(allowCred.id);
            }

            return getAssert
        }
        function authn(form)
        {
            window.loginForm=form
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
        console.log(options)
      return navigator.credentials.get(options);
    }).then(function(assertion) {

        $("#passkeys").val(JSON.stringify(publicKeyCredentialToJSON(assertion)));
        document.getElementById(window.loginForm).submit()


        });
    $(document).ready(function () {
        if (location.protocol != 'https:') {
            console.error("Passkeys must work under secure context")
        }
    });
        }


    </script>