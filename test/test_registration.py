"""
Tests unitaires pour l'inscription des utilisateurs.
"""
from app.models.models import User


def test_register_success(client, player_role):
    """Une inscription valide doit créer un utilisateur et rediriger vers le login."""
    response = client.post(
        "/auth/register",
        data={
            "username": "nouveaujoueur",
            "email": "nouveau@test.com",
            "password": "Secure123!",
            "password_confirm": "Secure123!",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302
    user = User.query.filter_by(username="nouveaujoueur").first()
    assert user is not None
    assert user.emailUser == "nouveau@test.com"


def test_register_assigns_player_role(client, player_role):
    """L'inscription doit assigner le rôle 'player' par défaut."""
    client.post(
        "/auth/register",
        data={
            "username": "nouveaujoueur",
            "email": "nouveau@test.com",
            "password": "Secure123!",
            "password_confirm": "Secure123!",
        },
    )
    user = User.query.filter_by(username="nouveaujoueur").first()
    assert user is not None
    role_names = [r.nameRoles for r in user.roles]
    assert "player" in role_names


def test_register_duplicate_username(client, test_player):
    """Un nom d'utilisateur déjà pris doit être refusé."""
    response = client.post(
        "/auth/register",
        data={
            "username": "testplayer",
            "email": "autre@test.com",
            "password": "Secure123!",
            "password_confirm": "Secure123!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "utilisateur" in response.data.decode("utf-8").lower()


def test_register_duplicate_email(client, test_player):
    """Une adresse email déjà utilisée doit être refusée."""
    response = client.post(
        "/auth/register",
        data={
            "username": "autrejoueur",
            "email": "player@test.com",
            "password": "Secure123!",
            "password_confirm": "Secure123!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "email" in response.data.decode("utf-8").lower()


def test_register_passwords_mismatch(client):
    """Des mots de passe différents doivent être refusés."""
    response = client.post(
        "/auth/register",
        data={
            "username": "nouveaujoueur",
            "email": "nouveau@test.com",
            "password": "Secure123!",
            "password_confirm": "Different123!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "correspondent" in response.data.decode("utf-8").lower()


def test_register_password_too_short(client):
    """Un mot de passe trop court (< 8 chars) doit être refusé."""
    response = client.post(
        "/auth/register",
        data={
            "username": "nouveaujoueur",
            "email": "nouveau@test.com",
            "password": "Abc1!",
            "password_confirm": "Abc1!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "8" in response.data.decode("utf-8")


def test_register_password_no_uppercase(client):
    """Un mot de passe sans majuscule doit être refusé."""
    response = client.post(
        "/auth/register",
        data={
            "username": "nouveaujoueur",
            "email": "nouveau@test.com",
            "password": "nouppercase1!",
            "password_confirm": "nouppercase1!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "majuscule" in response.data.decode("utf-8").lower()


def test_register_password_no_digit(client):
    """Un mot de passe sans chiffre doit être refusé."""
    response = client.post(
        "/auth/register",
        data={
            "username": "nouveaujoueur",
            "email": "nouveau@test.com",
            "password": "NoDigitHere!",
            "password_confirm": "NoDigitHere!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "chiffre" in response.data.decode("utf-8").lower()


def test_register_password_no_special_char(client):
    """Un mot de passe sans caractère spécial doit être refusé."""
    response = client.post(
        "/auth/register",
        data={
            "username": "nouveaujoueur",
            "email": "nouveau@test.com",
            "password": "NoSpecial123",
            "password_confirm": "NoSpecial123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "spécial" in response.data.decode("utf-8").lower()


def test_register_missing_fields(client):
    """Des champs manquants doivent afficher une erreur."""
    response = client.post(
        "/auth/register",
        data={"username": "", "email": "", "password": "", "password_confirm": ""},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "champs" in response.data.decode("utf-8").lower()


def test_register_password_no_lowercase(client):
    """Un mot de passe sans minuscule doit être refusé."""
    response = client.post(
        "/auth/register",
        data={
            "username": "nouveaujoueur",
            "email": "nouveau@test.com",
            "password": "NOLOWERCASE1!",
            "password_confirm": "NOLOWERCASE1!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "minuscule" in response.data.decode("utf-8").lower()
