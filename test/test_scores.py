"""
Tests unitaires pour la gestion des scores et des résultats.
"""
import json
from datetime import date

from app.extensions import db
from app.models.models import Result


# ── Création de résultat (niveau modèle) ────────────────────────────────────

def test_result_creation(test_player, test_quiz):
    """Un résultat doit être créé et persisté correctement."""
    result = Result(
        idQUIZinResult=test_quiz.idQUIZ,
        idUSERinResult=test_player.idUSER,
        date=date.today(),
        score=7,
        totalQuestions=10,
        answer=str({"1": "A", "2": "B"}),
    )
    db.session.add(result)
    db.session.commit()

    saved = Result.query.filter_by(
        idQUIZinResult=test_quiz.idQUIZ,
        idUSERinResult=test_player.idUSER,
    ).first()
    assert saved is not None
    assert saved.score == 7
    assert saved.totalQuestions == 10


def test_result_score_zero(test_player, test_quiz):
    """Un score de 0 doit être valide."""
    result = Result(
        idQUIZinResult=test_quiz.idQUIZ,
        idUSERinResult=test_player.idUSER,
        date=date.today(),
        score=0,
        totalQuestions=5,
        answer="{}",
    )
    db.session.add(result)
    db.session.commit()

    saved = Result.query.filter_by(
        idQUIZinResult=test_quiz.idQUIZ,
        idUSERinResult=test_player.idUSER,
    ).first()
    assert saved.score == 0


def test_result_perfect_score(test_player, test_quiz):
    """Un score parfait (score == totalQuestions) doit être valide."""
    result = Result(
        idQUIZinResult=test_quiz.idQUIZ,
        idUSERinResult=test_player.idUSER,
        date=date.today(),
        score=10,
        totalQuestions=10,
        answer="{}",
    )
    db.session.add(result)
    db.session.commit()

    saved = Result.query.filter_by(score=10, totalQuestions=10).first()
    assert saved is not None
    assert saved.score == saved.totalQuestions


def test_result_relationships(test_player, test_quiz):
    """Les relations result → user et result → quiz doivent être accessibles."""
    result = Result(
        idQUIZinResult=test_quiz.idQUIZ,
        idUSERinResult=test_player.idUSER,
        date=date.today(),
        score=5,
        totalQuestions=10,
        answer="{}",
    )
    db.session.add(result)
    db.session.commit()

    saved = Result.query.get(result.idRESULT)
    assert saved.user.username == test_player.username
    assert saved.quiz.title == test_quiz.title


def test_multiple_results_same_user(test_player, test_quiz):
    """Un utilisateur peut avoir plusieurs résultats pour le même quiz."""
    for score in [3, 6, 9]:
        db.session.add(Result(
            idQUIZinResult=test_quiz.idQUIZ,
            idUSERinResult=test_player.idUSER,
            date=date.today(),
            score=score,
            totalQuestions=10,
            answer="{}",
        ))
    db.session.commit()

    results = Result.query.filter_by(
        idQUIZinResult=test_quiz.idQUIZ,
        idUSERinResult=test_player.idUSER,
    ).all()
    assert len(results) == 3
    scores = {r.score for r in results}
    assert scores == {3, 6, 9}


def test_average_score_calculation(test_player, test_quiz):
    """Le score moyen doit être calculable depuis les résultats."""
    for score in [4, 6, 8]:
        db.session.add(Result(
            idQUIZinResult=test_quiz.idQUIZ,
            idUSERinResult=test_player.idUSER,
            date=date.today(),
            score=score,
            totalQuestions=10,
            answer="{}",
        ))
    db.session.commit()

    results = Result.query.filter_by(idUSERinResult=test_player.idUSER).all()
    avg = sum(r.score for r in results) / len(results)
    assert avg == 6.0


# ── Soumission via route HTTP ────────────────────────────────────────────────

def test_submit_quiz_success(client, test_player, test_quiz):
    """La route de soumission doit créer un résultat et retourner 200."""
    with client.session_transaction() as sess:
        sess["user_id"] = test_player.idUSER
        sess["username"] = test_player.username
        sess["user_roles"] = ["player"]

    response = client.post(
        f"/quiz/{test_quiz.idQUIZ}/submit",
        json={
            "answers": {"1": "A", "2": "B"},
            "score": 8,
            "totalQuestions": 10,
        },
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["score"] == 8

    saved = Result.query.filter_by(
        idQUIZinResult=test_quiz.idQUIZ,
        idUSERinResult=test_player.idUSER,
    ).first()
    assert saved is not None
    assert saved.score == 8


def test_submit_quiz_not_logged_in(client, test_quiz):
    """Un utilisateur non connecté doit recevoir une erreur 401."""
    response = client.post(
        f"/quiz/{test_quiz.idQUIZ}/submit",
        json={"answers": {}, "score": 5, "totalQuestions": 10},
    )
    assert response.status_code == 401
    data = response.get_json()
    assert data["success"] is False


def test_submit_quiz_not_found(client, test_player):
    """Soumettre un résultat pour un quiz inexistant doit retourner 404."""
    with client.session_transaction() as sess:
        sess["user_id"] = test_player.idUSER
        sess["username"] = test_player.username
        sess["user_roles"] = ["player"]

    response = client.post(
        "/quiz/99999/submit",
        json={"answers": {}, "score": 0, "totalQuestions": 0},
    )
    assert response.status_code == 404


def test_submit_quiz_score_stored_correctly(client, test_player, test_quiz):
    """Le score soumis doit être exactement celui stocké en base."""
    with client.session_transaction() as sess:
        sess["user_id"] = test_player.idUSER
        sess["username"] = test_player.username
        sess["user_roles"] = ["player"]

    client.post(
        f"/quiz/{test_quiz.idQUIZ}/submit",
        json={"answers": {"1": "C"}, "score": 3, "totalQuestions": 5},
    )

    saved = Result.query.filter_by(idUSERinResult=test_player.idUSER).first()
    assert saved.score == 3
    assert saved.totalQuestions == 5
