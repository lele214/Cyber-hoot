# import de Flask et des éléments qu'on utilise (les routes, les affichages html)
from flask import (
    Blueprint,
    render_template,
    request,
    session,
    jsonify,
    current_app,
    send_from_directory,
    redirect,
    url_for,
    flash,
)
from app.extensions import db, db_transaction
from app.models.models import Result, Quiz, Question, Response, Media, Review
from app.services.badge_service import award_score_badges, award_review_badges
from app.decorators import login_required
from datetime import date
from sqlalchemy import func
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

    # Récupère les notes moyennes et le nombre d'avis par quiz
    avg_ratings = {
        r[0]: round(r[1], 1)
        for r in db.session.query(Review.idQUIZinReview, func.avg(Review.rating))
        .group_by(Review.idQUIZinReview)
        .all()
    }
    review_counts = {
        r[0]: r[1]
        for r in db.session.query(Review.idQUIZinReview, func.count(Review.idREVIEW))
        .group_by(Review.idQUIZinReview)
        .all()
    }

    quizzes_data = [
        {
            "id": q.idQUIZ,
            "title": q.title,
            "difficulty": q.difficulty,
            "category": q.category,
            "avg_rating": avg_ratings.get(q.idQUIZ),
            "review_count": review_counts.get(q.idQUIZ, 0),
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
                "explanation": question.explanation,
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

        # Attribution automatique des badges
        new_badges = award_score_badges(
            user_id=user_id,
            quiz_id=quiz_id,
            score=score,
            total_questions=total_questions,
        )
        badges_earned = [
            {"name": b.name, "icon": b.icon, "description": b.description}
            for b in new_badges
        ]

        return jsonify(
            {
                "success": True,
                "message": "Quiz validé avec succès",
                "score": score,
                "totalQuestions": total_questions,
                "badges_earned": badges_earned,
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


# Formulaire pour laisser un avis sur un quiz
@main_bp.route("/quiz/<int:quiz_id>/review", methods=["GET", "POST"])
@login_required
def quiz_review(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    user_id = session.get("user_id")

    # Vérifie que l'utilisateur a bien complété ce quiz
    has_completed = Result.query.filter_by(
        idQUIZinResult=quiz_id, idUSERinResult=user_id
    ).first()
    if not has_completed:
        flash("Vous devez d'abord compléter ce quiz pour laisser un avis.", "error")
        return redirect(url_for("main.quiz_detail", quiz_id=quiz_id))

    # Récupère un éventuel avis existant
    existing_review = Review.query.filter_by(
        idQUIZinReview=quiz_id, idUSERinReview=user_id
    ).first()

    if request.method == "POST":
        rating = request.form.get("rating", type=int)
        comment = request.form.get("comment", "").strip() or None

        if not rating or not (1 <= rating <= 5):
            flash("Veuillez sélectionner une note entre 1 et 5 étoiles.", "error")
            return render_template(
                "quiz/review_form.html",
                quiz=quiz,
                existing_review=existing_review,
            )

        try:
            if existing_review:
                existing_review.rating = rating
                existing_review.comment = comment
                existing_review.date = date.today()
                with db_transaction() as db_session:
                    db_session.merge(existing_review)
                flash("Votre avis a été mis à jour.", "success")
            else:
                new_review = Review(
                    idUSERinReview=user_id,
                    idQUIZinReview=quiz_id,
                    rating=rating,
                    comment=comment,
                    date=date.today(),
                )
                with db_transaction() as db_session:
                    db_session.add(new_review)
                # Attribution des badges liés aux avis
                has_comment = bool(comment and comment.strip())
                new_badges = award_review_badges(user_id=user_id, has_comment=has_comment)
                if new_badges:
                    names = ", ".join(f"{b.icon} {b.name}" for b in new_badges)
                    flash(f"Nouveau(x) badge(s) débloqué(s) : {names} !", "success")
                flash("Votre avis a été enregistré. Merci !", "success")
        except Exception as e:
            flash(f"Erreur lors de l'enregistrement : {str(e)}", "error")

        return redirect(url_for("profile.player_dashboard"))

    return render_template(
        "quiz/review_form.html",
        quiz=quiz,
        existing_review=existing_review,
    )


# Page publique listant tous les badges disponibles
@main_bp.get("/badges")
def badges_page():
    from app.models.models import Badge, UserBadge

    all_badges = Badge.query.order_by(Badge.trigger, Badge.category, Badge.score_min).all()

    CATEGORY_LABELS = {
        "SECURITE_WEB": "Sécurité Web",
        "MALWARE": "Malware",
        "RESEAUX": "Réseaux",
        "CRYPTOGRAPHIE": "Cryptographie",
        "INGENIERIE_SOCIALE": "Ingénierie sociale",
        "INTRODUCTION_CYBER": "Introduction Cyber",
    }

    # Badges déjà obtenus par l'utilisateur connecté
    earned_ids = set()
    if "user_id" in session:
        user_id = session["user_id"]
        earned_ids = {
            ub.idBadge
            for ub in UserBadge.query.filter_by(idUser=user_id).all()
        }

    badges_data = [
        {
            "id": b.idBadges,
            "name": b.name,
            "description": b.description,
            "icon": b.icon or "🏅",
            "trigger": b.trigger,
            "category": CATEGORY_LABELS.get(b.category, "Global") if b.category else "Global",
            "score_range": f"{b.score_min}% – {b.score_max}%"
                if b.score_min is not None and b.score_max is not None
                else "—",
            "earned": b.idBadges in earned_ids,
        }
        for b in all_badges
    ]

    return render_template("badges/badges.html", badges=badges_data)


# Liste des avis pour un quiz
@main_bp.get("/quiz/<int:quiz_id>/reviews")
def quiz_reviews(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    reviews = (
        Review.query
        .filter(Review.idQUIZinReview == quiz_id)
        .order_by(Review.date.desc())
        .all()
    )

    avg_rating = (
        db.session.query(func.avg(Review.rating))
        .filter(Review.idQUIZinReview == quiz_id)
        .scalar()
    )
    avg_rating = round(avg_rating, 1) if avg_rating else None

    reviews_data = [
        {
            "username": review.user.username,
            "rating": review.rating,
            "comment": review.comment,
            "date": review.date.strftime("%d/%m/%Y") if review.date else "N/A",
        }
        for review in reviews
    ]

    return render_template(
        "quiz/quiz_reviews.html",
        quiz=quiz,
        reviews=reviews_data,
        avg_rating=avg_rating,
        review_count=len(reviews_data),
    )
