# import de Flask et des éléments qu'on utilise (les routes, les affichages html)
from flask import Blueprint, render_template, request, session, jsonify
from app.database import db
from app.models.models import Result, Quiz
from datetime import date

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


# Route pour soumettre un quiz (nécessite d'être connecté)
@main_bp.post("/quiz/<int:quiz_id>/submit")
def quiz_submit(quiz_id):
    # Vérifier que l'utilisateur est connecté
    if "user_id" not in session:
        return jsonify(
            {
                "success": False,
                "error": "Vous devez être connecté pour valider le quiz",
                "redirect": "/auth/login",
            }
        ), 401

    # Vérifier que l'ID du quiz existe (entre 1 et 8)
    if quiz_id < 1 or quiz_id > 8:
        return jsonify({"success": False, "error": "Quiz non trouvé"}), 404

    # Récupérer les réponses soumises
    data = request.get_json()
    answers = data.get("answers", {})
    score = data.get("score", 0)
    total_questions = data.get("totalQuestions", 0)

    try:
        # Vérifier si le quiz existe dans la base de données
        quiz = Quiz.query.filter_by(idQUIZ=quiz_id).first()
        if not quiz:
            return jsonify({"success": False, "error": "Quiz non trouvé dans la base de données"}), 404

        # Récupérer l'ID de l'utilisateur depuis la session
        user_id = session.get("user_id")

        # Créer un nouveau résultat dans la base de données
        new_result = Result(
            idQUIZinResult=quiz_id,
            idUSERinResult=user_id,
            date=date.today(),
            score=score,
            totalQuestions=total_questions,
            resultHistory=str(answers)  # Stocker les réponses en format texte
        )

        # Ajouter et enregistrer le résultat
        db.session.add(new_result)
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": "Quiz validé avec succès",
                "score": score,
                "totalQuestions": total_questions
            }
        ), 200

    except Exception as e:
        # En cas d'erreur, annuler les changements
        db.session.rollback()
        return jsonify(
            {
                "success": False,
                "error": f"Erreur lors de l'enregistrement du résultat: {str(e)}"
            }
        ), 500
