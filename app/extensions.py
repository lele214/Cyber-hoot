from flask_sqlalchemy import SQLAlchemy
from contextlib import contextmanager

db = SQLAlchemy()


@contextmanager
def db_transaction():
    """Context manager pour gérer les transacrtions de base de données.
    - commit automatique à la fin du bloc with
    - rollback automatique en cas d'erreur
    """
    try:
        yield db.session
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
