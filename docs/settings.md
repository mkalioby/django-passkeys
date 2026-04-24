# Settings Reference

All settings go in your Django `settings.py`.

## Required

### `FIDO_SERVER_ID`

The Relying Party ID for WebAuthn. **Must exactly match the domain users access your site from.**

```python
# Simple
FIDO_SERVER_ID = "example.com"

# Multi-tenant (callable, receives request)
def get_server_id(request):
    return request.get_host().split(':')[0]

FIDO_SERVER_ID = get_server_id
```

!!! warning
    `127.0.0.1` and `localhost` are **different domains** to WebAuthn. For local development, use `"localhost"` and access via `http://localhost:8000/`.

### `FIDO_SERVER_NAME`

Human-readable name for your service. Shown to users during passkey registration.

```python
FIDO_SERVER_NAME = "My App"

# Multi-tenant
FIDO_SERVER_NAME = lambda request: request.tenant.name
```

### `AUTHENTICATION_BACKENDS`

Must include the passkey backend:

```python
AUTHENTICATION_BACKENDS = ['passkeys.backend.PasskeyModelBackend']
```

## Optional

### `KEY_ATTACHMENT`

Controls which authenticator types are allowed during registration. Default: `None` (allow all).

| Value | Authenticators |
|-------|---------------|
| `None` | All (platform + roaming) |
| `passkeys.Attachment.PLATFORM` | Only platform (TouchID, FaceID, Windows Hello) |
| `passkeys.Attachment.CROSS_PLATFORM` | Only roaming (USB/NFC security keys) |

```python
import passkeys
KEY_ATTACHMENT = passkeys.Attachment.PLATFORM
```

### `PASSKEYS_API_TOKEN_BACKEND`

*DRF only.* Override the auto-detected token backend with a custom callable.

```python
PASSKEYS_API_TOKEN_BACKEND = 'myapp.auth.my_token_backend'
```

The callable receives `(user, request)` and must return a `dict`. See [DRF Token Backend](drf-setup.md#token-backend).

### `PASSKEYS_ALLOW_EMPTY_REQUEST`

Default: `False`.

If `True`, allows empty request to passkeys, useful when having multiple authentication backends.

### `PASSKEYS_ALLOW_NO_PASSKEY_FIELD`

Default: `False`.

If `True`, allows request not to have a `passkey` field, useful when having multiple authentication backends.

