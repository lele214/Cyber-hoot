"""
Tests unitaires pour la création et la gestion des badges.
"""
from datetime import date

from app.extensions import db
from app.models.models import Badge, UserBadge


# ── Création de badge (niveau modèle) ───────────────────────────────────────

def test_badge_creation(test_quiz):
    """Un badge doit être créé et lié à un quiz."""
    badge = Badge(
        name="Expert Cybersécurité",
        idQuiz=test_quiz.idQUIZ,
    )
    db.session.add(badge)
    db.session.commit()

    saved = Badge.query.filter_by(name="Expert Cybersécurité").first()
    assert saved is not None
    assert saved.idQuiz == test_quiz.idQUIZ


def test_badge_with_image(test_quiz):
    """Un badge peut stocker une image en binaire."""
    fake_image = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"  # en-tête PNG factice
    badge = Badge(
        name="Badge avec image",
        image=fake_image,
        idQuiz=test_quiz.idQUIZ,
    )
    db.session.add(badge)
    db.session.commit()

    saved = Badge.query.filter_by(name="Badge avec image").first()
    assert saved is not None
    assert saved.image == fake_image


def test_badge_linked_to_quiz(test_quiz):
    """La relation badge → quiz doit être accessible."""
    badge = Badge(name="Badge Quiz", idQuiz=test_quiz.idQUIZ)
    db.session.add(badge)
    db.session.commit()

    saved = Badge.query.filter_by(name="Badge Quiz").first()
    assert saved.quiz is not None
    assert saved.quiz.title == test_quiz.title


def test_multiple_badges_per_quiz(test_quiz):
    """Un quiz peut avoir plusieurs badges."""
    badges = [
        Badge(name="Badge Bronze", idQuiz=test_quiz.idQUIZ),
        Badge(name="Badge Argent", idQuiz=test_quiz.idQUIZ),
        Badge(name="Badge Or",     idQuiz=test_quiz.idQUIZ),
    ]
    db.session.add_all(badges)
    db.session.commit()

    quiz_badges = Badge.query.filter_by(idQuiz=test_quiz.idQUIZ).all()
    assert len(quiz_badges) == 3


# ── Attribution de badge à un utilisateur ───────────────────────────────────

def test_assign_badge_to_user(test_player, test_quiz):
    """Un badge doit pouvoir être attribué à un utilisateur."""
    badge = Badge(name="Badge Joueur", idQuiz=test_quiz.idQUIZ)
    db.session.add(badge)
    db.session.flush()

    user_badge = UserBadge(
        idUser=test_player.idUSER,
        idBadge=badge.idBadges,
        obtainedAt=date.today(),
    )
    db.session.add(user_badge)
    db.session.commit()

    saved = UserBadge.query.filter_by(
        idUser=test_player.idUSER,
        idBadge=badge.idBadges,
    ).first()
    assert saved is not None
    assert saved.obtainedAt == date.today()


def test_user_badge_relationship(test_player, test_quiz):
    """La relation UserBadge doit être accessible depuis l'utilisateur."""
    badge = Badge(name="Badge Relation", idQuiz=test_quiz.idQUIZ)
    db.session.add(badge)
    db.session.flush()

    user_badge = UserBadge(
        idUser=test_player.idUSER,
        idBadge=badge.idBadges,
        obtainedAt=date.today(),
    )
    db.session.add(user_badge)
    db.session.commit()

    db.session.refresh(test_player)
    badge_ids = [ub.idBadge for ub in test_player.user_badges]
    assert badge.idBadges in badge_ids


def test_badge_without_image_is_valid(test_quiz):
    """Un badge sans image (champ nullable) doit être valide."""
    badge = Badge(name="Badge sans image", image=None, idQuiz=test_quiz.idQUIZ)
    db.session.add(badge)
    db.session.commit()

    saved = Badge.query.filter_by(name="Badge sans image").first()
    assert saved is not None
    assert saved.image is None
