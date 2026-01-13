# Fichier principal pour lancer l'application Flask
# Ce fichier sert de point d'entrée pour démarrer le serveur web

# Import de la fonction qui crée et configure l'application Flask
from app import create_app

# Création de l'instance de l'application Flask
app = create_app()

# Point d'entrée du programme : lance le serveur web uniquement si ce fichier est exécuté directement
if __name__ == "__main__":
    # Démarre le serveur Flask sur toutes les interfaces (0.0.0.0) au port 8000 avec le mode debug activé
    app.run(host="0.0.0.0", port=8000, debug=True)
