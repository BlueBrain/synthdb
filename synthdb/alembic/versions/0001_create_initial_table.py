"""Create initial table.

Revision ID: 0001
Revises:
Create Date: 2022-03-29 12:24:02.695521

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Operations to perform an upgrade."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "synthesis_inputs",
        sa.Column("brain_region", sa.String(), nullable=False),
        sa.Column("mtype", sa.String(), nullable=False),
        sa.Column("luigi_config", sa.String(), nullable=False),
        sa.Column("distributions_path", sa.String(), nullable=False),
        sa.Column("parameters_path", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("brain_region", "mtype", "luigi_config"),
    )
    # ### end Alembic commands ###


def downgrade():
    """Operations to perform an downgrade."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("synthesis_inputs")
    # ### end Alembic commands ###
