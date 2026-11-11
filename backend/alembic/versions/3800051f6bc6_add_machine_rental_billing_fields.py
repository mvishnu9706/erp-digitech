"""add machine rental billing fields

Revision ID: 38000051f6bc
Revises: 6094936f4f8c
Create Date: 2026-09-29
"""

from alembic import op


# ============================================================
# REVISION IDENTIFIERS
# ============================================================

revision = "38000051f6bc"
down_revision = "6094936f4f8c"
branch_labels = None
depends_on = None


# ============================================================
# UPGRADE
# ============================================================

def upgrade():

    # --------------------------------------------------------
    # WARRANTY
    # --------------------------------------------------------

    op.execute("""
        ALTER TABLE machines
        ADD COLUMN IF NOT EXISTS warranty_start_date DATE
    """)

    op.execute("""
        ALTER TABLE machines
        ADD COLUMN IF NOT EXISTS warranty_end_date DATE
    """)

    # --------------------------------------------------------
    # AMC
    # --------------------------------------------------------

    op.execute("""
        ALTER TABLE machines
        ADD COLUMN IF NOT EXISTS amc_start_date DATE
    """)

    op.execute("""
        ALTER TABLE machines
        ADD COLUMN IF NOT EXISTS amc_end_date DATE
    """)

    # --------------------------------------------------------
    # RENTAL ADVANCE
    # --------------------------------------------------------

    op.execute("""
        ALTER TABLE machines
        ADD COLUMN IF NOT EXISTS rental_advance
        NUMERIC(12, 2)
        NOT NULL DEFAULT 0
    """)

    # --------------------------------------------------------
    # FREE PRINTS PER MONTH
    # --------------------------------------------------------

    op.execute("""
        ALTER TABLE machines
        ADD COLUMN IF NOT EXISTS free_prints_per_month
        INTEGER
        NOT NULL DEFAULT 0
    """)

    # --------------------------------------------------------
    # A4 B/W RATE
    # --------------------------------------------------------

    op.execute("""
        ALTER TABLE machines
        ADD COLUMN IF NOT EXISTS a4_bw_rate
        NUMERIC(12, 4)
        NOT NULL DEFAULT 0
    """)

    # --------------------------------------------------------
    # A4 COLOR RATE
    # --------------------------------------------------------

    op.execute("""
        ALTER TABLE machines
        ADD COLUMN IF NOT EXISTS a4_color_rate
        NUMERIC(12, 4)
        NOT NULL DEFAULT 0
    """)

    # --------------------------------------------------------
    # A3 B/W RATE
    # --------------------------------------------------------

    op.execute("""
        ALTER TABLE machines
        ADD COLUMN IF NOT EXISTS a3_bw_rate
        NUMERIC(12, 4)
        NOT NULL DEFAULT 0
    """)

    # --------------------------------------------------------
    # A3 COLOR RATE
    # --------------------------------------------------------

    op.execute("""
        ALTER TABLE machines
        ADD COLUMN IF NOT EXISTS a3_color_rate
        NUMERIC(12, 4)
        NOT NULL DEFAULT 0
    """)


# ============================================================
# DOWNGRADE
# ============================================================

def downgrade():

    op.execute("""
        ALTER TABLE machines
        DROP COLUMN IF EXISTS a3_color_rate
    """)

    op.execute("""
        ALTER TABLE machines
        DROP COLUMN IF EXISTS a3_bw_rate
    """)

    op.execute("""
        ALTER TABLE machines
        DROP COLUMN IF EXISTS a4_color_rate
    """)

    op.execute("""
        ALTER TABLE machines
        DROP COLUMN IF EXISTS a4_bw_rate
    """)

    op.execute("""
        ALTER TABLE machines
        DROP COLUMN IF EXISTS free_prints_per_month
    """)

    op.execute("""
        ALTER TABLE machines
        DROP COLUMN IF EXISTS rental_advance
    """)

    op.execute("""
        ALTER TABLE machines
        DROP COLUMN IF EXISTS amc_end_date
    """)

    op.execute("""
        ALTER TABLE machines
        DROP COLUMN IF EXISTS amc_start_date
    """)

    op.execute("""
        ALTER TABLE machines
        DROP COLUMN IF EXISTS warranty_end_date
    """)

    op.execute("""
        ALTER TABLE machines
        DROP COLUMN IF EXISTS warranty_start_date
    """)