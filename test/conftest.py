import os
import pytest
from datetime import date
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db as _db
from app.models.models import (
    User, Role, Quiz, Badge, Question, Response, Result, UserBadge
)


@pytest.fixture(scope="session")
def app():
    """Crée l'application Flask avec SQLite en mémoire pour les tests."""
    test_app = create_app("testing")
    os.makedirs(test_app.config["UPLOAD_FOLDER"], exist_ok=True)
    with test_app.app_context():
        _db.create_all()
        yield test_app
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Client HTTP pour les tests de routes."""
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_db(app):
    """Vide toutes les tables après chaque test pour isolation complète."""
    yield
    _db.session.rollback()
    for table in reversed(_db.metadata.sorted_tables):
        _db.session.execute(table.delete())
    _db.session.commit()


# --- Fixtures de rôles ---

@pytest.fixture
def player_role():
    role = Role(nameRoles="player")
    _db.session.add(role)
    _db.session.commit()
    return role


@pytest.fixture
def creator_role():
    role = Role(nameRoles="creator")
    _db.session.add(role)
    _db.session.commit()
    return role


@pytest.fixture
def admin_role():
    role = Role(nameRoles="admin")
    _db.session.add(role)
    _db.session.commit()
    return role


# --- Fixtures d'utilisateurs ---

@pytest.fixture
def test_player(player_role):
    user = User(
        username="testplayer",
        hashpassword=generate_password_hash("Player123!"),
        emailUser="player@test.com",
    )
    user.roles.append(player_role)
    _db.session.add(user)
    _db.session.commit()
    return user


@pytest.fixture
def test_creator(creator_role):
    user = User(
        username="testcreator",
        hashpassword=generate_password_hash("Creator123!"),
        emailUser="creator@test.com",
    )
    user.roles.append(creator_role)
    _db.session.add(user)
    _db.session.commit()
    return user


@pytest.fixture
def test_admin(admin_role):
    user = User(
        username="testadmin",
        hashpassword=generate_password_hash("Admin123!"),
        emailUser="admin@test.com",
    )
    user.roles.append(admin_role)
    _db.session.add(user)
    _db.session.commit()
    return user


# --- Fixture de quiz complet ---

@pytest.fixture
def test_quiz(test_creator):
    quiz = Quiz(
        title="Quiz Test",
        difficulty="EASY",
        statut="DRAFT",
        idCreatedByUser=test_creator.idUSER,
        createdAt=date.today(),
    )
    _db.session.add(quiz)
    _db.session.flush()

    question = Question(
        idQuestionFromQuiz=quiz.idQUIZ,
        QuestionText="Qu'est-ce qu'un mot de passe fort ?",
    )
    _db.session.add(question)
    _db.session.flush()

    _db.session.add_all([
        Response(idResponseFromQuestion=question.idQUESTION, responseText="Au moins 12 caractères avec majuscules, chiffres et symboles", isCorrect=True),
        Response(idResponseFromQuestion=question.idQUESTION, responseText="Le prénom suivi de la date de naissance", isCorrect=False),
        Response(idResponseFromQuestion=question.idQUESTION, responseText="Un mot du dictionnaire", isCorrect=False),
        Response(idResponseFromQuestion=question.idQUESTION, responseText="1234", isCorrect=False),
    ])
    _db.session.commit()
    return quiz
