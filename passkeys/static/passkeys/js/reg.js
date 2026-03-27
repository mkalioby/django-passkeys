var MakeCredReq = (makeCredReq) => {
    makeCredReq.publicKey.challenge = base64url.decode(makeCredReq.publicKey.challenge);
    makeCredReq.publicKey.user.id = base64url.decode(makeCredReq.publicKey.user.id);

    for (let excludeCred of makeCredReq.publicKey.excludeCredentials) {
        excludeCred.id = base64url.decode(excludeCred.id);
    }

    return makeCredReq
}

async function get_new_credentials(data) {
    options = MakeCredReq(data)
    try {
        key_data = await navigator.credentials.create(options)
        return publicKeyCredentialToJSON(key_data)
    }
    catch (e) {
        console.error(e)
        throw e
    }
}
