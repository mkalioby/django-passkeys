# django-passkeys

[![Downloads](https://pepy.tech/badge/django-passkeys/month)](https://pepy.tech/project/django-passkeys)

An extension to Django *ModelBackend* backend to support passkeys.

Passkeys is an extension to Web Authentication API that will allow the user to login to a service using another device.

This app is a slim-down version of [django-mfa2](https://github.com/mkalioby/django-mfa2)

Passkeys are now supported on 
* Apple Ecosystem (iPhone 16.0+, iPadOS 16.1, Mac OS X Ventura)
* Chromium based browsers (on PC and Laptop) allows picking up credentials from Android and iPhone/iPadOS.
* Android Credentials creation for ResidentKeys is currently in live now

On May 3, 2023, Google allowed the use of Passkeys for the users to login, killing the password for enrolled users. 

# Installation

`pip install django-passkeys`

Currently, it support Django 2.0+, Python 3.7+

# Usage
1. in your settings.py add the application to your installed apps
   ```python
   INSTALLED_APPS=(
   '......',
   'passkeys',
   '......')
   ```
2. Collect Static Files
`python manage.py collectstatic`
3. Run migrate
`python manage.py migrate`
4. Add the following settings to your file

   ```python
    AUTHENTICATION_BACKENDS = ['passkeys.backend.PasskeyModelBackend'] # Change your authentication backend
    FIDO_SERVER_ID="localhost"      # Server rp id for FIDO2, it the full domain of your project
    FIDO_SERVER_NAME="TestApp"
    import passkeys
    KEY_ATTACHMENT = NONE | passkeys.Attachment.CROSS_PLATFORM | passkeys.Attachment.PLATFORM
   ```
   **Note**: Starting v1.1, `FIDO_SERVER_ID` and/or `FIDO_SERVER_NAME` can be callable to support multi-tenants web applications.
5. Add passkeys to urls.py
   ```python 

   urls_patterns= [
   '...',
   url(r'^passkeys/', include('passkeys.urls')),
   '....',
    ]
    ```
6. To match the look and feel of your project, Passkeys includes `base.html` but it needs blocks named `head` & `content` to added its content to it.
   **Notes:** 
    
    1. You can override `PassKeys_base.html` which is used by `Passkeys.html` so you can control the styling better and current `Passkeys_base.html` extends `base.html`
    1. Currently, `PassKeys_base.html` needs JQuery and bootstrap. 

7. Somewhere in your app, add a link to 'passkeys:home'
    ```<li><a href="{% url 'passkeys:home' %}">Passkeys</a> </li>```
8. In your login view, change the authenticate call to include the request as follows
   ```python
    user=authenticate(request, username=request.POST["username"],password=request.POST["password"])
    ```

8. Finally, In your `login.html`
   * Give an id to your login form e.g 'loginForm', the id should be provided when calling `authn` function
   * Inside the form, add 
     ```html
      <input type="hidden" name="passkeys" id="passkeys"/>
      <button class="btn btn-block btn-dark" type="button" onclick="authn('loginForm')"><img src="{% static 'passkeys/imgs/FIDO-Passkey_Icon-White.png' %}" style="width: 24px">
     {%include 'passkeys.js' %}
     ```
For Example, See 'example' app and look at EXAMPLE.md to see how to set it up.

# Detect if user is using passkeys
Once the backend is used, there will be a `passkey` key in request.session. 
If the user used a passkey then `request.session['passkey']['passkey']` will be True and the key information will be there like this
```python
{'passkey': True, 'name': 'Chrome', 'id': 2, 'platform': 'Chrome on Apple', 'cross_platform': False}
```
`cross_platform`: means that the user used a key from another platform so there is no key local to the device used to login e.g used an Android phone on Mac OS X or iPad.
If the user didn't use a passkey then it will be set to False
```python
{'passkey':False}
```

# Check if the user can be enrolled for a platform authenticator

If you want to check if the user can be enrolled to use a platform authenticator, you can do the following in your main page.

```html
<div id="pk" class="alert alert-info" style="display: none">Your device supports passkeys, <a href="{%url 'passkeys:enroll'%}">Enroll</a> </div>
<script type="text/javascript">
function register_pk()
    {
        $('#pk').show();
    }
{% include 'check_passkeys.js'%}
$(document).ready(check_passkey(true,register_pk))
</script>
```
check_passkey function paramters are as follows 
* `platform_authenticator`: if the service requires only a platform authenticator (e.g TouchID, Windows Hello or Android SafetyNet)
* `success_func`: function to call if a platform authenticator is found or if the user didn't login by a passkey
* `fail_func`: function to call if no platform authenticator is found (optional).


## Security contact information

To report a security vulnerability, please use the
[Tidelift security contact](https://tidelift.com/security).
Tidelift will coordinate the fix and disclosure.

# Contributors
* [mahmoodnasr](https://github.com/mahmoodnasr)
* [jacopsd](https://github.com/jacopsd)   
* [gasparbrogueira](https://github.com/gasparbrogueira)




