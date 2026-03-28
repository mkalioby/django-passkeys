# Django Template Integration

1. Add passkeys to urls.py
   
    ```python 
     urls_patterns= [
     '...',
      url(r'^passkeys/', include('passkeys.urls')),
     '....',
      ]
    ```
To match the look and feel of your project, Passkeys includes `base.html` but it needs blocks named `head` & `content` to added its content to it.

    !!! note "Customizing Templates"

        1. You can override `passkeys/base.html` which is used by `passkeys/manage.html` so you can control the styling better and current `passkeys/base.html` extends `base.html`
        1. Currently, `passKeys/base.html` needs jQuery and bootstrap. 

1. Somewhere in your app, add a link to 'passkeys:home'

    ```html
    <li><a href="{% url 'passkeys:home' %}">Passkeys</a> </li>
    ```
   
1. In your **login view**, change the authenticate call to include the request as follows
   
    ```python
     user = authenticate(request, username=request.POST["username"],password=request.POST["password"])
    ```

1. Finally, in your **login.html**
    * Give an id to your login form e.g. `loginForm`, the id should be provided when calling `authn` function
    * Inside the form, add 
        ```html
         <input type="hidden" name="passkeys" id="passkeys"/>
         <button class="btn btn-block btn-dark" type="button" onclick="authn('loginForm')"><img src="{% static 'passkeys/imgs/FIDO-Passkey_Icon-White.png' %}" style="width: 24px"/> Login by Passkeys </button>
         {%include 'passkeys/passkeys.js' %}
        ```
 For more information about how to set it up, please see the 'example' app and the [EXAMPLE.md](Example.md) document.

## Check if the user can be enrolled for a platform authenticator

If you want to check if the user can be enrolled to use a platform authenticator, you can do the following in your main page.

```html
<div id="pk" class="alert alert-info" style="display: none">Your device supports passkeys, <a href="{%url 'passkeys:enroll'%}">Enroll</a> </div>
<script type="text/javascript">
function register_pk()
    {
        $('#pk').show();
    }
{% include 'passkeys/check.js'%}
$(document).ready(check_passkey(true,register_pk))
</script>
```
check_passkey function parameters are as follows 

* `platform_authenticator`: if the service requires only a platform authenticator (e.g TouchID, Windows Hello or Android SafetyNet)
* `success_func`: function to call if a platform authenticator is found or if the user didn't login by a passkey
* `fail_func`: function to call if no platform authenticator is found (optional).

## Using Conditional UI

Conditional UI is a way for the browser to prompt the user to use the passkey to login to the system as shown in 

![./imgs/conditionalUI.png](./imgs%2FconditionalUI.png)

Starting version v1.2. you can use Conditional UI by adding the following to your login page

1. Add `webauthn` to autocomplete of the username field as shown below.

    ```html
     <input name="username" placeholder="username" autocomplete="username webauthn">
    ```
2. Add the following to the page js.

    ```js
     window.onload = checkConditionalUI('loginForm');
    ```
where `loginForm` is name of your login form.

## Using Immediate Mediation 

Immediate Mediation is an extension to WebAuthn API that allows the browser to immediately prompt the user to use password/passkeys
without the need of a login form. This is currently supported by Google Chrome 144+ and soon on Android devices. 

You can watch demo presented by Google

[![Watch the video](./imgs/immediate.png)](https://developer.chrome.com//static/blog/webauthn-immediate-mediation-ot/video/immediate-mediation-explicit-flow.mp4)

To enable this feature in your pages add a new hidden form in your page that the passkeys can use to send to the server.

```html
{%include 'passkeys/passkeys.js' allow_password=True %}
<form id="loginForm" action="{% url 'login' %}" method="post" style="display: none">
      {% csrf_token %}
    <input type="hidden" id="passkeys" name="passkeys" />
    <input type="hidden" id="username" name="username" />
    <input type="hidden" id="password" name="password" />
   <input type="hidden" name="next" value="{{ request.get_full_path }}" />
  </form>
```

You can check [public.html](../exmple/testapp/templates/public.html) for an example of how to configure it.

!!! note "Important"
    **Note**: setting `allow_password` to `True` (default `False`) will allow the user to login by password if  that what is stored in the password manager, otherwise, the user will be forced to login by passkeys.
!!! warning 
    if no credentials are found a call to a js function named `no_credentials_found()` is perform, make sure to implement this js function.

