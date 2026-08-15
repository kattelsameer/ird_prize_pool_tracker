"""add user auth: users table, per-user consumer_profiles, per-profile app_settings

This introduces real accounts. Previously the app operated against one
implicit, anonymous "singleton" profile (CLAUDE.md §23's initial "keep it
simple" allowance) with a singleton app_settings row. Neither can be safely
attributed to a specific new user account, so this migration removes them --
an intentional, one-time breaking change, acceptable because no real
multi-user deployment of this app has happened yet. Coupons/notifications
belonging to that old anonymous profile are removed via the FK cascade
implied by deleting the profile row; nothing about *published* IRD data
(prize_pool_winners, networks, sync_runs) is touched.

Revision ID: 0002_add_user_auth
Revises: 0001_initial
Create Date: 2026-08-15

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002_add_user_auth"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # Old anonymous data can't be attributed to any new account -- see module
    # docstring. Delete child rows first (SQLite has no FK-cascade-on-delete
    # enabled by default), then the profile rows themselves.
    op.execute("DELETE FROM coupons")
    op.execute("DELETE FROM notifications")
    op.execute("DELETE FROM app_settings")
    op.execute("DELETE FROM consumer_profiles")

    with op.batch_alter_table("consumer_profiles") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.String(36), nullable=False))
        batch_op.create_foreign_key(
            "fk_consumer_profiles_user_id", "users", ["user_id"], ["id"]
        )
        batch_op.create_index("ix_consumer_profiles_user_id", ["user_id"], unique=True)

    with op.batch_alter_table("app_settings") as batch_op:
        # Widen id from String(10) (fit "singleton") to String(36) (fit a UUID) --
        # SQLite doesn't enforce this either way, but Postgres would.
        batch_op.alter_column("id", type_=sa.String(36), existing_type=sa.String(10))
        batch_op.add_column(sa.Column("profile_id", sa.String(36), nullable=False))
        batch_op.create_foreign_key(
            "fk_app_settings_profile_id", "consumer_profiles", ["profile_id"], ["id"]
        )
        batch_op.create_index("ix_app_settings_profile_id", ["profile_id"], unique=True)


def downgrade() -> None:
    with op.batch_alter_table("app_settings") as batch_op:
        batch_op.drop_index("ix_app_settings_profile_id")
        batch_op.drop_constraint("fk_app_settings_profile_id", type_="foreignkey")
        batch_op.drop_column("profile_id")
        batch_op.alter_column("id", type_=sa.String(10), existing_type=sa.String(36))

    with op.batch_alter_table("consumer_profiles") as batch_op:
        batch_op.drop_index("ix_consumer_profiles_user_id")
        batch_op.drop_constraint("fk_consumer_profiles_user_id", type_="foreignkey")
        batch_op.drop_column("user_id")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
