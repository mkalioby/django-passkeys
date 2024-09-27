## 2.0

This is backward incompatible version, as the templates moved to `passkeys` folder
and the names are lowercase now. please check the README.md for more details.

* Upgraded the FIDO2 dependency to be >1.1.1.
* Added `login_required` to some functions
* `delKey` accepts POST now not GET.

Thanks for [smark-1](https://github.com/smark-1) and [rafaelurben](https://github.com/rafaelurben) for the work done in the release 
 


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