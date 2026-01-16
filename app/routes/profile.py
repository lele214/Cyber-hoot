# import de Flask et des éléments qu'on utilise (les routes, les affichages html, la session, les redirections, les messages flash)
from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.models.models import Result, Quiz, User
from app.database import db
from sqlalchemy import func

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
    # Vérifie si l'utilisateur possède le rôle "admin"
    if "admin" not in user_roles:
        flash("Accès refusé : réservé aux administrateurs", "error")
        return redirect(url_for("main.home"))

    # Récupère le nom d'utilisateur depuis la session
    username = session.get("username")
    # Affiche le template du dashboard admin avec les données de l'utilisateur
    return render_template("profile/admin/admin_dashboard.html", username=username, user_roles=user_roles)


# Envoie vers la page du tableau de bord créateur
@profile_bp.get("/creator")
def creator_dashboard():
    # Vérifie si l'utilisateur est connecté
    if "user_id" not in session:
        return redirect(url_for("auth.login_get"))

    # Récupère les rôles de l'utilisateur depuis la session
    user_roles = session.get("user_roles", [])
    # Vérifie si l'utilisateur possède le rôle "creator"
    if "creator" not in user_roles:
        flash("Accès refusé : réservé aux créateurs", "error")
        return redirect(url_for("main.home"))

    # Récupère le nom d'utilisateur depuis la session
    username = session.get("username")
    # Affiche le template du dashboard créateur avec les données de l'utilisateur
    return render_template(
        "profile/creator/creator_dashboard.html", username=username, user_roles=user_roles
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
    user_id = session.get("user_id")

    # Récupérer les statistiques de l'utilisateur
    # 1. Nombre total de quiz disponibles (publiés)
    total_quizzes = Quiz.query.filter_by(statut='PUBLISHED').count()

    # 2. Récupérer tous les résultats de l'utilisateur avec les informations du quiz
    user_results = db.session.query(
        Result, Quiz
    ).join(
        Quiz, Result.idQUIZinResult == Quiz.idQUIZ
    ).filter(
        Result.idUSERinResult == user_id
    ).order_by(
        Result.date.desc()
    ).all()

    # 3. Calculer les statistiques
    completed_quizzes = len(user_results)
    remaining_quizzes = total_quizzes - completed_quizzes

    # 4. Calculer le score moyen
    if completed_quizzes > 0:
        total_score = sum((result.score / result.totalQuestions * 100) for result, quiz in user_results if result.totalQuestions > 0)
        average_score = round(total_score / completed_quizzes, 1)
    else:
        average_score = 0

    # 5. Formater les résultats pour l'affichage
    quiz_history = []
    for result, quiz in user_results:
        if result.totalQuestions > 0:
            percentage = round((result.score / result.totalQuestions) * 100)
        else:
            percentage = 0

        quiz_history.append({
            'quiz_title': quiz.title,
            'quiz_difficulty': quiz.difficulty,
            'score': result.score,
            'total_questions': result.totalQuestions,
            'percentage': percentage,
            'date': result.date.strftime('%d/%m/%Y') if result.date else 'N/A'
        })

    # Affiche le template du dashboard joueur avec les données de l'utilisateur
    return render_template(
        "profile/player/player_dashboard.html",
        username=username,
        user_roles=user_roles,
        total_quizzes=total_quizzes,
        completed_quizzes=completed_quizzes,
        remaining_quizzes=remaining_quizzes,
        average_score=average_score,
        quiz_history=quiz_history
    )
