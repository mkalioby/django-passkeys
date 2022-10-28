# django-passkeys

An extension to Django ModelBackend backend to support passkeys.

Passkeys is an extension to Web Authentication API that will allow the user to login to a service using another device.

This app is a slim-down version of [django-mfa2](https://github.com/mkalioby/django-mfa2)

Passkeys are now supported on 
* Apple Ecosystem (iPhone 16.0+, iPadOS 16.1, Mac OS X Ventura)
* Chromium based browsers (on PC and Laptop) allows picking up credentials from Android and iPhone/iPadOS.
* Android Credentials creation for ResidentKeys is currently in Beta.

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
3. Add the following settings to your file

   ```python
    AUTHENTICATION_BACKENDS = ['passkeys.backend.PasskeyModelBackend'] # Change your authentication backend
    FIDO_SERVER_ID="localhost"      # Server rp id for FIDO2, it the full domain of your project
    FIDO_SERVER_NAME="TestApp"
    import passkeys
    KEY_ATTACHMENT = NONE | passkeys.Attachment.CROSS_PLATFORM | passkeys.Attachment.PLATFORM
   ```
4. Add passkeys to urls.py
   ```python 

   urls_patterns= [
   '...',
   url(r'^passkeys/', include('passkeys.urls')),
   '....',
    ]
    ```
5. To match the look and feel of your project, Passkeys includes `base.html` but it needs blocks named `head` & `content` to added its content to it.
   **Note:** You can override `PassKeys_base.html` which is used by `Passkeys.html` so you can control the styling better and current `Passkeys_base.html` extends `base.html`

6. Somewhere in your app, add a link to 'mfa_home'
```<li><a href="{% url 'passkeys:home' %}">Passkeys</a> </li>```

7. In your `login.html`
   * Give an id to your login form e.g 'loginForm'
   * Inside the form, add 
     ```html
      <input type="hidden" name="passkeys" id="passkeys"/>
      <button class="btn btn-block btn-dark" type="button" onclick="authn('loginForm')"><img src="{% static 'passkeys/imgs/FIDO-Passkey_Icon-White.png' %}" style="width: 24px">
     {%include 'passkeys.js' %}
     ```
For Example, See 'example' app and look at EXAMPLE.md to see how to set it up.



