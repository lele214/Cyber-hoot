# import de Flask et des éléments qu'on utilise (les routes, les affichages html)
from flask import (
    Blueprint,
    render_template,
    request,
    session,
    jsonify,
    current_app,
    send_from_directory,
)
from app.extensions import db_transaction
from app.models.models import Result, Quiz, Question, Response, Media
from app.decorators import login_required
from datetime import date
import os

# Création de la route principale de l'application
main_bp = Blueprint("main", __name__)


# Envoie vers la page d'accueil
@main_bp.get("/")
def home():
    return render_template("index.html")


# Envoie vers la page listant tous les quiz
@main_bp.get("/quiz")
def quiz():
    # Récupère tous les quiz publiés depuis la base de données
    published_quizzes = Quiz.query.filter_by(statut="PUBLISHED").all()
    quizzes_data = [
        {
            "id": q.idQUIZ,
            "title": q.title,
            "difficulty": q.difficulty,
            "category": q.category,
        }
        for q in published_quizzes
    ]
    return render_template("quiz/quiz.html", published_quizzes=quizzes_data)


# Envoie vers la page d'un quiz spécifique en fonction de son ID
@main_bp.get("/quiz/<int:quiz_id>")
def quiz_detail(quiz_id):
    # Vérifie d'abord si un template statique existe (quiz historiques)
    template_path = os.path.join(
        current_app.template_folder, f"quiz/quiz{quiz_id}.html"
    )
    if os.path.exists(template_path):
        return render_template(f"quiz/quiz{quiz_id}.html")

    # Sinon, charge le quiz dynamiquement depuis la base de données
    quiz = Quiz.query.get_or_404(quiz_id)

    # Prépare les questions et réponses
    questions_data = []
    correct_answers = {}
    for i, question in enumerate(quiz.questions):
        responses = []
        for j, response in enumerate(question.responses):
            resp_media = Media.query.filter_by(
                idMediaFromResponse=response.idRESPONSE
            ).first()
            responses.append(
                {
                    "index": j,
                    "text": response.responseText,
                    "media_id": resp_media.idMEDIA if resp_media else None,
                }
            )
            if response.isCorrect:
                correct_answers[f"q{i}"] = str(j)
        q_medias = Media.query.filter_by(idMediaFromQuestion=question.idQUESTION).all()
        image_media = next((m for m in q_medias if m.mediaType != "link"), None)
        link_media = next((m for m in q_medias if m.mediaType == "link"), None)
        questions_data.append(
            {
                "index": i,
                "text": question.QuestionText,
                "responses": responses,
                "media_id": image_media.idMEDIA if image_media else None,
                "link_url": link_media.mediaUrl if link_media else None,
                "link_label": link_media.mediaLabel if link_media else None,
            }
        )

    return render_template(
        "quiz/quiz_dynamic.html",
        quiz=quiz,
        questions_data=questions_data,
        correct_answers=correct_answers,
    )


# Route protégée pour servir les images uploadées (hors de static/)
@main_bp.get("/media/<int:media_id>")
@login_required
def serve_media(media_id):
    media = Media.query.get_or_404(media_id)
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    # mediaUrl contient juste le nom du fichier (ex: "abc123.jpg")
    return send_from_directory(upload_folder, media.mediaUrl)


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

    # Récupérer les réponses soumises
    data = request.get_json()
    answers = data.get("answers", {})
    score = data.get("score", 0)
    total_questions = data.get("totalQuestions", 0)

    try:
        # Vérifier si le quiz existe dans la base de données
        quiz = Quiz.query.filter_by(idQUIZ=quiz_id).first()
        if not quiz:
            return jsonify(
                {"success": False, "error": "Quiz non trouvé dans la base de données"}
            ), 404

        # Récupérer l'ID de l'utilisateur depuis la session
        user_id = session.get("user_id")

        # Créer un nouveau résultat dans la base de données
        new_result = Result(
            idQUIZinResult=quiz_id,
            idUSERinResult=user_id,
            date=date.today(),
            score=score,
            totalQuestions=total_questions,
            # resultHistory=str(answers),
            answer=str(answers),  # Stocker les réponses en format texte
        )

        # Ajouter et enregistrer le résultat
        # db.session.add(new_result)
        # db.session.commit()
        with db_transaction() as db_session:
            db_session.add(new_result)

        return jsonify(
            {
                "success": True,
                "message": "Quiz validé avec succès",
                "score": score,
                "totalQuestions": total_questions,
            }
        ), 200

    except Exception as e:
        # En cas d'erreur, annuler les changements
        # db.session.rollback() //déjà fait dans db_transaction
        return jsonify(
            {
                "success": False,
                "error": f"Erreur lors de l'enregistrement du résultat: {str(e)}",
            }
        ), 500
