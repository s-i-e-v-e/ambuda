"""Add ContributorInfo

Revision ID: ed1c7e4af52d
Revises: e22c8a3d348f
Create Date: 2023-04-05 21:07:26.123049

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ed1c7e4af52d"
down_revision = "e22c8a3d348f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "contributor_info",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("contributor_info")
    # ### end Alembic commands ###
