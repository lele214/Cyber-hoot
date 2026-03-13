"""
Service d'attribution automatique des badges.

Trois types de déclencheurs :
  - "score"          : basé sur le pourcentage de réussite à un quiz
  - "review"         : déclenché quand l'utilisateur laisse un avis (note)
  - "review_comment" : déclenché quand l'utilisateur laisse un avis avec commentaire
"""
from datetime import date
from app.extensions import db
from app.models.models import Badge, UserBadge, Result, Quiz, Review


def _award(user_id: int, badge: Badge) -> bool:
    """Attribue un badge à un utilisateur s'il ne l'a pas déjà. Retourne True si nouveau."""
    existing = UserBadge.query.filter_by(idUser=user_id, idBadge=badge.idBadges).first()
    if existing:
        return False
    db.session.add(UserBadge(idUser=user_id, idBadge=badge.idBadges, obtainedAt=date.today()))
    return True


def award_score_badges(user_id: int, quiz_id: int, score: int, total_questions: int) -> list:
    """
    Attribue les badges de type 'score' après un quiz.
    Retourne la liste des nouveaux badges obtenus.
    """
    if total_questions == 0:
        return []

    percentage = round(score / total_questions * 100)
    quiz = Quiz.query.get(quiz_id)
    category = quiz.category if quiz else None

    # Badges candidats : score dans la plage ET (catégorie nulle OU catégorie correspond)
    candidates = Badge.query.filter(
        Badge.trigger == "score",
        Badge.score_min <= percentage,
        Badge.score_max >= percentage,
        db.or_(Badge.category.is_(None), Badge.category == category),
    ).all()

    newly_awarded = []
    for badge in candidates:
        if _award(user_id, badge):
            newly_awarded.append(badge)

    if newly_awarded:
        db.session.commit()

    return newly_awarded


def award_review_badges(user_id: int, has_comment: bool) -> list:
    """
    Attribue les badges liés aux avis.
    - 'review'         : a laissé un avis (avec ou sans commentaire)
    - 'review_comment' : a laissé un avis AVEC commentaire
    Retourne la liste des nouveaux badges obtenus.
    """
    triggers = ["review"]
    if has_comment:
        triggers.append("review_comment")

    candidates = Badge.query.filter(Badge.trigger.in_(triggers)).all()

    newly_awarded = []
    for badge in candidates:
        if _award(user_id, badge):
            newly_awarded.append(badge)

    if newly_awarded:
        db.session.commit()

    return newly_awarded


def award_retroactive(app=None):
    """
    Attribue rétroactivement les badges à tous les utilisateurs existants
    en rejouant leurs résultats et avis.
    À appeler depuis le script de seed ou une route admin.
    """
    def _run():
        # --- Badges basés sur les scores ---
        results = Result.query.filter(Result.totalQuestions > 0).all()
        for result in results:
            award_score_badges(
                user_id=result.idUSERinResult,
                quiz_id=result.idQUIZinResult,
                score=result.score,
                total_questions=result.totalQuestions,
            )

        # --- Badges basés sur les avis ---
        reviews = Review.query.all()
        for review in reviews:
            has_comment = bool(review.comment and review.comment.strip())
            award_review_badges(user_id=review.idUSERinReview, has_comment=has_comment)

    if app:
        with app.app_context():
            _run()
    else:
        _run()
