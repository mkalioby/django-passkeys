# django-passkeys

[![PyPI version](https://badge.fury.io/py/django-passkeys.svg)](https://badge.fury.io/py/django-passkeys)
[![Downloads](https://static.pepy.tech/badge/django-passkeys)](https://pepy.tech/project/django-passkeys)
[![Downloads / Month ](https://pepy.tech/badge/django-passkeys/month)](https://pepy.tech/project/django-passkeys)
[![build](https://github.com/mkalioby/django-passkeys/actions/workflows/basic_checks.yml/badge.svg)](https://github.com/mkalioby/django-passkeys/actions/workflows/basic_checks.yml)
![Coverage](https://raw.githubusercontent.com/mkalioby/django-passkeys/main/coverage.svg)

![Django Versions](https://img.shields.io/pypi/frameworkversions/django/django-passkeys)
![Python Versions](https://img.shields.io/pypi/pyversions/django-passkeys)


An extension to Django *ModelBackend* backend to support passkeys.

Passkeys is an extension to Web Authentication API that will allow the user to login to a service using another device.

This app is a slim-down version of [django-mfa2](https://github.com/mkalioby/django-mfa2)

Passkeys are now supported on
* Apple Ecosystem (iPhone 16.0+, iPadOS 16.1, Mac OS X Ventura)
* Chromium based browsers (on PC and Laptop) allows picking up credentials from Android and iPhone/iPadOS.
* Android Credentials creation for ResidentKeys is currently live now.

On May 3, 2023, Google allowed the use of Passkeys for the users to login, killing the password for enrolled users.

# Installation

`pip install django-passkeys`

Supports Django 4.2+, Python 3.10+

# Usage
1. In your settings.py add the application to your installed apps
   ```python
   INSTALLED_APPS = [
       '......',
       'passkeys',
       '......',
   ]
   ```
2. Collect Static Files
   ```
   python manage.py collectstatic
   ```
3. Run migrate
   ```
   python manage.py migrate
   ```
4. Add the following settings to your file

   ```python
   AUTHENTICATION_BACKENDS = ['passkeys.backend.PasskeyModelBackend']
   FIDO_SERVER_ID = "localhost"      # Server rp id for FIDO2, must match your domain
   FIDO_SERVER_NAME = "TestApp"
   import passkeys
   KEY_ATTACHMENT = None  # or passkeys.Attachment.CROSS_PLATFORM or passkeys.Attachment.PLATFORM
   ```
   **Note**: `FIDO_SERVER_ID` and/or `FIDO_SERVER_NAME` can be a callable to support multi-tenant web applications. The `request` object is passed to the callable.

   **Important**: `FIDO_SERVER_ID` must match the domain you access the site from. For local development, use `localhost` and access via `http://localhost:8000/` (not `127.0.0.1`).

5. Add passkeys to urls.py
   ```python
   urlpatterns = [
       '...',
       path('passkeys/', include('passkeys.urls')),
       '...',
   ]
   ```
6. To match the look and feel of your project, Passkeys includes `base.html` but it needs blocks named `head` & `content` to add its content to it.

   **Notes:**

    1. You can override `PassKeys_base.html` which is used by `Passkeys.html` so you can control the styling better. The default `Passkeys_base.html` extends `base.html`.
    2. Currently, `PassKeys_base.html` needs jQuery and Bootstrap.

7. Somewhere in your app, add a link to 'passkeys:home'
    ```html
    <li><a href="{% url 'passkeys:home' %}">Passkeys</a></li>
    ```
8. In your login view, change the authenticate call to include the request as follows
   ```python
   user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
   ```

9. In your `login.html`
   * Give an id to your login form e.g `loginForm`, the id should be provided when calling the `authn` function
   * Inside the form, add
     ```html
     <input type="hidden" name="passkeys" id="passkeys"/>
     <button class="btn btn-block btn-dark" type="button" onclick="authn('loginForm')">
         <img src="{% static 'passkeys/imgs/FIDO-Passkey_Icon-White.png' %}" style="width: 24px">
     </button>
     {% include 'passkeys.js' %}
     ```

For a full example, see the `example` app and look at [Example.md](Example.md) for setup instructions.

# Detect if user is using passkeys

Once the backend is used, there will be a `passkey` key in `request.session`.
If the user used a passkey then `request.session['passkey']['passkey']` will be `True` and the key information will be available:
```python
{'passkey': True, 'name': 'Chrome', 'id': 2, 'platform': 'Chrome on Apple', 'cross_platform': False}
```
`cross_platform` means that the user used a key from another platform, so there is no key local to the device used to login (e.g. used an Android phone on Mac OS X or iPad).

If the user didn't use a passkey then it will be:
```python
{'passkey': False}
```


# Check if the user can be enrolled for a platform authenticator

If you want to check if the user can be enrolled to use a platform authenticator, you can do the following in your main page.

```html
<div id="pk" class="alert alert-info" style="display: none">
    Your device supports passkeys, <a href="{% url 'passkeys:enroll' %}">Enroll</a>
</div>
<script type="text/javascript">
function register_pk() {
    $('#pk').show();
}
{% include 'check_passkeys.js' %}
$(document).ready(check_passkey(true, register_pk))
</script>
```
`check_passkey` function parameters:
* `platform_authenticator`: if the service requires only a platform authenticator (e.g TouchID, Windows Hello or Android SafetyNet)
* `success_func`: function to call if a platform authenticator is found or if the user didn't login by a passkey
* `fail_func`: function to call if no platform authenticator is found (optional).


## Using Conditional UI

Conditional UI is a way for the browser to prompt the user to use the passkey to login to the system as shown below:

![conditionalUI.png](imgs%2FconditionalUI.png)

Starting version v1.2, you can use Conditional UI by adding the following to your login page:

1. Add `webauthn` to autocomplete of the username field:
```html
<input name="username" placeholder="username" autocomplete="username webauthn">
```

2. Add the following to the page JavaScript:
```js
window.onload = checkConditionalUI('loginForm');
```
where `loginForm` is the id of your login form.

## Security contact information

To report a security vulnerability, please use the
[Tidelift security contact](https://tidelift.com/security).
Tidelift will coordinate the fix and disclosure.

# Contributors
* [mahmoodnasr](https://github.com/mahmoodnasr)
* [jacopsd](https://github.com/jacopsd)
* [gasparbrogueira](https://github.com/gasparbrogueira)
* [pulse-mind](https://github.com/pulse-mind)
