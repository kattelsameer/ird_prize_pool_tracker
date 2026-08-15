"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-15

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "consumer_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("display_name", sa.String(120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "networks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_networks_name", "networks", ["name"], unique=True)

    op.create_table(
        "sync_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("records_received", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("records_inserted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("records_updated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("records_skipped", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.String(2000), nullable=True),
    )
    op.create_index("ix_sync_runs_status", "sync_runs", ["status"])

    op.create_table(
        "coupons",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("profile_id", sa.String(36), sa.ForeignKey("consumer_profiles.id"), nullable=False),
        sa.Column("coupon_id", sa.String(160), nullable=False),
        sa.Column("coupon_code", sa.String(64), nullable=False),
        sa.Column("normalized_coupon_code", sa.String(64), nullable=False),
        sa.Column("transaction_date", sa.Date(), nullable=True),
        sa.Column("fiscal_year", sa.String(16), nullable=True),
        sa.Column("network", sa.String(80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_coupons_profile_id", "coupons", ["profile_id"])
    op.create_index("ix_coupons_coupon_id", "coupons", ["coupon_id"])
    op.create_index("ix_coupons_normalized_coupon_code", "coupons", ["normalized_coupon_code"])
    op.create_index("ix_coupons_transaction_date", "coupons", ["transaction_date"])
    op.create_index("ix_coupons_fiscal_year", "coupons", ["fiscal_year"])
    op.create_index("ix_coupons_network", "coupons", ["network"])

    op.create_table(
        "prize_pool_winners",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("source_record_id", sa.String(200), nullable=False),
        sa.Column("draw_id", sa.String(120), nullable=False),
        sa.Column("category_title_en", sa.String(120), nullable=True),
        sa.Column("category_title_ne", sa.String(200), nullable=True),
        sa.Column("draw_type", sa.String(40), nullable=True),
        sa.Column("draw_title_en", sa.String(400), nullable=True),
        sa.Column("draw_title_ne", sa.String(400), nullable=True),
        sa.Column("eligible_from", sa.Date(), nullable=True),
        sa.Column("eligible_to", sa.Date(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("claim_deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column("claim_open", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("winner_rank", sa.Integer(), nullable=False),
        sa.Column("prize_fiscal_year_code", sa.String(16), nullable=False),
        sa.Column("prize_coupon_number", sa.String(64), nullable=False),
        sa.Column("normalized_coupon_code", sa.String(64), nullable=False),
        sa.Column("raw_draw_json", sa.JSON(), nullable=False),
        sa.Column("source", sa.String(20), nullable=False, server_default="ird_live"),
        sa.Column("source_sync_id", sa.String(36), sa.ForeignKey("sync_runs.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("draw_id", "prize_coupon_number", name="uq_draw_coupon"),
    )
    op.create_index("ix_prize_pool_winners_source_record_id", "prize_pool_winners", ["source_record_id"])
    op.create_index("ix_prize_pool_winners_draw_id", "prize_pool_winners", ["draw_id"])
    op.create_index("ix_prize_pool_winners_eligible_from", "prize_pool_winners", ["eligible_from"])
    op.create_index("ix_prize_pool_winners_eligible_to", "prize_pool_winners", ["eligible_to"])
    op.create_index("ix_prize_pool_winners_claim_deadline", "prize_pool_winners", ["claim_deadline"])
    op.create_index(
        "ix_prize_pool_winners_prize_fiscal_year_code", "prize_pool_winners", ["prize_fiscal_year_code"]
    )
    op.create_index(
        "ix_prize_pool_winners_normalized_coupon_code", "prize_pool_winners", ["normalized_coupon_code"]
    )
    op.create_index("ix_prize_pool_winners_source", "prize_pool_winners", ["source"])

    op.create_table(
        "notifications",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("profile_id", sa.String(36), sa.ForeignKey("consumer_profiles.id"), nullable=False),
        sa.Column("type", sa.String(40), nullable=False),
        sa.Column("coupon_id", sa.String(36), nullable=True),
        sa.Column("draw_id", sa.String(120), nullable=True),
        sa.Column("message", sa.String(500), nullable=False),
        sa.Column("dedup_key", sa.String(300), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_notifications_profile_id", "notifications", ["profile_id"])
    op.create_index("ix_notifications_type", "notifications", ["type"])
    op.create_index("ix_notifications_created_at", "notifications", ["created_at"])
    op.create_index("ix_notifications_dedup_key", "notifications", ["dedup_key"], unique=True)

    op.create_table(
        "app_settings",
        sa.Column("id", sa.String(10), primary_key=True),
        sa.Column("notify_new_match", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notify_claim_expiring", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notify_claim_expired", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notify_sync_updates", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notify_sync_failures", sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade() -> None:
    op.drop_table("app_settings")
    op.drop_index("ix_notifications_dedup_key", table_name="notifications")
    op.drop_index("ix_notifications_created_at", table_name="notifications")
    op.drop_index("ix_notifications_type", table_name="notifications")
    op.drop_index("ix_notifications_profile_id", table_name="notifications")
    op.drop_table("notifications")

    op.drop_index("ix_prize_pool_winners_source", table_name="prize_pool_winners")
    op.drop_index("ix_prize_pool_winners_normalized_coupon_code", table_name="prize_pool_winners")
    op.drop_index("ix_prize_pool_winners_prize_fiscal_year_code", table_name="prize_pool_winners")
    op.drop_index("ix_prize_pool_winners_claim_deadline", table_name="prize_pool_winners")
    op.drop_index("ix_prize_pool_winners_eligible_to", table_name="prize_pool_winners")
    op.drop_index("ix_prize_pool_winners_eligible_from", table_name="prize_pool_winners")
    op.drop_index("ix_prize_pool_winners_draw_id", table_name="prize_pool_winners")
    op.drop_index("ix_prize_pool_winners_source_record_id", table_name="prize_pool_winners")
    op.drop_table("prize_pool_winners")

    op.drop_index("ix_coupons_network", table_name="coupons")
    op.drop_index("ix_coupons_fiscal_year", table_name="coupons")
    op.drop_index("ix_coupons_transaction_date", table_name="coupons")
    op.drop_index("ix_coupons_normalized_coupon_code", table_name="coupons")
    op.drop_index("ix_coupons_coupon_id", table_name="coupons")
    op.drop_index("ix_coupons_profile_id", table_name="coupons")
    op.drop_table("coupons")

    op.drop_index("ix_sync_runs_status", table_name="sync_runs")
    op.drop_table("sync_runs")

    op.drop_index("ix_networks_name", table_name="networks")
    op.drop_table("networks")

    op.drop_table("consumer_profiles")
