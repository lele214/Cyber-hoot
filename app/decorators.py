from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    """Vérifie que l'utilisateur est connecté, sinon redirige vers le login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.login_get"))
        return f(*args, **kwargs)
    return decorated_function


def role_required(role_name):
    """Vérifie que l'utilisateur possède le rôle demandé, sinon redirige vers l'accueil."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_roles = session.get("user_roles", [])
            if role_name not in user_roles:
                flash(f"Accès refusé : réservé aux {role_name}s", "error")
                return redirect(url_for("main.home"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
