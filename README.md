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
* Android Credentials creation for ResidentKeys is currently live.

On May 3, 2023, Google allowed the use of Passkeys for the users to login, killing the password for enrolled users. 

# Installation

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
    1. Currently, `PassKeys_base.html` needs jQuery and bootstrap. 

7. Somewhere in your app, add a link to 'passkeys:home'
    ```html
    <li><a href="{% url 'passkeys:home' %}">Passkeys</a> </li>
   ```
8. In your login view, change the authenticate call to include the request as follows
   
   ```python
    user = authenticate(request, username=request.POST["username"],password=request.POST["password"])
   ```

8. Finally, In your `login.html`
   * Give an id to your login form e.g 'loginForm', the id should be provided when calling `authn` function
   * Inside the form, add 
     ```html
      <input type="hidden" name="passkeys" id="passkeys"/>
      <button class="btn btn-block btn-dark" type="button" onclick="authn('loginForm')"><img src="{% static 'passkeys/imgs/FIDO-Passkey_Icon-White.png' %}" style="width: 24px"></button>
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


## Using Conditional UI

Conditional UI is a way for the browser to prompt the user to use the passkey to login to the system as shown in 

![conditionalUI.png](imgs%2FconditionalUI.png)

Starting version v1.2. you can use Conditional UI by adding the following to your login page

1. Add `webauthn` to autocomplete of the username field as shown below.
```html
<input name="username" placeholder="username" autocomplete="username webauthn">
```
add the following to the page js.

```js
window.onload = checkConditionalUI('loginForm');
```
where `loginForm` is name of your login form.

# REST API (Django REST Framework)

An optional DRF module provides REST endpoints for passkey registration, authentication, and management.

## Installation

```bash
pip install django-passkeys[drf]

# With JWT support:
pip install django-passkeys[drf-jwt]
```

## Setup

1. Add `rest_framework` to your `INSTALLED_APPS`:
   ```python
   INSTALLED_APPS = [
       ...
       'rest_framework',
       'passkeys',
   ]
   ```

2. Add the API URLs to your project:
   ```python
   urlpatterns = [
       ...
       path('api/passkeys/', include('passkeys.api.urls')),
   ]
   ```

## API Endpoints

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| `GET` | `/api/passkeys/` | Required | List user's passkeys |
| `GET` | `/api/passkeys/<id>` | Required | Retrieve a passkey |
| `PATCH` | `/api/passkeys/<id>` | Required | Update a passkey (name, enabled) |
| `DELETE` | `/api/passkeys/<id>` | Required | Delete a passkey |
| `POST` | `/api/passkeys/register/options` | Required | Get WebAuthn registration options |
| `POST` | `/api/passkeys/register/verify` | Required | Verify and save new credential |
| `POST` | `/api/passkeys/authenticate/options` | Public | Get WebAuthn authentication options |
| `POST` | `/api/passkeys/authenticate/verify` | Public | Verify assertion and return token |

## Registration Flow (user must be logged in)

**Step 1 — Get registration options:**
```
POST /api/passkeys/register/options
Authorization: Bearer <token>

Response 200:
{
    "options": { "publicKey": { ... } },
    "state_token": "signed-state-token..."
}
```

**Step 2 — Create credential in the browser:**
```js
options.publicKey.challenge = base64url.decode(options.publicKey.challenge);
options.publicKey.user.id = base64url.decode(options.publicKey.user.id);
for (let cred of options.publicKey.excludeCredentials) {
    cred.id = base64url.decode(cred.id);
}

const credential = await navigator.credentials.create(options);
```

**Step 3 — Verify and save:**
```
POST /api/passkeys/register/verify
Authorization: Bearer <token>
Content-Type: application/json

{
    "state_token": "signed-state-token...",
    "key_name": "My Laptop",
    "credential": { "id": "...", "rawId": "...", "response": {...}, "type": "public-key" }
}

