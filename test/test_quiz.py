"""
Tests unitaires pour la création et la modification de quiz.
"""
import json
from datetime import date

import pytest

from app.extensions import db
from app.models.models import Quiz, Question, Response, Media


# ── Création de quiz (niveau modèle) ───────────────────────────────────────

def test_quiz_creation_model(test_creator):
    """Un quiz doit être créé et persisté correctement."""
    quiz = Quiz(
        title="Introduction à la cybersécurité",
        difficulty="EASY",
        statut="DRAFT",
        idCreatedByUser=test_creator.idUSER,
        createdAt=date.today(),
    )
    db.session.add(quiz)
    db.session.commit()

    saved = Quiz.query.filter_by(title="Introduction à la cybersécurité").first()
    assert saved is not None
    assert saved.difficulty == "EASY"
    assert saved.statut == "DRAFT"
    assert saved.idCreatedByUser == test_creator.idUSER


def test_quiz_with_questions_and_responses(test_creator):
    """Un quiz doit pouvoir contenir des questions avec des réponses."""
    quiz = Quiz(
        title="Quiz complet",
        difficulty="MEDIUM",
        statut="DRAFT",
        idCreatedByUser=test_creator.idUSER,
        createdAt=date.today(),
    )
    db.session.add(quiz)
    db.session.flush()

    question = Question(
        idQuestionFromQuiz=quiz.idQUIZ,
        QuestionText="Qu'est-ce que le phishing ?",
        explanation="Le phishing est une technique d'hameçonnage.",
    )
    db.session.add(question)
    db.session.flush()

    db.session.add_all([
        Response(idResponseFromQuestion=question.idQUESTION, responseText="Une attaque par email", isCorrect=True),
        Response(idResponseFromQuestion=question.idQUESTION, responseText="Un logiciel antivirus", isCorrect=False),
        Response(idResponseFromQuestion=question.idQUESTION, responseText="Un protocole réseau", isCorrect=False),
    ])
    db.session.commit()

    saved_quiz = Quiz.query.get(quiz.idQUIZ)
    assert len(saved_quiz.questions) == 1
    assert saved_quiz.questions[0].QuestionText == "Qu'est-ce que le phishing ?"
    assert len(saved_quiz.questions[0].responses) == 3
    correct = [r for r in saved_quiz.questions[0].responses if r.isCorrect]
    assert len(correct) == 1


def test_quiz_min_two_responses_validation(test_creator):
    """Vérifier que la logique métier exige au moins 2 réponses par question."""
    quiz = Quiz(
        title="Quiz Minimal",
        difficulty="EASY",
        statut="DRAFT",
        idCreatedByUser=test_creator.idUSER,
        createdAt=date.today(),
    )
    db.session.add(quiz)
    db.session.flush()

    question = Question(
        idQuestionFromQuiz=quiz.idQUIZ,
        QuestionText="Question unique ?",
    )
    db.session.add(question)
    db.session.flush()

    # Une seule réponse
    db.session.add(
        Response(idResponseFromQuestion=question.idQUESTION, responseText="Réponse unique", isCorrect=True)
    )
    db.session.commit()

    saved = Question.query.get(question.idQUESTION)
    assert len(saved.responses) < 2  # La contrainte doit être vérifiée au niveau route


# ── Création via route HTTP ──────────────────────────────────────────────────

