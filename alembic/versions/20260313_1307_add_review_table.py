"""add review table

Revision ID: da17c899ae66
Revises:
Create Date: 2026-03-13 13:07:02.391560

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# identifiants de révision
revision: str = 'da17c899ae66'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # La table REVIEW a été créée lors de la première tentative (DDL non transactionnel MySQL).
    # On vérifie son existence avant de la recréer pour éviter une erreur.
    from alembic import op as _op
    bind = _op.get_bind()
    inspector = sa.inspect(bind)
    if 'REVIEW' not in inspector.get_table_names():
        op.create_table('REVIEW',
            sa.Column('idREVIEW', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('idUSERinReview', sa.Integer(), nullable=False),
            sa.Column('idQUIZinReview', sa.Integer(), nullable=False),
            sa.Column('rating', sa.Integer(), nullable=False),
            sa.Column('comment', sa.Text(), nullable=True),
            sa.Column('date', sa.Date(), nullable=True),
            sa.ForeignKeyConstraint(['idQUIZinReview'], ['QUIZ.idQUIZ'], ),
            sa.ForeignKeyConstraint(['idUSERinReview'], ['USER.idUSER'], ),
            sa.PrimaryKeyConstraint('idREVIEW'),
            sa.UniqueConstraint('idUSERinReview', 'idQUIZinReview', name='unique_user_quiz_review')
        )


def downgrade() -> None:
    op.drop_table('REVIEW')
