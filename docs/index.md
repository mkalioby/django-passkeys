# django-passkeys

A Django authentication backend for passkeys (WebAuthn/FIDO2). Drop-in passwordless login for your Django project.

## Supported Platforms

| Platform | Version |
|----------|---------|
| Apple (iPhone, iPad, Mac) | iOS 16+, iPadOS 16.1+, macOS Ventura |
| Chromium (Chrome, Edge) | Desktop and mobile — picks up credentials from Android/iPhone |
| Android | Native resident key creation |
| Windows | Windows Hello |

## Install

```bash
pip install django-passkeys
```

For REST API support:

**DRF**

```bash
pip install django-passkeys[drf]
```

**DRF + JWT**

```bash
pip install django-passkeys[drf-jwt]
```

## Common Setup

Add these to your `settings.py` regardless of which integration you use:

```python
INSTALLED_APPS = [
    ...
    'passkeys',
]

AUTHENTICATION_BACKENDS = ['passkeys.backend.PasskeyModelBackend']

FIDO_SERVER_ID = "localhost"       # (1)
FIDO_SERVER_NAME = "My App"
```

1. Must match your domain exactly. See [Settings Reference](settings.md#fido_server_id).

Then run migrations:

```bash
python manage.py migrate
```

## Choose Your Integration

| | Template-Based | REST API (DRF) |
|---|---|---|
| **Best for** | Server-rendered Django apps | SPAs, mobile apps, headless APIs |
| **Auth flow** | Session-based with Django forms | Token-based (JWT, DRF Token, or Session) |
| **Frontend** | Django templates with jQuery | Any frontend (React, Vue, mobile, etc.) |
| **Guide** | [Template Setup](template-setup.md) | [DRF Setup](drf-setup.md) |

!!! tip
    Both can coexist in the same project — use templates for your web app and the API for your mobile app.

## Example Project

A working example is included in the repository:

```bash
git clone https://github.com/mkalioby/django-passkeys.git
cd django-passkeys
python -m venv env && source env/bin/activate
pip install -r requirements.txt
cd example
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://localhost:8000/` in your browser.

!!! warning
    Use `localhost` not `127.0.0.1` — WebAuthn requires the domain to match `FIDO_SERVER_ID`.

For HTTPS (required in production):

```bash
pip install django-sslserver
python manage.py runsslserver
```