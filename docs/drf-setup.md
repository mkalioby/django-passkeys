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
from django.urls import path, include

urlpatterns = [
    ...
    path('api/passkeys/', include('passkeys.api.urls')),
]
```

## Endpoints Overview

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

## Complete Registration Flow

User must be authenticated to register a new passkey. This is a two-step process: first get the WebAuthn challenge options from the server, then pass the browser's credential response back.

### Step 1 — Get registration options

Send a POST request to get the WebAuthn `PublicKeyCredentialCreationOptions`. The server returns the challenge, relying party info, user info, and a signed `state_token` that ties the two steps together.

```http
POST /api/passkeys/register/options
Authorization: Bearer <your-auth-token>
```

**Response `200 OK`:**

```json
{
    "options": {
        "publicKey": {
            "rp": {
                "id": "example.com",
                "name": "My App"
            },
            "user": {
                "id": "am9obg==",
                "name": "john",
                "displayName": "John Doe"
            },
            "challenge": "dGVzdC1jaGFsbGVuZ2U...",
            "pubKeyCredParams": [
                {"type": "public-key", "alg": -7},
                {"type": "public-key", "alg": -257}
            ],
            "excludeCredentials": [],
            "authenticatorSelection": {
                "residentKey": "preferred",
                "userVerification": "preferred"
            }
        }
    },
    "state_token": "eyJhbGciOi..."
}
```

| Field | Description |
|-------|-------------|
| `options.publicKey` | Standard WebAuthn `PublicKeyCredentialCreationOptions` — pass directly to `navigator.credentials.create()` |
| `options.publicKey.challenge` | Base64URL-encoded challenge — must be decoded to `ArrayBuffer` before passing to the browser |
| `options.publicKey.user.id` | Base64URL-encoded user ID — must be decoded to `ArrayBuffer` |
| `options.publicKey.excludeCredentials` | List of already-registered credential IDs — browser will skip these |
| `state_token` | Signed server state — must be sent back in the verify step. Expires in 5 minutes |

### Step 2 — Create credential in the browser

Decode the binary fields and call the WebAuthn browser API:

```js
// Decode binary fields from base64url to ArrayBuffer
const { options, state_token } = await response.json();
options.publicKey.challenge = base64url.decode(options.publicKey.challenge);
options.publicKey.user.id = base64url.decode(options.publicKey.user.id);
for (let cred of options.publicKey.excludeCredentials) {
    cred.id = base64url.decode(cred.id);
}

// Browser prompts user for biometric/PIN
const credential = await navigator.credentials.create(options);

