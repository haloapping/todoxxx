"""create table

Revision ID: 7cc02171dc03
Revises: 86d613bc80be
Create Date: 2025-11-23 11:15:26.882870

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7cc02171dc03"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE users (
            id text NOT NULL,
            username text NOT NULL,
            email text NOT NULL,
            password text NOT NULL,
            created_at timestamptz DEFAULT now() NULL,
            updated_at timestamptz NULL,
            CONSTRAINT users_email_key UNIQUE (email),
            CONSTRAINT users_password_key UNIQUE (password),
            CONSTRAINT users_pkey PRIMARY KEY (id),
            CONSTRAINT users_username_key UNIQUE (username)
        );
                
        CREATE TABLE tasks (
            id text NOT NULL,
            user_id text NOT NULL,
            title text NOT NULL,
            description text NULL,
            created_at timestamptz DEFAULT now() NULL,
            updated_at timestamptz NULL,
            CONSTRAINT tasks_pkey PRIMARY KEY (id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
