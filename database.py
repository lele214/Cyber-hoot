from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()


def init_db(app):
    mysql_user = os.getenv("MYSQL_USER", "flaskuser")
    mysql_password = os.getenv("MYSQL_PASSWORD", "flaskpassword")
    mysql_host = os.getenv("MYSQL_HOST", "localhost")
    mysql_port = os.getenv("MYSQL_PORT", "3306")
    mysql_database = os.getenv("MYSQL_DATABASE", "cyberhoot")

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = (
        False  # True si on veut afficher les requêtes SQL en erreur
    )

    db.init_app(app)

    return db
