"""
Tests unitaires pour l'authentification (connexion).
Remplacement de l'ancien script par des tests pytest corrects.

Correction : l'ancien fichier importait 'from app.database import db'
qui n'existe pas — le bon module est 'app.extensions'.
"""
from werkzeug.security import check_password_hash
from app.models.models import User
from app.extensions import db  # noqa: F401  (import correct)


def test_user_password_hash_matches(test_player):
    """Le hash stocké doit correspondre au mot de passe du joueur de test."""
    user = User.query.filter_by(username="testplayer").first()
    assert user is not None
    assert check_password_hash(user.hashpassword, "Player123!") is True


def test_user_wrong_password_rejected(test_player):
    """Un mauvais mot de passe ne doit pas être accepté."""
    user = User.query.filter_by(username="testplayer").first()
    assert user is not None
    assert check_password_hash(user.hashpassword, "WrongPassword!") is False


def test_user_has_player_role(test_player):
    """L'utilisateur de test doit avoir le rôle 'player'."""
    user = User.query.filter_by(username="testplayer").first()
    assert user is not None
    role_names = [role.nameRoles for role in user.roles]
    assert "player" in role_names


def test_login_route_success(client, test_player):
    """La route de login doit rediriger vers l'accueil en cas de succès."""
    response = client.post(
        "/auth/login",
        data={"username": "testplayer", "password": "Player123!"},
        follow_redirects=False,
    )
    assert response.status_code == 302


def test_login_route_wrong_password(client, test_player):
    """Un mauvais mot de passe doit rester sur la page de login."""
    response = client.post(
        "/auth/login",
        data={"username": "testplayer", "password": "WrongPassword!"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "incorrect" in response.data.decode("utf-8").lower() or \
           "mot de passe" in response.data.decode("utf-8").lower()


def test_login_route_unknown_user(client):
    """Un utilisateur inexistant ne doit pas pouvoir se connecter."""
    response = client.post(
        "/auth/login",
        data={"username": "utilisateur_inexistant", "password": "Password123!"},
        follow_redirects=True,
    )
    assert response.status_code == 200


def test_login_route_missing_fields(client):
    """Des champs vides doivent afficher un message d'erreur."""
    response = client.post(
        "/auth/login",
        data={"username": "", "password": ""},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "champs" in response.data.decode("utf-8").lower()


def test_logout_clears_session(client, test_player):
    """La déconnexion doit vider la session."""
    client.post(
        "/auth/login",
        data={"username": "testplayer", "password": "Player123!"},
    )
    response = client.get("/auth/logout", follow_redirects=False)
    assert response.status_code == 302
