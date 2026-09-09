"""clean_audit_and_soft_delete

Revision ID: 2a3b4c5d6e7f
Revises: 1dd7d9a9616c
Create Date: 2026-09-09 12:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a3b4c5d6e7f'
down_revision: Union[str, None] = '1dd7d9a9616c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. Users table ────────────────────────────────────────────────────────
    op.add_column(
        'users',
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
    )

    # ── 2. HCPs table ─────────────────────────────────────────────────────────
    op.add_column(
        'hcps',
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
    )
    op.add_column(
        'hcps',
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
    )
    op.add_column(
        'hcps',
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        'hcps',
        sa.Column('created_by', sa.BigInteger(), nullable=True),
    )
    op.add_column(
        'hcps',
        sa.Column('updated_by', sa.BigInteger(), nullable=True),
    )
    op.add_column(
        'hcps',
        sa.Column('deleted_by', sa.BigInteger(), nullable=True),
    )
    op.create_foreign_key(
        'fk_hcps_created_by_users',
        'hcps',
        'users',
        ['created_by'],
        ['id'],
        ondelete='SET NULL',
    )
    op.create_foreign_key(
        'fk_hcps_updated_by_users',
        'hcps',
        'users',
        ['updated_by'],
        ['id'],
        ondelete='SET NULL',
    )
    op.create_foreign_key(
        'fk_hcps_deleted_by_users',
        'hcps',
        'users',
        ['deleted_by'],
        ['id'],
        ondelete='SET NULL',
    )
    op.create_index(op.f('ix_hcps_deleted_at'), 'hcps', ['deleted_at'], unique=False)

    # ── 3. Interactions table ─────────────────────────────────────────────────
    op.add_column(
        'interactions',
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        'interactions',
        sa.Column('created_by', sa.BigInteger(), nullable=True),
    )
    op.add_column(
        'interactions',
        sa.Column('updated_by', sa.BigInteger(), nullable=True),
    )
    op.add_column(
        'interactions',
        sa.Column('deleted_by', sa.BigInteger(), nullable=True),
    )
    op.create_foreign_key(
        'fk_interactions_created_by_users',
        'interactions',
        'users',
        ['created_by'],
        ['id'],
        ondelete='SET NULL',
    )
    op.create_foreign_key(
        'fk_interactions_updated_by_users',
        'interactions',
        'users',
        ['updated_by'],
        ['id'],
        ondelete='SET NULL',
    )
    op.create_foreign_key(
        'fk_interactions_deleted_by_users',
        'interactions',
        'users',
        ['deleted_by'],
        ['id'],
        ondelete='SET NULL',
    )
    op.create_index(
        op.f('ix_interactions_deleted_at'),
        'interactions',
        ['deleted_at'],
        unique=False,
    )

    # ── 4. FollowUps table ───────────────────────────────────────────────────
    op.add_column(
        'follow_ups',
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
    )
    op.add_column(
        'follow_ups',
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
    )
    op.add_column(
        'follow_ups',
        sa.Column('created_by', sa.BigInteger(), nullable=True),
    )
    op.add_column(
        'follow_ups',
        sa.Column('updated_by', sa.BigInteger(), nullable=True),
    )
    op.create_foreign_key(
        'fk_follow_ups_created_by_users',
        'follow_ups',
        'users',
        ['created_by'],
        ['id'],
        ondelete='SET NULL',
    )
    op.create_foreign_key(
        'fk_follow_ups_updated_by_users',
        'follow_ups',
        'users',
        ['updated_by'],
        ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    # ── 4. FollowUps table ───────────────────────────────────────────────────
    op.drop_constraint('fk_follow_ups_updated_by_users', 'follow_ups', type_='foreignkey')
    op.drop_constraint('fk_follow_ups_created_by_users', 'follow_ups', type_='foreignkey')
    op.drop_column('follow_ups', 'updated_by')
    op.drop_column('follow_ups', 'created_by')
    op.drop_column('follow_ups', 'updated_at')
    op.drop_column('follow_ups', 'created_at')

    # ── 3. Interactions table ─────────────────────────────────────────────────
    op.drop_index(op.f('ix_interactions_deleted_at'), table_name='interactions')
    op.drop_constraint('fk_interactions_deleted_by_users', 'interactions', type_='foreignkey')
    op.drop_constraint('fk_interactions_updated_by_users', 'interactions', type_='foreignkey')
    op.drop_constraint('fk_interactions_created_by_users', 'interactions', type_='foreignkey')
    op.drop_column('interactions', 'deleted_by')
    op.drop_column('interactions', 'updated_by')
    op.drop_column('interactions', 'created_by')
    op.drop_column('interactions', 'deleted_at')

    # ── 2. HCPs table ─────────────────────────────────────────────────────────
    op.drop_index(op.f('ix_hcps_deleted_at'), table_name='hcps')
    op.drop_constraint('fk_hcps_deleted_by_users', 'hcps', type_='foreignkey')
    op.drop_constraint('fk_hcps_updated_by_users', 'hcps', type_='foreignkey')
    op.drop_constraint('fk_hcps_created_by_users', 'hcps', type_='foreignkey')
    op.drop_column('hcps', 'deleted_by')
    op.drop_column('hcps', 'updated_by')
    op.drop_column('hcps', 'created_by')
    op.drop_column('hcps', 'deleted_at')
    op.drop_column('hcps', 'updated_at')
    op.drop_column('hcps', 'created_at')

    # ── 1. Users table ────────────────────────────────────────────────────────
    op.drop_column('users', 'updated_at')
