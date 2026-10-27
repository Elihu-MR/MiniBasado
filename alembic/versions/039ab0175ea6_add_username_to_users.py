"""add username to users

Revision ID: 039ab0175ea6
Revises: 61948fb944f6
Create Date: 2026-10-08 21:02:05.947171

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

revision: str = '039ab0175ea6'
down_revision: Union[str, Sequence[str], None] = '61948fb944f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Soltar la FK vieja (refrigerador -> usuario)
    op.drop_constraint('refrigerador_usuario_id_fkey', 'refrigerador', type_='foreignkey')

    # 2. Agregar columnas nuevas a users como NULLABLE primero
    op.add_column('users', sa.Column('username', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True))
    op.add_column('users', sa.Column('hashed_password', sqlmodel.sql.sqltypes.AutoString(), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column('users', sa.Column('profile_pic', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True))

    # 3. Pasar datos de las columnas viejas a las nuevas
    op.execute("UPDATE users SET username = 'user_' || id, hashed_password = password_hash")

    # 4. Ahora sí, NOT NULL + índice único
    op.alter_column('users', 'username', nullable=False)
    op.alter_column('users', 'hashed_password', nullable=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # 5. Quitar columnas viejas
    op.drop_column('users', 'password_hash')
    op.drop_column('users', 'phone')
    op.drop_column('users', 'name')

    # 6. Limpiar refrigeradores con dueño inexistente y crear FK nueva -> users
    op.execute("UPDATE refrigerador SET usuario_id = NULL WHERE usuario_id NOT IN (SELECT id FROM users)")
    op.create_foreign_key('refrigerador_usuario_id_fkey', 'refrigerador', 'users', ['usuario_id'], ['id'])

    # 7. AL FINAL: borrar la tabla vieja
    op.drop_index(op.f('ix_usuario_email'), table_name='usuario')
    op.drop_index(op.f('ix_usuario_username'), table_name='usuario')
    op.drop_table('usuario')


def downgrade() -> None:
    op.create_table('usuario',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('username', sa.VARCHAR(length=50), nullable=False),
        sa.Column('email', sa.VARCHAR(), nullable=False),
        sa.Column('hashed_password', sa.VARCHAR(), nullable=False),
        sa.Column('is_active', sa.BOOLEAN(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), nullable=False),
        sa.Column('profile_pic', sa.VARCHAR(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id', name='usuario_pkey'),
    )
    op.create_index(op.f('ix_usuario_username'), 'usuario', ['username'], unique=True)
    op.create_index(op.f('ix_usuario_email'), 'usuario', ['email'], unique=True)

    op.drop_constraint('refrigerador_usuario_id_fkey', 'refrigerador', type_='foreignkey')
    op.execute("UPDATE refrigerador SET usuario_id = NULL")
    op.create_foreign_key('refrigerador_usuario_id_fkey', 'refrigerador', 'usuario', ['usuario_id'], ['id'])

    op.add_column('users', sa.Column('name', sa.VARCHAR(length=120), nullable=True))
    op.add_column('users', sa.Column('phone', sa.VARCHAR(length=40), nullable=True))
    op.add_column('users', sa.Column('password_hash', sa.VARCHAR(length=255), nullable=True))
    op.execute("UPDATE users SET name = username, password_hash = hashed_password")
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_column('users', 'profile_pic')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'hashed_password')
    op.drop_column('users', 'username')