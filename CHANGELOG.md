## 2.1

* Fixes: #72, #73 and #74. Thanks to @red-one1
* Added `PASSKEYS_ALLOW_EMPTY_REQUEST` default False to allow request to be `None`, useful when using multiple authentication backends.
* Added `PASSKEYS_ALLOW_NO_PASSKEY_FIELD` default False to allow request not to have a `passkey` field, useful when using multiple authentication backends.
* Upgraded fido2 to v2.2.0


## 2.0.0
* Breaking Change: Moved templates to `passkeys` folder and renamed the templates. thanks to @ganiyevuz and @smark-1 
  * `PassKeys.html` -> `passkeys/manage.html`
  * `PassKeys_base.html` -> `passkeys/base.html`
  * `check_passkeys.js` -> `passkeys/check.js`
  * `passkeys.js` -> `passkeys/passkeys.js`
  * `modal.html` -> `passkeys/modal.html`
* Dropped Support for django-2.0, django-2.1, django-4.0, django-4.1, django-5.0, django-5.1, but not django 2.2, 3.2.
* New: DRF API module (`passkeys.api`) — REST endpoints for passkey registration, authentication, and management
* New: Pluggable token backend — auto-detects SimpleJWT, DRF TokenAuth, or session-based auth
* New: Service layer (`passkeys.api.service`) — session-independent FIDO2 logic with signed state tokens
* New: Optional install via `pip install django-passkeys[drf]` or `pip install django-passkeys[drf-jwt]`
* Added: Support for Google new WebAuthn immediate mediation API (with allow/disallow password login) for Chromium Browser. for more details check [Google's announcement](https://developer.chrome.com/blog/webauthn-immediate-mediation-ot).
* Fix: add `@login required` to passkey registration views. thanks to @rafaelurbeno for reporting the issue.
* New: Add docs and hosted on [readthedocs.io](https://django-passkeys.readthedocs.io/en/v2.0/)
* Example app updated to show case template, rest framework integration and WebAuthn immediate mediation API


## 1.4.1
* Add csrfmiddlwwaretoken to deleteKey and toggle key.

## 1.4.0
* Fix: Change the hardcoded username field.
* Fix: Change Grammar for empty keys cases.
* Fix: Show user provided key name when deleting key.
* Cast Uint8Array objects to base64url encoding when preparing the payload so fido2 knows how to process it.
* Added: Django 6.0 tests
* Added: Python 3.14 to tests
* Upgraded fido2 to v2.1.0
* Moved DELETE key to be POST request
* Fixed some typos

   Thanks to @ashokdelphia, @offbyone, @resba & @ganiyevuz &  for his contribution in this release.

## v1.3.0

* Added Django 5.1, Django 5.2 to tests
* Added: Python 3.12, Python 3.13 to tests
* Upgrade fido2 to v2.0.0

## v1.2.7

* Fix: issue if the user isn't defined by username field #25.

## v1.2.6

* Adding Django 5.0 to test matrix and pypi classifiers

## 1.2.5

* Fix: Aborting the conditional UI was not working when 'Login by Passkeys' is clicked.


## v1.2.4

* No Change just updating README.md

## v1.2.3

* No Change just updating README.md

## v1.2.1.1

* Allow aborting the conditionalUI.

## v1.2

* Add support for Conditional UI.

## v1.1

* `FIDO_SERVER_ID` and `FIDO_SERVER_NAME` can be callable now for multi-tenant applications.

   Thanks to [jacopsd](https://github.com/jacopsd)   
* Fix: Issue while encoding PublicKeyCredentials.
* Fix: Add check that the key is enabled.
   
    Thanks to [gasparbrogueira](https://github.com/gasparbrogueira)

## v1.0
* Upgraded fido2 to v1.1.1
* Initial Production Release
