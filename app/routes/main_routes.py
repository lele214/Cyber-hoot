# import de Flask et des éléments qu'on utilise (les routes, les affichages html)
from flask import Blueprint, render_template

# Création de la route principale de l'application
main_bp = Blueprint("main", __name__)


# Envoie vers la page d'accueil
@main_bp.get("/")
def home():
    return render_template("index.html")


# Envoie vers la page listant tous les quiz
@main_bp.get("/quiz")
def quiz():
    return render_template("quiz/quiz.html")


# Envoie vers la page d'un quiz spécifique en fonction de son ID
@main_bp.get("/quiz/<int:quiz_id>")
def quiz_detail(quiz_id):
    # Vérifie que l'ID du quiz existe (entre 1 et 8)
    if quiz_id < 1 or quiz_id > 8:
        return "Quiz non trouvé", 404

    # Affiche le template du quiz correspondant à l'ID
    return render_template(f"quiz/quiz{quiz_id}.html")
