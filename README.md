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

This app is a slimmed-down version of [django-mfa2](https://github.com/mkalioby/django-mfa2)

Passkeys are now supported on
* Apple Ecosystem (iPhone 16.0+, iPadOS 16.1, Mac OS X Ventura)
* Chromium based browsers (on PC and Laptop) allows picking up credentials from Android and iPhone/iPadOS.
* Android Credentials creation for ResidentKeys is currently live.

On May 3, 2023, Google allowed the use of Passkeys for the users to login, killing the password for enrolled users.

**[Full Documentation](https://mkalioby.github.io/django-passkeys)**

## Installation

```
pip install django-passkeys
```

For DRF (REST API) support:
```
pip install django-passkeys[drf]

# With JWT:
pip install django-passkeys[drf-jwt]
```

## Choose Your Integration

django-passkeys supports two integration modes. Pick the one that fits your project:

| | Template-Based | REST API (DRF) |
|---|---|---|
| **Best for** | Server-rendered Django apps | SPAs, mobile apps, headless APIs |
| **Auth flow** | Session-based with Django forms | Token-based (JWT, DRF Token, or Session) |
| **Frontend** | Django templates with jQuery | Any frontend (React, Vue, mobile, etc.) |
| **Setup guide** | [Template Setup](docs/template-setup.md) | [DRF Setup](docs/drf-setup.md) |

Both can coexist in the same project — you can use templates for your web app and the API for your mobile app.

### Quick Start — Common Settings

Regardless of which integration you choose, add these to your `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'passkeys',
]

AUTHENTICATION_BACKENDS = ['passkeys.backend.PasskeyModelBackend']
FIDO_SERVER_ID = "localhost"      # Must match your domain
FIDO_SERVER_NAME = "TestApp"
```

Then follow the guide for your chosen integration:
- **[Template-Based Setup](docs/template-setup.md)** — Django templates with session auth
- **[REST API Setup (DRF)](docs/drf-setup.md)** — REST endpoints with pluggable token backend

## Example Project

See the `example` app and [Example.md](Example.md) for a working demo.

## Using Immediate Mediation 

Immediate Mediation is an extension to WebAuthn API that allows the browser to immediately prompt the user to use password/passkeys
without the need of a login form. This is currently supported by Google Chrome 144+ and soon on Android devices. 

You can watch demo showed by Google

[![Watch the video](imgs/immediate.png)](https://developer.chrome.com//static/blog/webauthn-immediate-mediation-ot/video/immediate-mediation-explicit-flow.mp4)

To enable this feature in your pages add a new hidden form in your page that the passkeys can use to send to the server.

```html
{%include 'passkeys/passkeys.js' allow_password=True %}
<form id="loginForm" action="{% url 'login' %}" method="post" style="display: none">
      {% csrf_token %}
    <input type="hidden" id="passkeys" name="passkeys" />
    <input type="hidden" id="username" name="username" />
    <input type="hidden" id="password" name="password" />
  </form>
```

You can check [public.html](exmple/testapp/templates/public.html) for an example of how to configure it.

**Note**: setting `allow_password` to `True` (default `False`) will allow the user to login by password if 
that what is stored in the password manager, otherwise, the user will be forced to login by passkeys.

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