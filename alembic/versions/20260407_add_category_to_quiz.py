"""add category column to QUIZ table

Revision ID: a1c2d3e4f506
Revises: b3a1f7e2c904
Create Date: 2026-04-07 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# identifiants de révision
revision: str = 'a1c2d3e4f506'
down_revision: Union[str, None] = 'b3a1f7e2c904'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Vérifier si la colonne existe déjà avant de l'ajouter
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('QUIZ')]

    if 'category' not in columns:
        op.add_column(
            'QUIZ',
            sa.Column(
                'category',
                sa.Enum(
                    'SECURITE_WEB',
                    'MALWARE',
                    'RESEAUX',
                    'CRYPTOGRAPHIE',
                    'INGENIERIE_SOCIALE',
                    'INTRODUCTION_CYBER',
                    name='quiz_category_enum'
                ),
                nullable=True,
            )
        )


def downgrade() -> None:
    op.drop_column('QUIZ', 'category')
