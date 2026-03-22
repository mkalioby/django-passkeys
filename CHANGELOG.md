## v1.4.0

* **Breaking**: Minimum Python version is now 3.10 (dropped 3.7, 3.8, 3.9)
* **Breaking**: Minimum Django version is now 4.2 (dropped 2.x, 3.x, 4.0, 4.1)
* **Breaking**: `del_key` and `toggle_key` views now require POST instead of GET
* Added Django 6.0 support
* Added Python 3.14 support
* Dropped Django 5.0 (EOL)
* Security: State-changing operations (delete, toggle) now enforce POST with CSRF protection
* Security: Backend raises `SuspiciousOperation` instead of generic `Exception`
* Performance: `auth_complete` uses single query (`.first()`) instead of two (`exists()` + `[0]`)
* Performance: `save(update_fields=[...])` for partial updates instead of full model save
* Performance: Added composite index on `(credential_id, enabled)`
* Performance: `getUserCredentials` uses `.only('token')` to fetch only needed column
* Fixed: Inverted error messages in ownership checks ("You own" → "You don't own")
* Fixed: `delKey` view had no 404 handling for missing keys
* Fixed: Template referenced non-existent `key.key_type` attribute
* Model: Use `settings.AUTH_USER_MODEL` instead of `get_user_model()` at class level
* Model: Added `__str__`, `verbose_name`, `ordering`, `related_name`
* Model: Added `BigAutoField` as `default_auto_field`
* Code: Renamed all functions to PEP 8 snake_case (`getUserCredentials` → `get_user_credentials`, etc.)
* Code: Removed unused imports (`RegistrationResponse`, `PASSWORD_HASHERS`)
* Code: `enable_json_mapping()` called once at module load instead of per-request
* Code: Modernized settings to use `pathlib.Path` instead of `os.path`
* Code: Removed deprecated `USE_L10N` setting
* **Breaking**: Renamed `FIDO2.py` → `webauthn.py` (update imports: `from passkeys.webauthn import ...`)
* **Breaking**: Templates moved to `passkeys/` namespace (`PassKeys.html` → `passkeys/manage.html`, `PassKeys_base.html` → `passkeys/base.html`, `passkeys.js` → `passkeys/login.js`, `check_passkeys.js` → `passkeys/check.js`)
* Code: Cleaned up JS templates — consistent indentation, `const`/`let`, proper semicolons
* CI: Updated GitHub Actions to v4/v5

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

* `FIDO_SERVER_ID` and `FIDO_SERVER_NAME` can be callable now for multi-tenant applications

   Thanks to [jacopsd](https://github.com/jacopsd)
* Fix: Issue while encoding PublicKeyCredentials.
* Fix: Add check that the key is enabled.

    Thanks to [gasparbrogueira](https://github.com/gasparbrogueira)

## v1.0
* Upgraded fido2 to v1.1.1
* Initial Production Release
