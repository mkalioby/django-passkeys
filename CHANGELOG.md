## v2.0.0

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

* `FIDO_SERVER_ID` and `FIDO_SERVER_NAME` call be callable now to multi tenants application

   Thanks for [jacopsd](https://github.com/jacopsd)   
* Fix: Issue while encoding PublicKeyCredentials.
* Fix: Add check that the key is enabled.
   
    Thanks for [gasparbrogueira](https://github.com/gasparbrogueira)

## v1.0
* Upgraded fido2 to v1.1.1
* Initial Production Release