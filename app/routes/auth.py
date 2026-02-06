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
from app.extensions import db_transaction
from app.models.models import User, ConnexionLog, Role
from flask import current_app


# Création de la route lié à l'authentification
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# Utilisateur admin par défaut pour le développement (ne pas utiliser en production)
DEV_ADMIN_USER = {
    "id": 0,
    "username": "AdminHoot",
    "hashpassword": "scrypt:32768:8:1$PSwKNtuaZCDoODBA$3df18ede31a2f2189d4cbf1e86e9abea8863c19f84a6b10f1e8cef1d30ac22add6187296513070ca58c4fcec37bde4c332f1b1a70cbe18334fccfffc38b1b3b6",
    "email": "admin@cyberhoot.local",
    "roles": ["admin", "creator"],
}


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

    # Vérifier d'abord l'utilisateur admin de développement
    if username == DEV_ADMIN_USER["username"] and check_password_hash(
        DEV_ADMIN_USER["hashpassword"], password
    ):
        session["user_id"] = DEV_ADMIN_USER["id"]
        session["username"] = DEV_ADMIN_USER["username"]
        session["user_roles"] = DEV_ADMIN_USER["roles"]
        return redirect(url_for("main.home"))

    # Sinon, vérifier dans la base de données
    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.hashpassword, password):
        session["user_id"] = user.idUSER
        session["username"] = user.username
        # Récupérer les rôles de l'utilisateur
        user_roles = [role.nameRoles for role in user.roles]
        session["user_roles"] = user_roles

        with db_transaction() as db_session:
            connexion_log = ConnexionLog(idUSERforConnexion=user.idUSER)
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

        # TODO: Envoyer l'email avec le lien de réinitialisation
        # Pour l'instant, afficher le lien dans la console (développement uniquement)
        print(f"Lien de réinitialisation pour {email}: {reset_url}")

        flash(
            "Si cette adresse email existe, un lien de réinitialisation a été envoyé.",
            "success",
        )
    else:
        # Ne pas révéler si l'email existe ou non (sécurité)
        flash(
            "Si cette adresse email existe, un lien de réinitialisation a été envoyé.",
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
