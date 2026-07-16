"""Add durable, hashed email OTP challenges.

Revision ID: 002
Revises: 001
"""
from alembic import op
import sqlalchemy as sa


revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "email_otps",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("otp_hash", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_email_otps_email", "email_otps", ["email"])
    op.create_index("ix_email_otps_expires_at", "email_otps", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_email_otps_expires_at", table_name="email_otps")
    op.drop_index("ix_email_otps_email", table_name="email_otps")
    op.drop_table("email_otps")
