from flask import Blueprint, render_template, session, redirect, url_for

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


@profile_bp.get("/")
def profile():
    if "user_id" not in session:
        return redirect(url_for("auth.login_get"))

    username = session.get("username")
    user_type = session.get("user_type")

    return render_template(
        "profile/profile.html", username=username, user_type=user_type
    )
