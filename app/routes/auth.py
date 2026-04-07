# Import du module regex
import re

# import de Flask et des éléments qu'on utilise (les routes, les affichages html, etc)
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)

# import d'outil pour la sécurité (hash mdp)
from werkzeug.security import check_password_hash, generate_password_hash

# import des tokens pour la réinitialisation
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

# import de l'application (base de donnée, les models de page, la config de l'appli flask)
# fonction try/except dans extensions.py
from app.extensions import db_transaction, mail
from app.models.models import User, ConnectionLog, Role
from flask import current_app
from flask_mail import Message


# Création de la route lié à l'authentification
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# Envoie vers la page de login
@auth_bp.get("/login")
def login_get():
    return render_template("auth/login.html")


# Récupère les données envoyées par le formulaire du login
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
        # Récupérer les rôles de l'utilisateur
        user_roles = [role.nameRoles for role in user.roles]
        session["user_roles"] = user_roles

        with db_transaction() as db_session:
            connexion_log = ConnectionLog(idUserForConnection=user.idUSER)
            db_session.add(connexion_log)
        # db.session.add(connexion_log)
        # db.session.commit()

        # flash(f"Bienvenue {user.username} !", "success")
        return redirect(url_for("main.home"))
    else:
        flash("Nom d'utilisateur ou mot de passe incorrect", "error")
        return render_template("auth/login.html")


# Envoie vers la page d'inscription
@auth_bp.get("/register")
def register_get():
    return render_template("auth/register.html")


# Récupère les données entrées dans le formulaire d'inscription
@auth_bp.post("/register")
def register_post():
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    password_confirm = request.form.get("password_confirm")
    # Ici est noté toutes les restrictions liées au mot de passe
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

    # Gère les vérifications pour éviter les doublons de pseudo ou email
    existing_user_by_username = User.query.filter_by(username=username).first()
    if existing_user_by_username:
        flash("Ce nom d'utilisateur est déjà utilisé", "error")
        return render_template("auth/register.html")

    existing_user_by_email = User.query.filter_by(emailUser=email).first()
    if existing_user_by_email:
        flash("Cette adresse email est déjà utilisée", "error")
        return render_template("auth/register.html")

    # Hashage du mot de passe
    hashed_password = generate_password_hash(password)

    # Ici ajout du nouvel utilisateur en base de donnée
    new_user = User(
        username=username,
        emailUser=email,
        hashpassword=hashed_password,
    )

    # Récupérer le rôle "player" et l'assigner à l'utilisateur par défaut
    player_role = Role.query.filter_by(nameRoles="player").first()
    if player_role:
        new_user.roles.append(player_role)

    # # Ajout du nouvel utilisateur à la session de la base de données (préparation)
    # db.session.add(new_user)
    # # Enregistrement définitif des modifications dans la base de données
    # db.session.commit()

    # Ajout du nouvel utilisateur à la session de la base de données
    with db_transaction() as db_session:
        db_session.add(new_user)

    flash("Compte créé avec succès ! Vous pouvez maintenant vous connecter.", "success")
    return redirect(url_for("auth.login_get"))


# Renvoi vers la page d'accueil à la déconnexion
@auth_bp.get("/logout")
def logout():
    session.clear()
    # flash("Vous avez été déconnecté avec succès", "success")
    return redirect(url_for("main.home", logout="success"))


# Génère un token lié à l'email pour réinitialiser son compte
def generate_reset_token(email):
    """Génère un token de réinitialisation sécurisé"""
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(email, salt="password-reset-salt")


# Et ici vérifie que le token ne soit pas expiré
def verify_reset_token(token, expiration=3600):
    """Vérifie un token de réinitialisation (expire après 1 heure par défaut)"""
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        email = serializer.loads(token, salt="password-reset-salt", max_age=expiration)
        return email
    except (SignatureExpired, BadSignature):
        return None


# Envoie vers la page pour réinitialiser son compte
@auth_bp.get("/forgot-password")
def forgot_password_get():
    return render_template("auth/forgot_password.html")


