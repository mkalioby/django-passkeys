# Template-Based Setup

This guide covers the Django template integration. Complete the [Common Setup](index.md#common-setup) first.

## 1. Add URLs

```python
from django.urls import path, include

urlpatterns = [
    ...
    path('passkeys/', include('passkeys.urls')),
]
```

## 2. Collect Static Files

```bash
python manage.py collectstatic
```

## 3. Update Your Login View

Pass `request` to `authenticate()`:

```python
from django.contrib.auth import authenticate, login

def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"],
        )
        if user:
            login(request, user)
            return redirect("home")
    return render(request, "login.html")
```

## 4. Update Your Login Template

Add a hidden input and passkey button inside your login form:

```html
<form method="post" id="loginForm">
    {% csrf_token %}
    <input type="text" name="username" autocomplete="username webauthn">
    <input type="password" name="password">

    <!-- Passkey support -->
    <input type="hidden" name="passkeys" id="passkeys"/>
    <button type="button" class="btn btn-dark" onclick="authn('loginForm')">
        <img src="{% static 'passkeys/imgs/FIDO-Passkey_Icon-White.png' %}" style="width: 24px">
        Login with Passkey
    </button>

    {% include 'passkeys.js' %}
    <button type="submit">Login</button>
</form>
```

!!! note
    The form must have an `id` attribute. Pass this id to `authn()`.

## 5. Add Passkey Management Link

Let users manage their passkeys from your app:

```html
<a href="{% url 'passkeys:home' %}">Manage Passkeys</a>
```

## Template Customization

The management UI uses `PassKeys_base.html` which extends your `base.html`. It requires blocks named `head` and `content`.

To customize styling, override `PassKeys_base.html` in your own templates directory.

!!! info "Requirements"
    The built-in templates require jQuery and Bootstrap.

## Detect Passkey Usage

After login, check `request.session['passkey']`:

```python
# User logged in with a passkey
request.session['passkey']
# {'passkey': True, 'name': 'Chrome', 'id': 2, 'platform': 'Chrome on Apple', 'cross_platform': False}

# User logged in with password
request.session['passkey']
# {'passkey': False}
```

`cross_platform` is `True` when the user authenticated from a different platform than where the key was registered (e.g. Android phone used on Mac).

## Enrollment Prompt

Show a prompt to users whose devices support passkeys:

```html
<div id="pk" class="alert alert-info" style="display: none">
    Your device supports passkeys, <a href="{% url 'passkeys:enroll' %}">Enroll</a>
</div>
<script>
function register_pk() { $('#pk').show(); }
{% include 'check_passkeys.js' %}
$(document).ready(check_passkey(true, register_pk))
</script>
```

| Parameter | Description |
|-----------|-------------|
| `platform_authenticator` | `true` to require platform authenticator (TouchID, Windows Hello) |
| `success_func` | Called when a platform authenticator is available |
| `fail_func` | Called when no platform authenticator is found (optional) |

## Conditional UI

Browsers can prompt passkey login directly in the username field:

![Conditional UI](https://raw.githubusercontent.com/mkalioby/django-passkeys/main/imgs/conditionalUI.png)

1. Add `webauthn` to the username autocomplete:
   ```html
   <input name="username" placeholder="username" autocomplete="username webauthn">
   ```

2. Initialize on page load:
   ```js
   window.onload = checkConditionalUI('loginForm');
   ```