Response 201:
{
    "id": 1, "name": "My Laptop", "enabled": true,
    "platform": "Apple", "added_on": "...", "last_used": null
}
```

## Authentication Flow (no login required)

WebAuthn supports two authentication modes:

- **Discoverable (passwordless)** — send an empty body or omit `username`. The browser/OS shows all passkeys the user has saved for this domain and lets them pick one. This is the true passwordless experience.
- **Username-assisted** — send `username` to narrow the prompt to only that user's registered passkeys. Useful when the user has already typed their username in the login form.

**Step 1 — Get authentication options:**
```
POST /api/passkeys/authenticate/options
Content-Type: application/json

{}                       // discoverable — browser shows all passkeys for this site
{ "username": "john" }   // username-assisted — only shows john's passkeys

Response 200:
{
    "options": { "publicKey": { ... } },
    "state_token": "signed-state-token..."
}
```

**Step 2 — Get assertion in the browser:**
```js
options.publicKey.challenge = base64url.decode(options.publicKey.challenge);
for (let cred of options.publicKey.allowCredentials) {
    cred.id = base64url.decode(cred.id);
}

const assertion = await navigator.credentials.get(options);
```

**Step 3 — Verify and get token:**
```
POST /api/passkeys/authenticate/verify
Content-Type: application/json

{
    "state_token": "signed-state-token...",
    "credential": { "id": "...", "rawId": "...", "response": {...}, "type": "public-key" }
}

Response 200 (varies by token backend):
{ "user_id": 1, "username": "john", "token_type": "jwt", "access": "...", "refresh": "..." }
{ "user_id": 1, "username": "john", "token_type": "token", "token": "..." }
{ "user_id": 1, "username": "john", "token_type": "session" }
```

## Passkey Management

```
# List all passkeys for the authenticated user
GET /api/passkeys/
Authorization: Bearer <token>

Response 200:
[{ "id": 1, "name": "My Laptop", "enabled": true, "platform": "Apple", "added_on": "...", "last_used": "..." }]

# Update a passkey (name, enabled)
PATCH /api/passkeys/1
Authorization: Bearer <token>
Content-Type: application/json

{ "name": "Work Laptop", "enabled": false }

Response 200:
{ "id": 1, "name": "Work Laptop", "enabled": false, "platform": "Apple", ... }

# Delete a passkey (returns 404 if not owned by user)
DELETE /api/passkeys/1
Authorization: Bearer <token>

Response 204
```

## Token Backend

After successful passkey authentication, the API returns a token based on your project's auth configuration. Detection order:

1. **`PASSKEYS_API_TOKEN_BACKEND`** setting (if set) — a dotted path to a custom callable
2. **SimpleJWT** — if `rest_framework_simplejwt` is in `INSTALLED_APPS`, returns `access` and `refresh` tokens
3. **DRF Token** — if `rest_framework.authtoken` is in `INSTALLED_APPS`, returns a `token`
4. **Session** (fallback) — logs the user in via Django session

### Custom Token Backend

```python
# myapp/auth.py
def my_token_backend(user, request):
    """Custom backend must accept (user, request) and return a dict."""
    token = generate_my_token(user)
    return {'token_type': 'custom', 'token': token}

# settings.py
PASSKEYS_API_TOKEN_BACKEND = 'myapp.auth.my_token_backend'
```

## State Token

The API uses signed state tokens (Django's `signing` module) instead of sessions to carry FIDO2 state between `options` and `verify` calls. This means:

- **Stateless clients** (mobile apps, SPAs with JWT) work without sessions
- Tokens are HMAC-signed with your `SECRET_KEY` and expire after **5 minutes**
- Sessions are still written as a side-effect when available, for backward compatibility

## Security contact information

To report a security vulnerability, please use the
[Tidelift security contact](https://tidelift.com/security).
Tidelift will coordinate the fix and disclosure.

# Contributors
* [mahmoodnasr](https://github.com/mahmoodnasr)
* [jacopsd](https://github.com/jacopsd)   
* [gasparbrogueira](https://github.com/gasparbrogueira)
* [pulse-mind](https://github.com/pulse-mind)
* [ashokdelphia](https://github.com/ashokdelphia)
* [offbyone](https://github.com/offbyone)
* [resba](https://github.com/resba)
* [ganiyevuz](https://github.com/ganiyevuz)
