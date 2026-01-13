# import de Flask et des éléments qu'on utilise (les routes, les affichages html, la session, les redirections, les messages flash)
from flask import Blueprint, render_template, session, redirect, url_for, flash

# Création de la route liée aux profils utilisateurs
profile_bp = Blueprint("profile", __name__, url_prefix="/profile")


## POUR PROTEGER LES ROUTES :
# Regarder du côté des "Décorateurs" sur Flask


# Envoie vers la page de profil par défaut (redirige automatiquement vers le profil Player)
@profile_bp.get("/")
def profile():
    # Vérifie si l'utilisateur est connecté en cherchant son ID dans la session
    if "user_id" not in session:
        return redirect(url_for("auth.login_get"))

    # Rediriger par défaut vers le profil Player
    return redirect(url_for("profile.player_dashboard"))


# Envoie vers la page du tableau de bord administrateur
@profile_bp.get("/admin")
def admin_dashboard():
    # Vérifie si l'utilisateur est connecté
    if "user_id" not in session:
        return redirect(url_for("auth.login_get"))

    # Récupère les rôles de l'utilisateur depuis la session
    user_roles = session.get("user_roles", [])
    # Vérifie si l'utilisateur possède le rôle "Admin"
    if "Admin" not in user_roles:
        flash("Accès refusé : réservé aux administrateurs", "error")
        return redirect(url_for("main.home"))

    # Récupère le nom d'utilisateur depuis la session
    username = session.get("username")
    # Affiche le template du dashboard admin avec les données de l'utilisateur
    return render_template("profile/admin/admin_dashboard.html", username=username, user_roles=user_roles)


# Envoie vers la page du tableau de bord rédacteur
@profile_bp.get("/redactor")
def redactor_dashboard():
    # Vérifie si l'utilisateur est connecté
    if "user_id" not in session:
        return redirect(url_for("auth.login_get"))

    # Récupère les rôles de l'utilisateur depuis la session
    user_roles = session.get("user_roles", [])
    # Vérifie si l'utilisateur possède le rôle "Redactor"
    if "Redactor" not in user_roles:
        flash("Accès refusé : réservé aux rédacteurs", "error")
        return redirect(url_for("main.home"))

    # Récupère le nom d'utilisateur depuis la session
    username = session.get("username")
    # Affiche le template du dashboard rédacteur avec les données de l'utilisateur
    return render_template(
        "profile/redactor/redactor_dashboard.html", username=username, user_roles=user_roles
    )


# Envoie vers la page du tableau de bord joueur
@profile_bp.get("/player")
def player_dashboard():
    # Vérifie si l'utilisateur est connecté
    if "user_id" not in session:
        return redirect(url_for("auth.login_get"))

    # Récupère le nom d'utilisateur et les rôles depuis la session
    username = session.get("username")
    user_roles = session.get("user_roles", [])
    # Affiche le template du dashboard joueur avec les données de l'utilisateur
    return render_template("profile/player/player_dashboard.html", username=username, user_roles=user_roles)
