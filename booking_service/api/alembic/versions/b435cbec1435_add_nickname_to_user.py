"""Add nickname to user

Revision ID: b435cbec1435
Revises: 93b0a792c346
Create Date: 2024-06-08 16:08:14.800496

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b435cbec1435'
down_revision: Union[str, None] = '93b0a792c346'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('nickname', sa.String(), nullable=True))
    # Adding the foreign key constraint on seat_id in the reservations table
    op.create_foreign_key('fk_reservations_seat_id', 'reservations', 'seats', ['seat_id'], ['id'], ondelete='SET NULL')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_reservations_seat_id', 'reservations', type_='foreignkey')
    op.drop_column('users', 'nickname')
    # ### end Alembic commands ###