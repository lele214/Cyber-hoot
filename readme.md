
## Cyber-hoot

Notre plateforme Cyber-hoot (pour "cyber" et "kahoot") propose des quiz sur le thème de la Cybersécurité. Aujourd'hui, à l'ère d'un monde hyper-connecté, le nombre de cyberattaques n'a jamais été aussi important : il est prévu jusqu'à une cyberattaque toutes les 2 secondes d'ici 2031. Et l'un des facteurs de réussite de ces attaques est toujours relatif à une chose : le facteur humain. En effet, ce sont les erreurs que nous faisons tous les jours qui nous rendent le plus vulnérable. Et la raison est essentiellement à cause d'un manque d'information ou de formation. Notre plateforme va proposer divers quiz de culture générale relatifs aux différentes attaques existantes, essentiellement pour sensibiliser sur les risques liés à la cybersécurité.

## Guide d'utilisation

### Créer un compte

1. Accédez à http://localhost:5000
2. Cliquez sur **S'inscrire** dans le menu de navigation
3. Remplissez le formulaire avec votre nom d'utilisateur, email et mot de passe
4. Validez pour créer votre compte

### Se connecter

1. Cliquez sur **Se connecter** dans le menu de navigation
2. Entrez votre nom d'utilisateur et mot de passe
3. Vous serez redirigé vers la page d'accueil

### Répondre à un quiz

1. Connectez-vous à votre compte
2. Cliquez sur **Quiz** dans le menu de navigation
3. Choisissez un quiz parmi la liste disponible (différents niveaux de difficulté)
4. Répondez aux questions en sélectionnant les bonnes réponses
5. Validez le quiz pour voir votre score

### Consulter son profil

1. Cliquez sur **Profil** dans le menu de navigation
2. Consultez vos informations personnelles
3. Visualisez l'historique de vos quiz et vos scores


## Structure du projet

```
Cyber-hoot/
├── app/                        # Code de l'application Flask
│   ├── __init__.py             # Factory pattern (création de l'app, blueprints)
│   ├── config.py               # Configuration dev/prod (DB, upload, clé secrète)
│   ├── extensions.py           # Instance SQLAlchemy + gestionnaire de transactions
│   ├── decorators.py           # Décorateurs login_required, role_required
│   ├── models/
│   │   └── models.py           # Tous les modèles SQLAlchemy (User, Quiz, Question…)
│   ├── routes/
│   │   ├── auth.py             # Inscription, connexion, réinitialisation mdp
│   │   ├── main_routes.py      # Accueil, liste des quiz, détail quiz, serve_media
│   │   └── profile.py          # Dashboards player/creator/admin, gestion des quiz
│   ├── templates/
│   │   ├── auth/               # Templates connexion / inscription
│   │   ├── profile/
│   │   │   ├── admin/          # Dashboard administrateur
│   │   │   ├── creator/        # Dashboard créateur, création/édition de quiz
│   │   │   └── player/         # Dashboard joueur
│   │   └── quiz/               # Liste des quiz, quiz dynamique
│   └── static/
│       ├── js/
│       │   ├── quiz.js         # Soumission du quiz (fetch)
│       │   └── quiz_create.js  # Formulaire dynamique de création/édition
│       ├── src/input.css       # Source Tailwind CSS
│       └── output.css          # CSS compilé
├── database/
│   └── db_schemaV3-3.sql       # Schéma MySQL (tables, relations, enums)
├── test/
│   └── seed_data.sql           # Données de test (utilisateurs, quiz, rôles)
├── secrets/                    # Fichiers secrets Docker (non versionnés)
│   └── ...
├── uploads/                    # Images uploadées pour les quiz (hors static/)
│   └── ...                     # Fichiers servis uniquement via /media/<id>
├── Dockerfile                  # Build de l'image Flask (Python 3.11 + npm)
├── docker-compose.yml          # Services : app, db (MySQL 8), adminer
├── run.py                      # Point d'entrée Flask
├── requirements.txt            # Dépendances Python
├── package.json                # Dépendances npm (Tailwind CSS)
└── .env                        # Variables d'environnement (non versionné)
```

## Base de données

La base de données MySQL 8 est automatiquement initialisée au démarrage Docker.

