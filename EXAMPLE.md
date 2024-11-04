# Use of Example project


## Notes for SSL

For passkeys, you need to use HTTPS, you can use a service like ngrok which creates a tunnel to your host.

Ask your IT department for permission beforehand.

Alternatively you can use django-sslserver.


## Setup

**run ngrok**

```shell
ngrok http 8000
```


**create virtual env**

```shell
virtualenv venv
```

**activate env** 

```shell
source venv/bin/activate
```

**install requirements** 

```shell
pip install -e .
```

**Change directory to example project**

```shell
cd example
```

**create .env file**

Check the ngrok output for the assigned hostname.

```
DJANGO_PASSKEY_HOST = ?.ngrok-free.app
```

**Run django migrations**

```shell
python manage.py migrate
```

**Create super user** 

```shell
python manage.py createsuperuser
```

**Start the django development server**

```python manage.py runserver```
