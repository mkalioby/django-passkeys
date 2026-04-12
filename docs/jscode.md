## Complete JavaScript Example

!!! info
    - For an example for key management and registering new key , check [mange.html](https://github.com/mkalioby/django-passkeys/blob/v2.0/example/test_app/templates/rest/manage.html)
    - For a login example using the API, check [login.html](https://github.com/mkalioby/django-passkeys/blob/v2.0/example/test_app/templates/rest/login.html)


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