// Convert the credential to a JSON-serializable object
// (credential.response contains ArrayBuffers that need base64url encoding)
const credentialJSON = {
    id: credential.id,
    rawId: base64url.encode(credential.rawId),
    response: {
        clientDataJSON: base64url.encode(credential.response.clientDataJSON),
        attestationObject: base64url.encode(credential.response.attestationObject),
    },
    type: credential.type,
};
```

!!! note "base64url helper"
    You need a base64url encode/decode utility. The library ships one at `passkeys/static/passkeys/js/base64url.js`, or use any npm package like `base64url` or `@hexagon/base64`.

### Step 3 — Verify and save the credential

Send the credential and state token back to the server:

```http
POST /api/passkeys/register/verify
Authorization: Bearer <your-auth-token>
Content-Type: application/json
```

**Request body:**

```json
{
    "state_token": "eyJhbGciOi...",
    "key_name": "My Laptop",
    "credential": {
        "id": "credentialIdBase64url...",
        "rawId": "credentialIdBase64url...",
        "response": {
            "clientDataJSON": "eyJ0eXBlIjoid2ViYXV0aG4uY3Jl...",
            "attestationObject": "o2NmbXRkbm9uZWdhdHRTdG10..."
        },
        "type": "public-key"
    }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `state_token` | Yes | The token from the options step |
| `key_name` | No | Human-readable name (e.g. "Work Laptop"). Defaults to detected platform ("Apple", "Google", etc.) |
| `credential` | Yes | The WebAuthn credential object from `navigator.credentials.create()` |
| `credential.id` | Yes | Base64URL-encoded credential ID |
| `credential.response.clientDataJSON` | Yes | Base64URL-encoded client data |
| `credential.response.attestationObject` | Yes | Base64URL-encoded attestation |

**Response `201 Created`:**

```json
{
    "id": 1,
    "name": "My Laptop",
    "enabled": true,
    "platform": "Apple",
    "added_on": "2026-03-24T12:00:00Z",
    "last_used": null
}
```

**Error responses:**

| Status | Cause |
|--------|-------|
| `400` | Invalid or expired state token, verification failed, or passkey already registered |
| `401/403` | Not authenticated |

---

## Complete Authentication Flow

No login required — this is how users log in with a passkey. Two-step process similar to registration.

!!! info "Two Authentication Modes"
    **Discoverable (passwordless)** — omit `username` or send `{}`. The browser/OS shows all passkeys the user has saved for this domain and lets them pick. This is the true passwordless flow.

    **Username-assisted** — send `{"username": "john"}` to narrow the prompt to that user's registered passkeys. Useful when the user already typed their username in your login form.

### Step 1 — Get authentication options

```http
POST /api/passkeys/authenticate/options
Content-Type: application/json
```

**Request body (choose one):**

```json
{}
```
```json
{"username": "john"}
```

| Field | Required | Description |
|-------|----------|-------------|
| `username` | No | If provided, only that user's credentials are included in `allowCredentials`. If omitted, the browser shows all discoverable passkeys for this domain |

**Response `200 OK`:**

```json
{
    "options": {
        "publicKey": {
            "rpId": "example.com",
            "challenge": "cmFuZG9tLWNoYWxsZW5nZQ...",
            "allowCredentials": [
                {
                    "id": "credentialIdBase64url...",
                    "type": "public-key"
                }
            ],
            "userVerification": "preferred"
        }
    },
    "state_token": "eyJhbGciOi..."
}
```

| Field | Description |
|-------|-------------|
| `options.publicKey.challenge` | Base64URL-encoded — decode to `ArrayBuffer` before passing to browser |
| `options.publicKey.allowCredentials` | Credentials the browser should look for. Empty if no username was provided (discoverable mode) |
| `options.publicKey.rpId` | Relying party ID — matches your `FIDO_SERVER_ID` |
| `state_token` | Signed server state — send back in verify step. Expires in 5 minutes |

### Step 2 — Get assertion in the browser

```js
const { options, state_token } = await response.json();

// Decode binary fields
options.publicKey.challenge = base64url.decode(options.publicKey.challenge);
for (let cred of options.publicKey.allowCredentials) {
    cred.id = base64url.decode(cred.id);
}

// Browser prompts user for biometric/PIN
const assertion = await navigator.credentials.get(options);

// Convert to JSON-serializable object
const assertionJSON = {
    id: assertion.id,
    rawId: base64url.encode(assertion.rawId),
    response: {
        authenticatorData: base64url.encode(assertion.response.authenticatorData),
        clientDataJSON: base64url.encode(assertion.response.clientDataJSON),
        signature: base64url.encode(assertion.response.signature),
        userHandle: assertion.response.userHandle
            ? base64url.encode(assertion.response.userHandle)
            : null,
    },
    type: assertion.type,
};
```

### Step 3 — Verify and get token

```http
POST /api/passkeys/authenticate/verify
Content-Type: application/json
```

**Request body:**

```json
{
    "state_token": "eyJhbGciOi...",
    "credential": {
        "id": "credentialIdBase64url...",
        "rawId": "credentialIdBase64url...",
        "response": {
            "authenticatorData": "SZYN5YgOjGh0NBcP...",
            "clientDataJSON": "eyJ0eXBlIjoid2ViYXV0aG4uZ2V0...",
            "signature": "MEUCIQC...",
            "userHandle": "am9obg=="
        },
        "type": "public-key"
    }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `state_token` | Yes | The token from the options step |
| `credential` | Yes | The WebAuthn assertion from `navigator.credentials.get()` |
| `credential.id` | Yes | Base64URL-encoded credential ID — used to look up the passkey |
| `credential.response.authenticatorData` | Yes | Base64URL-encoded authenticator data |
| `credential.response.clientDataJSON` | Yes | Base64URL-encoded client data |
| `credential.response.signature` | Yes | Base64URL-encoded signature |
| `credential.response.userHandle` | No | Base64URL-encoded user handle (may be null) |

**Response `200 OK` — varies by token backend:**

=== "JWT (SimpleJWT)"

    ```json
    {
        "user_id": 1,
        "username": "john",
        "token_type": "jwt",
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    ```

    Use `access` token in subsequent requests: `Authorization: Bearer <access>`

    Refresh with `POST /api/token/refresh/` when expired (standard SimpleJWT endpoint).

=== "DRF Token"

    ```json
    {
        "user_id": 1,
        "username": "john",
        "token_type": "token",
        "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
    }
    ```

    Use in subsequent requests: `Authorization: Token <token>`

=== "Session"

    ```json
    {
        "user_id": 1,
        "username": "john",
        "token_type": "session"
    }
    ```

    The session cookie is set automatically. No token needed — just use cookies.

**Error responses:**

| Status | Cause |
|--------|-------|
| `400` | Invalid or expired state token |
| `401` | Passkey authentication failed (invalid signature) |
| `404` | Credential ID not found or passkey is disabled |

---

## Complete JavaScript Example

Here's a full example using `fetch` for both registration and authentication:

```js
// ── Helper ──
function base64urlToBuffer(base64url) {
    const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
    const pad = base64.length % 4 === 0 ? '' : '='.repeat(4 - (base64.length % 4));
    const binary = atob(base64 + pad);
    return Uint8Array.from(binary, c => c.charCodeAt(0)).buffer;
}

function bufferToBase64url(buffer) {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    bytes.forEach(b => binary += String.fromCharCode(b));
    return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

// ── Register a new passkey ──
async function registerPasskey(authToken, keyName = '') {
    // Step 1: Get options
    const optionsRes = await fetch('/api/passkeys/register/options', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${authToken}` },
    });
    const { options, state_token } = await optionsRes.json();

    // Decode binary fields
    options.publicKey.challenge = base64urlToBuffer(options.publicKey.challenge);
    options.publicKey.user.id = base64urlToBuffer(options.publicKey.user.id);
    for (const cred of options.publicKey.excludeCredentials || []) {
        cred.id = base64urlToBuffer(cred.id);
    }

    // Step 2: Create credential
    const credential = await navigator.credentials.create(options);

    // Step 3: Verify
    const verifyRes = await fetch('/api/passkeys/register/verify', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            state_token,
            key_name: keyName,
            credential: {
                id: credential.id,
                rawId: bufferToBase64url(credential.rawId),
                response: {
                    clientDataJSON: bufferToBase64url(credential.response.clientDataJSON),
                    attestationObject: bufferToBase64url(credential.response.attestationObject),
                },
                type: credential.type,
            },
        }),
    });
    return await verifyRes.json(); // { id, name, enabled, platform, ... }
}

// ── Authenticate with a passkey ──
async function authenticateWithPasskey(username = null) {
    // Step 1: Get options
    const optionsRes = await fetch('/api/passkeys/authenticate/options', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(username ? { username } : {}),
    });
    const { options, state_token } = await optionsRes.json();

    // Decode binary fields
    options.publicKey.challenge = base64urlToBuffer(options.publicKey.challenge);
    for (const cred of options.publicKey.allowCredentials || []) {
        cred.id = base64urlToBuffer(cred.id);
    }

    // Step 2: Get assertion
    const assertion = await navigator.credentials.get(options);

    // Step 3: Verify
    const verifyRes = await fetch('/api/passkeys/authenticate/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            state_token,
            credential: {
                id: assertion.id,
                rawId: bufferToBase64url(assertion.rawId),
                response: {
                    authenticatorData: bufferToBase64url(assertion.response.authenticatorData),
                    clientDataJSON: bufferToBase64url(assertion.response.clientDataJSON),
                    signature: bufferToBase64url(assertion.response.signature),
                    userHandle: assertion.response.userHandle
                        ? bufferToBase64url(assertion.response.userHandle)
                        : null,
                },
                type: assertion.type,
            },
        }),
    });
    return await verifyRes.json(); // { user_id, username, token_type, ... }
}
```

**Usage:**

```js
// Register (user must be logged in)
const passkey = await registerPasskey(myAuthToken, 'My MacBook');
console.log('Registered:', passkey.name, passkey.platform);

// Authenticate (passwordless — no login needed)
const auth = await authenticateWithPasskey();
console.log('Logged in as:', auth.username);
console.log('Token:', auth.access || auth.token); // JWT or DRF Token

// Authenticate (username-assisted)
const auth2 = await authenticateWithPasskey('john');
```

---

## Passkey Management

All management endpoints require authentication.

### List all passkeys

```http
GET /api/passkeys/
Authorization: Bearer <token>
```

**Response `200 OK`:**

```json
[
    {
        "id": 1,
        "name": "My MacBook",
        "enabled": true,
        "platform": "Apple",
        "added_on": "2026-03-24T12:00:00Z",
        "last_used": "2026-03-25T09:30:00Z"
    },
    {
        "id": 2,
        "name": "Work PC",
        "enabled": true,
        "platform": "Microsoft",
        "added_on": "2026-03-20T08:00:00Z",
        "last_used": null
    }
]
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Passkey ID |
| `name` | string | User-given name or auto-detected platform |
| `enabled` | boolean | Whether this passkey can be used for login |
| `platform` | string | Detected platform: `Apple`, `Google`, `Microsoft`, `Chrome on Apple`, or `Key` |
| `added_on` | datetime | When the passkey was registered |
| `last_used` | datetime/null | Last successful authentication with this passkey |

### Retrieve a passkey

```http
GET /api/passkeys/1
Authorization: Bearer <token>
```

**Response `200 OK`:** Same shape as a single item from the list.

Returns `404` if the passkey doesn't exist or isn't owned by the authenticated user.

### Update a passkey

```http
PATCH /api/passkeys/1
Authorization: Bearer <token>
Content-Type: application/json
```

**Request body** (all fields optional):

```json
{"name": "Work Laptop", "enabled": false}
```

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | New display name |
| `enabled` | boolean | `false` to disable (passkey won't work for login), `true` to re-enable |

**Response `200 OK`:**

```json
{
    "id": 1,
    "name": "Work Laptop",
    "enabled": false,
    "platform": "Apple",
    "added_on": "2026-03-24T12:00:00Z",
    "last_used": "2026-03-25T09:30:00Z"
}
```

### Delete a passkey

```http
DELETE /api/passkeys/1
Authorization: Bearer <token>
```

**Response `204 No Content`** on success.

Returns `404` if the passkey doesn't exist or isn't owned by the authenticated user.

!!! warning
    Deleting a passkey is permanent. If the user has only one passkey and no password, they may lose access to their account.

---

## Token Backend

After successful passkey authentication, the API returns a token. The backend is auto-detected from your Django settings:

| Priority | Condition | Token type | Response fields |
|----------|-----------|------------|-----------------|
| 1 | `PASSKEYS_API_TOKEN_BACKEND` setting is set | Custom | Whatever your callable returns |
| 2 | `rest_framework_simplejwt` in `INSTALLED_APPS` | `jwt` | `access`, `refresh` |
| 3 | `rest_framework.authtoken` in `INSTALLED_APPS` | `token` | `token` |
| 4 | Fallback | `session` | (session cookie set) |

All responses always include `user_id`, `username`, and `token_type`.

### Custom Backend

If none of the built-in backends fit, create your own:

```python
# myapp/auth.py
def my_token_backend(user, request):
    """
    Custom token backend.
    Must accept (user, request) and return a dict.
    The dict is merged into the authenticate/verify response.
    """
    token = create_my_custom_token(user)
    return {
        'token_type': 'custom',
        'token': token,
        'expires_in': 3600,
    }
```

```python
# settings.py
PASSKEYS_API_TOKEN_BACKEND = 'myapp.auth.my_token_backend'
```

**Response will be:**

```json
{
    "user_id": 1,
    "username": "john",
    "token_type": "custom",
    "token": "my-custom-token-value",
    "expires_in": 3600
}
```

---

## How State Tokens Work

The API uses signed state tokens instead of sessions to carry FIDO2 state between the `options` and `verify` steps. This is what makes the API work for stateless clients.

| Property | Detail |
|----------|--------|
| **What it contains** | Serialized FIDO2 challenge state from the `fido2` library |
| **Signing** | HMAC with your Django `SECRET_KEY` via `django.core.signing` |
| **Expiry** | 5 minutes after creation |
| **Stateless** | Works with JWT/Token auth — no server-side session needed |
| **Session fallback** | Also written to session when available (backward compat with template flow) |

!!! tip "Why not just use sessions?"
    Mobile apps and SPAs using JWT don't have Django sessions. The signed state token carries the same information in the request body, so the two-step WebAuthn flow works without any server-side state.

---

## Error Handling

All error responses follow DRF's standard format:

```json
{"detail": "Error message here"}
```

| Status | When | Example |
|--------|------|---------|
| `400 Bad Request` | Validation error, expired/invalid state token | `{"detail": "Registration state has expired, please try again"}` |
| `401 Unauthorized` | Authentication failed during verify | `{"detail": "Passkey authentication failed"}` |
| `403 Forbidden` | Missing auth token on protected endpoint | `{"detail": "Authentication credentials were not provided."}` |
| `404 Not Found` | Passkey not found, disabled, or not owned by user | `{"detail": "Passkey not found or disabled"}` |
