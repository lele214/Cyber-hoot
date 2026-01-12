from flask import Blueprint, render_template, session, redirect, url_for, flash

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


## POUR PROTEGER LES ROUTES :
# Regarder du côté des "Décorateurs" sur Flask


@profile_bp.get("/")
def profile():
    if "user_id" not in session:
        return redirect(url_for("auth.login_get"))

    # Rediriger par défaut vers le profil Player
    return redirect(url_for("profile.player_dashboard"))


@profile_bp.get("/admin")
def admin_dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login_get"))

    user_roles = session.get("user_roles", [])
    if "Admin" not in user_roles:
        flash("Accès refusé : réservé aux administrateurs", "error")
        return redirect(url_for("main.home"))

    username = session.get("username")
    return render_template("profile/admin/admin_dashboard.html", username=username, user_roles=user_roles)


@profile_bp.get("/redactor")
def redactor_dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login_get"))

    user_roles = session.get("user_roles", [])
    if "Redactor" not in user_roles:
        flash("Accès refusé : réservé aux rédacteurs", "error")
        return redirect(url_for("main.home"))

    username = session.get("username")
    return render_template(
        "profile/redactor/redactor_dashboard.html", username=username, user_roles=user_roles
    )


@profile_bp.get("/player")
def player_dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login_get"))

    username = session.get("username")
    user_roles = session.get("user_roles", [])
    return render_template("profile/player/player_dashboard.html", username=username, user_roles=user_roles)
