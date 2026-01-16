from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()


def init_db(app):
    mysql_user = os.getenv("MYSQL_USER", "")
    mysql_password = os.getenv("MYSQL_PASSWORD", "")
    mysql_host = os.getenv("MYSQL_HOST", "")
    mysql_port = os.getenv("MYSQL_PORT", "")
    mysql_database = os.getenv("MYSQL_DATABASE", "")

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = (
        True  # True pour afficher les requêtes SQL et les erreurs
    )

    db.init_app(app)

    return db
