# Alembic — Gestion des migrations de base de données

## Qu'est-ce qu'Alembic ?

Alembic est l'outil de migration de référence dans l'écosystème Python. Il est développé par le même auteur que SQLAlchemy (Mike Bayer) et s'intègre naturellement avec Flask-SQLAlchemy.

Une **migration** est un fichier versionné qui décrit une modification du schéma de la base de données. Chaque migration contient :
- Une fonction `upgrade()` : ce qu'il faut faire pour appliquer la modification
- Une fonction `downgrade()` : ce qu'il faut faire pour l'annuler

Alembic maintient une table `alembic_version` dans la base de données pour savoir quelle migration a été appliquée en dernier.

---

## Pourquoi Alembic pour Cyber-hoot ?

Avant Alembic, toutes les modifications de schéma étaient faites **à la main dans Adminer** (des `ALTER TABLE` saisis manuellement). Cette approche posait plusieurs problèmes :

| Problème | Impact sur Cyber-hoot |
|----------|----------------------|
| Pas de traçabilité | Impossible de savoir quelles colonnes ont été ajoutées et quand |
| Pas de rollback | Une erreur de migration ne peut pas être annulée proprement |
| Synchronisation difficile | Si quelqu'un récupère le projet, il ne sait pas quelles migrations appliquer |
| Risque d'oubli | Des colonnes manquantes causaient des `OperationalError` au démarrage |

Exemple concret : les erreurs `Unknown column 'QUIZ.category'` et `Unknown column 'RESULT.answer'` rencontrées en développement auraient été évitées si les migrations avaient été versionnées dès le départ.

---

## Structure mise en place

```
cyber-hoot/
├── alembic.ini              # Configuration Alembic (chemin des migrations, logging)
├── alembic/
│   ├── env.py               # Intégration Flask app factory + SQLAlchemy
│   ├── script.py.mako       # Template pour générer les fichiers de migration
│   └── versions/            # Migrations versionnées (fichiers Python)
│       └── xxxx_nom.py      # Exemple de migration
```

---

## Comment ça s'intègre avec Flask

Le fichier clé est `alembic/env.py`. Il fait le lien entre Alembic et l'application Flask :

```python
from app import create_app
from app.extensions import db

flask_app = create_app()

with flask_app.app_context():
    config.set_main_option("sqlalchemy.url", flask_app.config["SQLALCHEMY_DATABASE_URI"])
    target_metadata = db.metadata
```

L'URL de la base de données n'est **pas écrite en dur** dans `alembic.ini` — elle est lue dynamiquement depuis la configuration Flask (qui elle-même lit les variables d'environnement et les Docker secrets).

---

## Commandes principales

Toutes les commandes s'exécutent depuis le conteneur Docker :

```bash
# Entrer dans le conteneur
docker exec -it <nom_du_conteneur_app> bash

# Voir l'état des migrations
alembic current          # version actuellement appliquée
alembic history          # historique complet

# Créer une nouvelle migration manuellement
alembic revision -m "add_column_xyz_to_table"

# Créer une migration automatiquement (depuis les modèles SQLAlchemy)
alembic revision --autogenerate -m "description_du_changement"

# Appliquer toutes les migrations en attente
alembic upgrade head

# Appliquer uniquement la prochaine migration
alembic upgrade +1

# Annuler la dernière migration
alembic downgrade -1

# Revenir à zéro (annuler toutes les migrations)
alembic downgrade base
```

---

## Workflow : comment modifier la base de données

Désormais, **ne plus modifier la base dans Adminer directement**. Le workflow correct est :

```
1. Modifier le modèle dans app/models/models.py
       │
       ▼
2. Générer la migration automatiquement
   alembic revision --autogenerate -m "description"
       │
       ▼
3. Vérifier le fichier généré dans alembic/versions/
   (toujours relire avant d'appliquer !)
       │
       ▼
4. Appliquer la migration
   alembic upgrade head
       │
       ▼
5. Commiter le fichier de migration dans Git
   → Tout le monde peut appliquer la même migration
```

---

## Mise en place initiale (projet existant)

Cyber-hoot avait déjà une base de données avec des données avant l'introduction d'Alembic. Pour initialiser Alembic sur un projet existant sans perdre les données :

```bash
# 1. Générer une migration "baseline" qui représente l'état actuel des modèles
alembic revision --autogenerate -m "baseline_initial_schema"

# 2. Marquer cette migration comme déjà appliquée (les tables existent déjà)
#    Sans cette étape, alembic essaierait de recréer toutes les tables !
alembic stamp head
```

Après cette étape, Alembic connaît l'état actuel. Les prochaines modifications de modèles généreront des migrations incrementales.

---

## Exemple de migration

Voici à quoi ressemble un fichier de migration généré automatiquement.

Imaginons qu'on ajoute un champ `hint_text` à la table `QUESTION` :

**Étape 1** — Modifier le modèle :
```python
# app/models/models.py
class Question(db.Model):
    QuestionText = db.Column(db.String(500), nullable=True)
    explanation = db.Column(db.Text, nullable=True)
    hint_text = db.Column(db.Text, nullable=True)  # ← nouveau champ
```

**Étape 2** — Générer la migration :
```bash
alembic revision --autogenerate -m "add_hint_text_to_question"
```

**Étape 3** — Fichier généré dans `alembic/versions/` :
```python
"""add hint_text to question

Revision ID: a1b2c3d4
Revises: f9e8d7c6
Create Date: 2026-03-13
"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4'
down_revision = 'f9e8d7c6'

def upgrade() -> None:
    op.add_column('QUESTION', sa.Column('hint_text', sa.Text(), nullable=True))

def downgrade() -> None:
    op.drop_column('QUESTION', 'hint_text')
```

**Étape 4** — Appliquer :
```bash
alembic upgrade head
```

---

## Points importants

- **Ne jamais modifier un fichier de migration déjà appliqué** — créer une nouvelle migration à la place
- **Toujours relire la migration autogénérée** avant de l'appliquer — Alembic peut parfois détecter de faux changements (notamment sur les types ENUM MySQL)
- **Commiter les fichiers de migration dans Git** — c'est leur raison d'être
- **Ne plus faire d'ALTER TABLE manuels dans Adminer** — sauf en cas d'urgence en production, et dans ce cas créer la migration correspondante ensuite