# Récupère les données envoyés via le formulaire de réinitialisation
@auth_bp.post("/forgot-password")
def forgot_password_post():
    email = request.form.get("email")

    if not email:
        flash("Veuillez entrer votre adresse email", "error")
        return render_template("auth/forgot_password.html")

    user = User.query.filter_by(emailUser=email).first()

    if user:
        # Générer le token de réinitialisation
        token = generate_reset_token(email)
        reset_url = url_for("auth.reset_password_get", token=token, _external=True)

        # Envoyer l'email avec le lien de réinitialisation
        try:
            msg = Message(
                subject="Réinitialisation de votre mot de passe - Cyber-hoot",
                recipients=[email],
                html=f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #0d1117; color: #c9d1d9; padding: 40px; border-radius: 8px; border: 1px solid #30363d;">
                    <h1 style="color: #58a6ff; margin-bottom: 8px;">Cyber-hoot</h1>
                    <h2 style="color: #f0f6fc; margin-bottom: 24px;">Réinitialisation de mot de passe</h2>
                    <p style="margin-bottom: 16px;">Bonjour <strong>{user.username}</strong>,</p>
                    <p style="margin-bottom: 24px;">Vous avez demandé à réinitialiser votre mot de passe. Cliquez sur le bouton ci-dessous pour choisir un nouveau mot de passe :</p>
                    <div style="text-align: center; margin: 32px 0;">
                        <a href="{reset_url}"
                           style="background-color: #58a6ff; color: #0d1117; padding: 14px 28px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 16px; display: inline-block;">
                            Réinitialiser mon mot de passe
                        </a>
                    </div>
                    <p style="margin-bottom: 8px; color: #8b949e; font-size: 14px;">Ce lien est valable pendant <strong style="color: #c9d1d9;">1 heure</strong>.</p>
                    <p style="color: #8b949e; font-size: 14px;">Si vous n'avez pas fait cette demande, ignorez simplement cet email — votre mot de passe restera inchangé.</p>
                    <hr style="border: none; border-top: 1px solid #30363d; margin: 32px 0;">
                    <p style="color: #6e7681; font-size: 12px; text-align: center;">Cyber-hoot — Plateforme de sensibilisation à la cybersécurité</p>
                </div>
                """,
            )
            mail.send(msg)
        except Exception as e:
            current_app.logger.error(f"Erreur envoi email réinitialisation à {email}: {e}")
            flash("Une erreur est survenue lors de l'envoi de l'email. Veuillez réessayer.", "error")
            return render_template("auth/forgot_password.html")

    # Ne pas révéler si l'email existe ou non (sécurité anti-énumération)
    flash(
        "Si cette adresse email est associée à un compte, un lien de réinitialisation vient d'être envoyé.",
        "success",
    )

    return redirect(url_for("auth.login_get"))


# Récupère la page de réinitialisation avec le token associé (temps défini pour réinitialiser le mdp)
@auth_bp.get("/reset-password/<token>")
def reset_password_get(token):
    # Vérifier que le token est valide
    email = verify_reset_token(token)
    if not email:
        flash("Le lien de réinitialisation est invalide ou a expiré", "error")
        return redirect(url_for("auth.forgot_password_get"))

    return render_template("auth/reset_password.html", token=token)


# Récupère les données envoyées par le formulaire de réinitialisation avec le token
# Fonctionne comme le formulaire "register" pour le mdp (même gestion de restriction pour le mpd)
@auth_bp.post("/reset-password/<token>")
def reset_password_post(token):
    # Vérifier que le token est valide
    email = verify_reset_token(token)
    if not email:
        flash("Le lien de réinitialisation est invalide ou a expiré", "error")
        return redirect(url_for("auth.forgot_password_get"))

    password = request.form.get("password")
    password_confirm = request.form.get("password_confirm")

    if not password or not password_confirm:
        flash("Veuillez remplir tous les champs", "error")
        return render_template("auth/reset_password.html", token=token)

    if password != password_confirm:
        flash("Les mots de passe ne correspondent pas", "error")
        return render_template("auth/reset_password.html", token=token)

    # Validation du mot de passe (même que pour l'inscription)
    if len(password) < 8:
        flash("Le mot de passe doit contenir au moins 8 caractères", "error")
        return render_template("auth/reset_password.html", token=token)

    if not re.search(r"[A-Z]", password):
        flash("Le mot de passe doit contenir au moins une majuscule", "error")
        return render_template("auth/reset_password.html", token=token)

    if not re.search(r"[a-z]", password):
        flash("Le mot de passe doit contenir au moins une minuscule", "error")
        return render_template("auth/reset_password.html", token=token)

    if not re.search(r"[0-9]", password):
        flash("Le mot de passe doit contenir au moins un chiffre", "error")
        return render_template("auth/reset_password.html", token=token)

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        flash("Le mot de passe doit contenir au moins un caractère spécial", "error")
        return render_template("auth/reset_password.html", token=token)

    # Trouver l'utilisateur et mettre à jour son mot de passe
    user = User.query.filter_by(emailUser=email).first()
    if not user:
        flash("Utilisateur introuvable", "error")
        return redirect(url_for("auth.forgot_password_get"))

    # Mettre à jour le mot de passe
    with db_transaction():
        user.hashpassword = generate_password_hash(password)
    # db.session.commit()

    flash(
        "Votre mot de passe a été réinitialisé avec succès. Vous pouvez maintenant vous connecter.",
        "success",
    )
    return redirect(url_for("auth.login_get"))
