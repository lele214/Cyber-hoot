"""
Tests unitaires pour la vérification de hash de mots de passe.
Conversion de l'ancien script en tests pytest.
"""
from werkzeug.security import check_password_hash, generate_password_hash

def test_hash_correct_password():
    """Un hash généré pour un mot de passe doit correspondre à ce même mot de passe."""
    password = "Admin1234!"
    hashed = generate_password_hash(password)
    assert check_password_hash(hashed, password) is True


def test_hash_wrong_password():
    """Un mauvais mot de passe ne doit pas correspondre au hash."""
    hashed = generate_password_hash("Admin1234!")
    assert check_password_hash(hashed, "WrongPassword!") is False


def test_hash_empty_password():
    """Une chaîne vide ne doit pas correspondre au hash d'un mot de passe."""
    hashed = generate_password_hash("Admin1234!")
    assert check_password_hash(hashed, "") is False


def test_generate_and_verify_roundtrip():
    """Un hash généré doit être vérifiable avec le même mot de passe."""
    password = "MonMotDePasse123!"
    hashed = generate_password_hash(password)
    assert check_password_hash(hashed, password) is True


def test_generate_and_verify_wrong_password():
    """Un hash généré ne doit pas correspondre à un autre mot de passe."""
    hashed = generate_password_hash("MonMotDePasse123!")
    assert check_password_hash(hashed, "AutreMotDePasse456@") is False


def test_two_hashes_of_same_password_are_different():
    """Deux hashes du même mot de passe doivent être différents (sel aléatoire)."""
    password = "MonMotDePasse123!"
    hash1 = generate_password_hash(password)
    hash2 = generate_password_hash(password)
    assert hash1 != hash2
    assert check_password_hash(hash1, password) is True
    assert check_password_hash(hash2, password) is True
