"""badge system - add fields to BADGES table

Revision ID: b3a1f7e2c904
Revises: da17c899ae66
Create Date: 2026-03-13 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# identifiants de révision
revision: str = 'b3a1f7e2c904'
down_revision: Union[str, None] = 'da17c899ae66'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = [c['name'] for c in inspector.get_columns('BADGES')]

    if 'description' not in columns:
        op.add_column('BADGES', sa.Column('description', sa.String(255), nullable=True))
    if 'icon' not in columns:
        op.add_column('BADGES', sa.Column('icon', sa.String(10), nullable=True))
    if 'score_min' not in columns:
        op.add_column('BADGES', sa.Column('score_min', sa.Integer(), nullable=True))
    if 'score_max' not in columns:
        op.add_column('BADGES', sa.Column('score_max', sa.Integer(), nullable=True))
    if 'category' not in columns:
        op.add_column('BADGES', sa.Column(
            'category',
            sa.Enum(
                'SECURITE_WEB', 'MALWARE', 'RESEAUX',
                'CRYPTOGRAPHIE', 'INGENIERIE_SOCIALE', 'INTRODUCTION_CYBER',
                name='badge_category_enum'
            ),
            nullable=True
        ))
    if 'trigger' not in columns:
        op.add_column('BADGES', sa.Column(
            'trigger',
            sa.Enum('score', 'review', 'review_comment', name='badge_trigger_enum'),
            nullable=False,
            server_default='score'
        ))

    # Rendre idQuiz nullable
    op.alter_column('BADGES', 'idQuiz',
                    existing_type=sa.Integer(),
                    nullable=True)
    # Agrandir name de 45 → 100
    op.alter_column('BADGES', 'name',
                    existing_type=sa.String(45),
                    type_=sa.String(100),
                    existing_nullable=True)


def downgrade() -> None:
    op.drop_column('BADGES', 'trigger')
    op.drop_column('BADGES', 'category')
    op.drop_column('BADGES', 'score_max')
    op.drop_column('BADGES', 'score_min')
    op.drop_column('BADGES', 'icon')
    op.drop_column('BADGES', 'description')
    op.alter_column('BADGES', 'idQuiz',
                    existing_type=sa.Integer(),
                    nullable=False)
    op.alter_column('BADGES', 'name',
                    existing_type=sa.String(100),
                    type_=sa.String(45),
                    existing_nullable=True)
