import os
from flask import Flask
from dotenv import load_dotenv


def create_app(config_name=None):
    """Application Factory - crée et configure l'application Flask"""
    load_dotenv()

    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)

    # Charger la configuration
    from app.config import config
    app.config.from_object(config[config_name])

    # Initialiser les extensions
    from app.extensions import db
    db.init_app(app)

    # Enregistrer les blueprints
    from app.routes.main_routes import main_bp
    from app.routes.auth import auth_bp
    from app.routes.profile import profile_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)

    # Créer le dossier d'uploads s'il n'existe pas
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Commandes CLI Flask
    _register_cli(app)

    return app


def _register_cli(app):
    import click

    @app.cli.command("seed-badges")
    def seed_badges_cmd():
        """Insère les badges prédéfinis et attribue rétroactivement aux utilisateurs."""
        from app.extensions import db
        from app.models.models import Badge
        from app.services.badge_service import award_retroactive

        BADGES = [
            # Badges globaux — score
            {"name": "Goûteur de Feutres", "description": "T'as vraiment une tête à connaître le goût des feutres", "icon": "🖊️", "trigger": "score", "score_min": 0, "score_max": 0, "category": None},
            {"name": "Fantôme du Net", "description": "Tu étais présent... mais à peine détectable dans la matrice", "icon": "👻", "trigger": "score", "score_min": 1, "score_max": 24, "category": None},
            {"name": "Padawan Numérique", "description": "La Force cyber est en toi, mais t'as pas encore choisi le bon côté", "icon": "🌱", "trigger": "score", "score_min": 25, "score_max": 49, "category": None},
            {"name": "Apprenti Cyber", "description": "Tu commences à y voir quelque chose dans la matrix", "icon": "🔍", "trigger": "score", "score_min": 50, "score_max": 74, "category": None},
            {"name": "Presque Hacker", "description": "Si proche, si loin... comme le WiFi du voisin", "icon": "📡", "trigger": "score", "score_min": 75, "score_max": 99, "category": None},
            {"name": "L'Élu du Clavier Sacré", "description": "Neo lui-même t'appelle son maître — perfection absolue", "icon": "⌨️", "trigger": "score", "score_min": 100, "score_max": 100, "category": None},
            # INTRODUCTION_CYBER
            {"name": "Je Pensais Que Cyber C'était Cyberpunk", "description": "Ce n'est pas un jeu vidéo... retente ta chance !", "icon": "🎮", "trigger": "score", "score_min": 0, "score_max": 49, "category": "INTRODUCTION_CYBER"},
            {"name": "Citoyen Numérique", "description": "Tu commences à parler la langue des machines", "icon": "🌐", "trigger": "score", "score_min": 50, "score_max": 99, "category": "INTRODUCTION_CYBER"},
            {"name": "Sénateur du Cyberespace", "description": "Tu maîtrises les fondamentaux mieux que nos politiciens", "icon": "🏛️", "trigger": "score", "score_min": 100, "score_max": 100, "category": "INTRODUCTION_CYBER"},
            # SECURITE_WEB
            {"name": "XSS = Marque de Lessive ?", "description": "Retourne à la machine à laver, on te rappellera", "icon": "🧺", "trigger": "score", "score_min": 0, "score_max": 49, "category": "SECURITE_WEB"},
            {"name": "Chasseur de Failles en Herbe", "description": "Tu sniffes les injections SQL à 10 mètres — presque", "icon": "🔎", "trigger": "score", "score_min": 50, "score_max": 99, "category": "SECURITE_WEB"},
            {"name": "Gardien des Temples HTTP", "description": "Aucune faille ne passe sous ton regard acéré", "icon": "🛡️", "trigger": "score", "score_min": 100, "score_max": 100, "category": "SECURITE_WEB"},
            # MALWARE
            {"name": "Cliqueur Professionnel", "description": "Tu as cliqué sur 'Vous avez gagné un iPhone' et tu t'en es vanté", "icon": "📱", "trigger": "score", "score_min": 0, "score_max": 49, "category": "MALWARE"},
            {"name": "Détective du Darkside", "description": "Tu connais leurs méthodes... mais pas encore toutes", "icon": "🕵️", "trigger": "score", "score_min": 50, "score_max": 99, "category": "MALWARE"},
            {"name": "Exterminateur de Virus", "description": "Les malwares fuient à ton approche comme vampires au soleil", "icon": "🦠", "trigger": "score", "score_min": 100, "score_max": 100, "category": "MALWARE"},
            # RESEAUX
            {"name": "Mon WiFi ça Marche Pas", "description": "C'est pas ta faute, c'est la box Livebox (on y croit)", "icon": "📶", "trigger": "score", "score_min": 0, "score_max": 49, "category": "RESEAUX"},
            {"name": "Architecte du Net en Devenir", "description": "Tu construis des ponts, mais pas encore des autoroutes", "icon": "🌉", "trigger": "score", "score_min": 50, "score_max": 99, "category": "RESEAUX"},
            {"name": "Maître du Routage Cosmique", "description": "IP, TCP, UDP ? C'est ton terrain de jeu favori", "icon": "🌍", "trigger": "score", "score_min": 100, "score_max": 100, "category": "RESEAUX"},
            # CRYPTOGRAPHIE
            {"name": "ROT13 ? C'est Quoi Ce Plat ?", "description": "Ce n'est pas une recette de cuisine, retente ta chance", "icon": "🍝", "trigger": "score", "score_min": 0, "score_max": 49, "category": "CRYPTOGRAPHIE"},
            {"name": "Déchiffreur de Runes Modernes", "description": "Tu décodes le monde, lettre par lettre", "icon": "🔑", "trigger": "score", "score_min": 50, "score_max": 99, "category": "CRYPTOGRAPHIE"},
            {"name": "Dieu du Chiffrement", "description": "AES, RSA, SHA... ça n'a plus aucun secret pour toi", "icon": "🔐", "trigger": "score", "score_min": 100, "score_max": 100, "category": "CRYPTOGRAPHIE"},
            # INGENIERIE_SOCIALE
            {"name": "Ma Banque M'a Demandé Mon Mot de Passe", "description": "Et tu as répondu... 🤦 Méfie-toi des mails suspects", "icon": "💸", "trigger": "score", "score_min": 0, "score_max": 49, "category": "INGENIERIE_SOCIALE"},
            {"name": "Détecteur de Phishing", "description": "Ta boîte mail est un vrai bunker anti-arnaque", "icon": "📧", "trigger": "score", "score_min": 50, "score_max": 99, "category": "INGENIERIE_SOCIALE"},
            {"name": "Maître Jedi de la Manipulation", "description": "Tu détectes les arnaques avant même qu'elles n'existent", "icon": "🎭", "trigger": "score", "score_min": 100, "score_max": 100, "category": "INGENIERIE_SOCIALE"},
            # Badges avis
            {"name": "Critique du Cyberspace", "description": "Tu as pris le temps de noter un quiz — respect, c'est rare", "icon": "⭐", "trigger": "review", "score_min": None, "score_max": None, "category": None},
            {"name": "Chroniqueur du Net", "description": "Tu as laissé un avis avec commentaire — ta plume illumine la communauté", "icon": "💬", "trigger": "review_comment", "score_min": None, "score_max": None, "category": None},
        ]

        inserted = 0
        for data in BADGES:
            if Badge.query.filter_by(name=data["name"], trigger=data["trigger"]).first():
                continue
            db.session.add(Badge(**data))
            inserted += 1
        db.session.commit()
        click.echo(f"✅ {inserted} badge(s) insérés.")

        click.echo("🔄 Attribution rétroactive...")
        award_retroactive()
        click.echo("✅ Terminé.")
