"""Add autobooking to session

Revision ID: 648240c30a17
Revises: 52ba21cf3b45
Create Date: 2024-06-09 14:36:52.170838

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '648240c30a17'
down_revision: Union[str, None] = '52ba21cf3b45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sessions', sa.Column('auto_booking', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sessions', 'auto_booking')
    # ### end Alembic commands ###
