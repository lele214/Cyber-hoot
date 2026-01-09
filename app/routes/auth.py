import re
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from werkzeug.security import check_password_hash, generate_password_hash
from app.database import db
from app.models.models import User, ConnexionLog

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.get("/login")
def login_get():
    return render_template("auth/login.html")


@auth_bp.post("/login")
def login_post():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        flash("Veuillez remplir tous les champs", "error")
        return render_template("auth/login.html")

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.hashpassword, password):
        session["user_id"] = user.idUSER
        session["username"] = user.username
        session["user_type"] = user.typeUser

        connexion_log = ConnexionLog(idUSERforConnexion=user.idUSER)
        db.session.add(connexion_log)
        db.session.commit()

        # flash(f"Bienvenue {user.username} !", "success")
        return redirect(url_for("main.home"))
    else:
        flash("Nom d'utilisateur ou mot de passe incorrect", "error")
        return render_template("auth/login.html")


@auth_bp.get("/register")
def register_get():
    return render_template("auth/register.html")


@auth_bp.post("/register")
def register_post():
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    password_confirm = request.form.get("password_confirm")

    if not email or not username or not password or not password_confirm:
        flash("Veuillez remplir tous les champs", "error")
        return render_template("auth/register.html")

    if password != password_confirm:
        flash("Les mots de passe ne correspondent pas", "error")
        return render_template("auth/register.html")

    if len(password) < 8:
        flash("Le mot de passe doit contenir au moins 8 caractères", "error")
        return render_template("auth/register.html")

    if not re.search(r"[A-Z]", password):
        flash("Le mot de passe doit contenir au moins une majuscule", "error")
        return render_template("auth/register.html")

    if not re.search(r"[a-z]", password):
        flash("Le mot de passe doit contenir au moins une minuscule", "error")
        return render_template("auth/register.html")

    if not re.search(r"[0-9]", password):
        flash("Le mot de passe doit contenir au moins un chiffre", "error")
        return render_template("auth/register.html")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        flash("Le mot de passe doit contenir au moins un caractère spécial", "error")
        return render_template("auth/register.html")

    existing_user_by_username = User.query.filter_by(username=username).first()
    if existing_user_by_username:
        flash("Ce nom d'utilisateur est déjà utilisé", "error")
        return render_template("auth/register.html")

    existing_user_by_email = User.query.filter_by(emailUser=email).first()
    if existing_user_by_email:
        flash("Cette adresse email est déjà utilisée", "error")
        return render_template("auth/register.html")

    hashed_password = generate_password_hash(password)
    new_user = User(
        username=username,
        emailUser=email,
        hashpassword=hashed_password,
        typeUser="Player",
    )

    db.session.add(new_user)
    db.session.commit()

    flash("Compte créé avec succès ! Vous pouvez maintenant vous connecter.", "success")
    return redirect(url_for("auth.login_get"))


@auth_bp.get("/logout")
def logout():
    session.clear()
    # flash("Vous avez été déconnecté avec succès", "success")
    return redirect(url_for("main.home", logout="success"))
