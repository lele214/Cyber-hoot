from flask import Blueprint, render_template, session, redirect, url_for, flash

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


## POUR PROTEGER LES ROUTES :
# Regarder du côté des "Décorateurs" sur Flask


@profile_bp.get("/")
def profile():
    if "user_id" not in session:
        return redirect(url_for("auth.login_get"))

    user_type = session.get("user_type")

    if user_type == "Admin":
        return redirect(url_for("profile.admin_dashboard"))
    elif user_type == "Redactor":
        return redirect(url_for("profile.redactor_dashboard"))
    else:
        return redirect(url_for("profile.player_dashboard"))


@profile_bp.get("/admin")
def admin_dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login_get"))

    if session.get("user_type") != "Admin":
        flash("Accès refusé : réservé aux administrateurs", "error")
        return redirect(url_for("main.home"))

    username = session.get("username")
    return render_template("profile/admin/admin_dashboard.html", username=username)


@profile_bp.get("/redactor")
def redactor_dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login_get"))

    if session.get("user_type") != "Redactor":
        flash("Accès refusé : réservé aux rédacteurs", "error")
        return redirect(url_for("main.home"))

    username = session.get("username")
    return render_template(
        "profile/redactor/redactor_dashboard.html", username=username
    )


@profile_bp.get("/player")
def player_dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login_get"))

    username = session.get("username")
    return render_template("profile/player/player_dashboard.html", username=username)
