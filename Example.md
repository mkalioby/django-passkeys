# Use of Example project

1. create virtual env: python -mvenv .venv
1. activate env `source .venv/bin/activate`
1. install requirements `python -mpip install -r requirements.txt`
1. cd to example project `cd example`
1. migrate `python manage.py migrate`
1. create super user `python manage.py createsuperuser`
1. start the server `python manage.py runserver`

# Notes for SSL

For passkeys, you need to use HTTPS, after the above steps are done:

1. stop the server
1. install requirements `python -mpip install -r example-ssl-requirements.txt`
1. start the ssl server `python manage.py runsslserver`
1. visit https://localhost:8000/ -- using `https://127.0.0.1:8000` will not work!
