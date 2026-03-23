## 1.4.0
* Fix: Change the hardcoded username field.
* Fix: Change Grammar for empty keys cases.
* Fix: Show user provided key name when deleting key.
* Added: Django 6.0 tests
* Added: Python 3.14 to tests
* Upgraded fido2 to v2.1.0
* Moved DELETE key to be POST request
* Fixed some typos

   Thanks to @ganiyevuz & ashokdelphia for his contribution in this release.

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