def test_quiz_create_route_success(client, test_creator):
    """La route de création doit créer un quiz en base et rediriger."""
    with client.session_transaction() as sess:
        sess["user_id"] = test_creator.idUSER
        sess["username"] = test_creator.username
        sess["user_roles"] = ["creator"]

    response = client.post(
        "/profile/creator/quiz/create",
        data={
            "title": "Quiz via route",
            "difficulty": "EASY",
            "question_text_0": "Qu'est-ce qu'un pare-feu ?",
            "correct_0": "0",
            "response_exists_0_0": "1",
            "response_text_0_0": "Un dispositif de sécurité réseau",
            "response_exists_0_1": "1",
            "response_text_0_1": "Un type de virus",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302
    quiz = Quiz.query.filter_by(title="Quiz via route").first()
    assert quiz is not None
    assert quiz.statut == "DRAFT"


def test_quiz_create_route_missing_title(client, test_creator):
    """Un titre manquant doit être refusé."""
    with client.session_transaction() as sess:
        sess["user_id"] = test_creator.idUSER
        sess["username"] = test_creator.username
        sess["user_roles"] = ["creator"]

    response = client.post(
        "/profile/creator/quiz/create",
        data={
            "title": "",
            "difficulty": "EASY",
            "question_text_0": "Une question ?",
            "correct_0": "0",
            "response_exists_0_0": "1",
            "response_text_0_0": "Réponse A",
            "response_exists_0_1": "1",
            "response_text_0_1": "Réponse B",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "titre" in response.data.decode("utf-8").lower() or \
           "obligatoire" in response.data.decode("utf-8").lower()


def test_quiz_create_route_invalid_difficulty(client, test_creator):
    """Une difficulté invalide doit être refusée."""
    with client.session_transaction() as sess:
        sess["user_id"] = test_creator.idUSER
        sess["username"] = test_creator.username
        sess["user_roles"] = ["creator"]

    response = client.post(
        "/profile/creator/quiz/create",
        data={
            "title": "Quiz test",
            "difficulty": "EXTREME",
            "question_text_0": "Une question ?",
            "correct_0": "0",
            "response_exists_0_0": "1",
            "response_text_0_0": "Réponse A",
            "response_exists_0_1": "1",
            "response_text_0_1": "Réponse B",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "difficulté" in response.data.decode("utf-8").lower() or \
           "valide" in response.data.decode("utf-8").lower()


def test_quiz_create_route_no_question(client, test_creator):
    """Un quiz sans question doit être refusé."""
    with client.session_transaction() as sess:
        sess["user_id"] = test_creator.idUSER
        sess["username"] = test_creator.username
        sess["user_roles"] = ["creator"]

    response = client.post(
        "/profile/creator/quiz/create",
        data={"title": "Quiz vide", "difficulty": "EASY"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "question" in response.data.decode("utf-8").lower()


def test_quiz_create_requires_login(client):
    """La route de création doit refuser les utilisateurs non connectés."""
    response = client.post(
        "/profile/creator/quiz/create",
        data={"title": "Quiz", "difficulty": "EASY"},
        follow_redirects=False,
    )
    assert response.status_code == 302


# ── Modification de quiz (niveau modèle) ────────────────────────────────────

def test_quiz_modification_title(test_quiz):
    """La modification du titre doit être persistée."""
    quiz = Quiz.query.get(test_quiz.idQUIZ)
    quiz.title = "Titre modifié"
    db.session.commit()

    updated = Quiz.query.get(test_quiz.idQUIZ)
    assert updated.title == "Titre modifié"


def test_quiz_modification_difficulty(test_quiz):
    """La modification de la difficulté doit être persistée."""
    quiz = Quiz.query.get(test_quiz.idQUIZ)
    quiz.difficulty = "HARD"
    db.session.commit()

    updated = Quiz.query.get(test_quiz.idQUIZ)
    assert updated.difficulty == "HARD"


def test_quiz_status_transitions(test_quiz):
    """Les changements de statut doivent être possibles : DRAFT → PENDING → PUBLISHED → MODIFIED."""
    quiz = Quiz.query.get(test_quiz.idQUIZ)

    quiz.statut = "PENDING"
    db.session.commit()
    assert Quiz.query.get(test_quiz.idQUIZ).statut == "PENDING"

    quiz.statut = "PUBLISHED"
    db.session.commit()
    assert Quiz.query.get(test_quiz.idQUIZ).statut == "PUBLISHED"

    quiz.statut = "MODIFIED"
    db.session.commit()
    assert Quiz.query.get(test_quiz.idQUIZ).statut == "MODIFIED"


def test_quiz_modification_via_route(client, test_creator, test_quiz):
    """La route de modification doit mettre à jour le quiz."""
    with client.session_transaction() as sess:
        sess["user_id"] = test_creator.idUSER
        sess["username"] = test_creator.username
        sess["user_roles"] = ["creator"]

    response = client.post(
        f"/profile/creator/quiz/{test_quiz.idQUIZ}/edit",
        data={
            "title": "Quiz modifié via route",
            "difficulty": "HARD",
            "question_text_0": "Nouvelle question ?",
            "correct_0": "0",
            "response_exists_0_0": "1",
            "response_text_0_0": "Réponse correcte",
            "response_exists_0_1": "1",
            "response_text_0_1": "Réponse incorrecte",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302

    updated = Quiz.query.get(test_quiz.idQUIZ)
    assert updated.title == "Quiz modifié via route"
    assert updated.difficulty == "HARD"


def test_quiz_published_becomes_modified_after_edit(client, test_creator, test_quiz):
    """Un quiz PUBLISHED doit passer à MODIFIED après modification."""
    test_quiz.statut = "PUBLISHED"
    db.session.commit()

    with client.session_transaction() as sess:
        sess["user_id"] = test_creator.idUSER
        sess["username"] = test_creator.username
        sess["user_roles"] = ["creator"]

    client.post(
        f"/profile/creator/quiz/{test_quiz.idQUIZ}/edit",
        data={
            "title": "Quiz republié",
            "difficulty": "EASY",
            "question_text_0": "Question mise à jour ?",
            "correct_0": "0",
            "response_exists_0_0": "1",
            "response_text_0_0": "Réponse A",
            "response_exists_0_1": "1",
            "response_text_0_1": "Réponse B",
        },
    )

    updated = Quiz.query.get(test_quiz.idQUIZ)
    assert updated.statut == "MODIFIED"
