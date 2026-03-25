# django-passkeys

[![PyPI version](https://badge.fury.io/py/django-passkeys.svg)](https://badge.fury.io/py/django-passkeys)
[![Downloads](https://static.pepy.tech/badge/django-passkeys)](https://pepy.tech/project/django-passkeys)
[![Downloads / Month ](https://pepy.tech/badge/django-passkeys/month)](https://pepy.tech/project/django-passkeys)
[![build](https://github.com/mkalioby/django-passkeys/actions/workflows/basic_checks.yml/badge.svg)](https://github.com/mkalioby/django-passkeys/actions/workflows/basic_checks.yml)
![Coverage](https://raw.githubusercontent.com/mkalioby/django-passkeys/main/coverage.svg)

![Django Versions](https://img.shields.io/pypi/frameworkversions/django/django-passkeys)
![Python Versions](https://img.shields.io/pypi/pyversions/django-passkeys)

**[Full Documentation](https://mkalioby.github.io/django-passkeys)**

An extension to Django *ModelBackend* backend to support passkeys. Supports both django templates and REST API (Django REST Framework) with pluggable token backends (JWT, DRF Token, or Session).

Passkeys is an extension to Web Authentication API that will allow the user to login to a service using another device.

This app is a slimmed-down version of [django-mfa2](https://github.com/mkalioby/django-mfa2)

Passkeys are now supported on
* Apple Ecosystem (iPhone 16.0+, iPadOS 16.1, Mac OS X Ventura)
* Chromium based browsers (on PC and Laptop) allows picking up credentials from Android and iPhone/iPadOS.
* Android Credentials creation for ResidentKeys is currently live.

On May 3, 2023, Google allowed the use of Passkeys for the users to login, killing the password for enrolled users.

## Special Features

django-passkeys supports the following features:
1. **Conditional UI** is a way for the browser to prompt the user to use the passkey to login as shown. 
![conditionalUI.png](imgs%2FconditionalUI.png)

1. **Immediate Mediation** is an extension to WebAuthn API that allows the browser to immediately prompt the 
user to use password/passkeys without the need of a login form. This is currently supported by Google Chrome 144+ and soon on Android devices.

You can watch demo presented by Google

[![Watch the video](imgs/immediate.png)](https://developer.chrome.com//static/blog/webauthn-immediate-mediation-ot/video/immediate-mediation-explicit-flow.mp4)

# Quick Start - Common Settings

`pip install django-passkeys`

Supports Django 2.0+, Python 3.7+

# Usage
1. In your settings.py add the application to your installed apps
   ```python
   INSTALLED_APPS=(
   '......',
   'passkeys',
   '......')
   ```
2. Collect Static Files
   ```shell
   python manage.py collectstatic
   ```

3. Run migrate
   ```shell
    python manage.py migrate
   ```
4. Add the following settings to your file

   ```python
    AUTHENTICATION_BACKENDS = ['passkeys.backend.PasskeyModelBackend'] # Change your authentication backend
    FIDO_SERVER_ID="localhost"      # Server rp id for FIDO2, must match your domain
    FIDO_SERVER_NAME="TestApp"
    import passkeys
    KEY_ATTACHMENT = None # or passkeys.Attachment.CROSS_PLATFORM or  passkeys.Attachment.PLATFORM
   ```
   **Notes**
    
   * Starting v1.1, `FIDO_SERVER_ID` and/or `FIDO_SERVER_NAME` can be a callable to support multi-tenant web applications, the `request` is passed to the called function. 
   * `FIDO_SERVER_ID` must match the domain you access the site from. For local development, use `localhost` and access via `http://localhost:8000/` (not `127.0.0.1`).


# Detect if user is using passkeys
Once the backend is used, there will be a `passkey` key in request.session. 
If the user used a passkey then `request.session['passkey']['passkey']` will be `True` and the key information will be there like this

```python
{'passkey': True, 'name': 'Chrome', 'id': 2, 'platform': 'Chrome on Apple', 'cross_platform': False}
```
`cross_platform`: means that the user used a key from another platform so there is no key local to the device used to login e.g used an Android phone on Mac OS X or iPad.
If the user didn't use a passkey then it will be set to False
```python
{'passkey':False}
```

By this the basic installation of django-passkeys, your next step depends on whether you want to use the Django Template integration or the REST API (Django REST Framework) integration.

## Choose Your Integration

django-passkeys supports two integration modes. Pick the one that fits your project:

| | Template-Based | REST API (DRF) |
|---|---|---|
| **Best for** | Server-rendered Django apps | SPAs, mobile apps, headless APIs |
| **Auth flow** | Session-based with Django forms | Token-based (JWT, DRF Token, or Session) |
| **Frontend** | Django templates with jQuery | Any frontend (React, Vue, mobile, etc.) |
| **Setup guide** | [Template Setup](docs/template-setup.md) | [DRF Setup](docs/drf-setup.md) |

Both can coexist in the same project — you can use templates for your web app and the API for your mobile app.

## Example Project

See the `example` app and [Example.md](Example.md) for a working demo.


## Security contact information

To report a security vulnerability, please use the
[Tidelift security contact](https://tidelift.com/security).
Tidelift will coordinate the fix and disclosure.

## Contributors
* [mahmoodnasr](https://github.com/mahmoodnasr)
* [jacopsd](https://github.com/jacopsd)
* [gasparbrogueira](https://github.com/gasparbrogueira)
* [pulse-mind](https://github.com/pulse-mind)
* [ashokdelphia](https://github.com/ashokdelphia)
* [offbyone](https://github.com/offbyone)
* [resba](https://github.com/resba)
* [ganiyevuz](https://github.com/ganiyevuz)
* [smark-1](https://github.com/smark-1)
* [ThomasWaldmann-1](https://github.com/ThomasWaldmann)
* [rafaelurben](https://github.com/rafaelurben)