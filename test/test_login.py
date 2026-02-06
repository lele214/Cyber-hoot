from werkzeug.security import check_password_hash, generate_password_hash
from app.models.models import User
from app.database import db
from app import create_app

# Créer l'application
app = create_app()

with app.app_context():
    # Récupérer l'utilisateur
    user = User.query.filter_by(username='admin_cyberhoot').first()

    if not user:
        print("ERREUR : Utilisateur 'admin_cyberhoot' non trouvé !")
    else:
        print(f"Utilisateur trouvé : {user.username}")
        print(f"Email : {user.emailUser}")
        print(f"Hash length : {len(user.hashpassword) if user.hashpassword else 0}")
        print(f"Hash preview : {user.hashpassword[:50] if user.hashpassword else 'None'}")

        # Tester le mot de passe
        password = 'Admin1234!'
        result = check_password_hash(user.hashpassword, password)

        print(f"\nTest du mot de passe '{password}':")
        print(f"Résultat : {result}")

        if result:
            print("SUCCESS : Le mot de passe est correct !")
        else:
            print("ECHEC : Le mot de passe est incorrect !")

        # Vérifier les rôles
        print(f"\nRôles de l'utilisateur : {[role.nameRoles for role in user.roles]}")
