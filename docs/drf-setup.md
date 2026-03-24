# REST API Setup (DRF)

This guide covers the DRF integration for SPAs, mobile apps, and headless APIs. Complete the [Common Setup](index.md#common-setup) first.

## 1. Install DRF Extra

=== "DRF"

    ```bash
    pip install django-passkeys[drf]
    ```

=== "DRF + JWT"

    ```bash
    pip install django-passkeys[drf-jwt]
    ```

## 2. Configure

Add `rest_framework` to your apps and include the API URLs:

```python
# settings.py
INSTALLED_APPS = [
    ...
    'rest_framework',
    'passkeys',
]
```

```python
# urls.py
urlpatterns = [
    ...
    path('api/passkeys/', include('passkeys.api.urls')),
]
```

## Endpoints

| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| `POST` | `register/options` | Required | Get WebAuthn registration options |
| `POST` | `register/verify` | Required | Verify and save new credential |
| `POST` | `authenticate/options` | Public | Get WebAuthn authentication options |
| `POST` | `authenticate/verify` | Public | Verify assertion, return token |
| `GET` | `/` | Required | List user's passkeys |
| `GET` | `<id>` | Required | Retrieve a passkey |
| `PATCH` | `<id>` | Required | Update a passkey (name, enabled) |
| `DELETE` | `<id>` | Required | Delete a passkey |

---

## Registration Flow

User must be authenticated to register a new passkey.

### Step 1 — Get options

```http
POST /api/passkeys/register/options
Authorization: Bearer <token>
```

```json title="Response 200"
{
    "options": { "publicKey": { "...": "..." } },
    "state_token": "signed-state-token..."
}
```

### Step 2 — Create credential (browser)

```js
options.publicKey.challenge = base64url.decode(options.publicKey.challenge);
options.publicKey.user.id = base64url.decode(options.publicKey.user.id);
for (let cred of options.publicKey.excludeCredentials) {
    cred.id = base64url.decode(cred.id);
}
const credential = await navigator.credentials.create(options);
```

### Step 3 — Verify

```http
POST /api/passkeys/register/verify
Authorization: Bearer <token>
Content-Type: application/json
```

```json title="Request"
{
    "state_token": "signed-state-token...",
    "key_name": "My Laptop",
    "credential": { "id": "...", "rawId": "...", "response": {}, "type": "public-key" }
}
```

```json title="Response 201"
{
    "id": 1,
    "name": "My Laptop",
    "enabled": true,
    "platform": "Apple",
    "added_on": "2026-03-24T12:00:00Z",
    "last_used": null
}
```

---

## Authentication Flow

No login required. This is how users authenticate with a passkey.

!!! info "Two Authentication Modes"
    - **Discoverable (passwordless)** — omit `username`. The browser shows all passkeys for this domain.
    - **Username-assisted** — send `username` to narrow the prompt to that user's keys. Useful when the user already typed their username.

### Step 1 — Get options

```http
POST /api/passkeys/authenticate/options
Content-Type: application/json
```

```json title="Request (either)"
{}
{"username": "john"}
```

```json title="Response 200"
{
    "options": { "publicKey": { "...": "..." } },
    "state_token": "signed-state-token..."
}
```

### Step 2 — Get assertion (browser)

```js
options.publicKey.challenge = base64url.decode(options.publicKey.challenge);
for (let cred of options.publicKey.allowCredentials) {
    cred.id = base64url.decode(cred.id);
}
const assertion = await navigator.credentials.get(options);
```

### Step 3 — Verify

```http
POST /api/passkeys/authenticate/verify
Content-Type: application/json
```

```json title="Request"
{
    "state_token": "signed-state-token...",
    "credential": { "id": "...", "rawId": "...", "response": {}, "type": "public-key" }
}
```

Response varies by token backend:

=== "JWT"

    ```json
    {"user_id": 1, "username": "john", "token_type": "jwt", "access": "eyJ...", "refresh": "eyJ..."}
    ```

=== "DRF Token"

    ```json
    {"user_id": 1, "username": "john", "token_type": "token", "token": "9944b09199..."}
    ```

=== "Session"

    ```json
    {"user_id": 1, "username": "john", "token_type": "session"}
    ```

---

## Passkey Management

### List passkeys

```http
GET /api/passkeys/
Authorization: Bearer <token>
```

```json title="Response 200"
[
    {"id": 1, "name": "My Laptop", "enabled": true, "platform": "Apple", "added_on": "...", "last_used": "..."}
]
```

### Update a passkey

```http
PATCH /api/passkeys/1
Authorization: Bearer <token>
Content-Type: application/json
```

```json title="Request"
{"name": "Work Laptop", "enabled": false}
```

### Delete a passkey

```http
DELETE /api/passkeys/1
Authorization: Bearer <token>
```

Returns `204 No Content`. Returns `404` if the passkey doesn't exist or isn't owned by the user.

---

## Token Backend

The token backend auto-detects your auth setup. Detection order:

| Priority | Condition | Returns |
|----------|-----------|---------|
| 1 | `PASSKEYS_API_TOKEN_BACKEND` setting is set | Custom callable result |
| 2 | `rest_framework_simplejwt` in `INSTALLED_APPS` | `access` + `refresh` JWT tokens |
| 3 | `rest_framework.authtoken` in `INSTALLED_APPS` | DRF auth `token` |
| 4 | Fallback | Session login |

### Custom Backend

```python
# myapp/auth.py
def my_token_backend(user, request):
    """Must accept (user, request) and return a dict."""
    return {'token_type': 'custom', 'token': generate_my_token(user)}
```

```python
# settings.py
PASSKEYS_API_TOKEN_BACKEND = 'myapp.auth.my_token_backend'
```

---

## How State Tokens Work

The API uses signed state tokens instead of sessions to carry FIDO2 state between `options` and `verify` calls.

| Property | Detail |
|----------|--------|
| **Signing** | HMAC with Django `SECRET_KEY` via `django.core.signing` |
| **Expiry** | 5 minutes |
| **Session** | Written as side-effect when available (backward compat) |
| **Stateless** | Works with JWT/Token auth — no session required |
