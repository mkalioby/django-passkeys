# Use of Example project

1. Create virtual env
   ```
   python -m venv venv
   ```
2. Activate env
   ```
   source venv/bin/activate
   ```
3. Install requirements
   ```
   pip install -r requirements.txt
   ```
4. cd to example project
   ```
   cd example
   ```
5. Run migrations
   ```
   python manage.py migrate
   ```
6. Create super user
   ```
   python manage.py createsuperuser
   ```
7. Start the server
   ```
   python manage.py runserver
   ```
8. Open `http://localhost:8000/` in your browser

   **Important**: Use `localhost` not `127.0.0.1` — WebAuthn requires the domain to match `FIDO_SERVER_ID` in settings.

# Notes for SSL

For passkeys in production, you need to use HTTPS. After the above steps are done:

1. Stop the server
2. Install SSL requirements
   ```
   pip install django-sslserver
   ```
3. Start the SSL server
   ```
   python manage.py runsslserver
   ```
