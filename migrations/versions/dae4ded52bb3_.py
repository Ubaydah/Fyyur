"""empty message

Revision ID: dae4ded52bb3
Revises: efa53be49a7e
Create Date: 2022-05-24 10:19:18.005824

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dae4ded52bb3'
down_revision = 'efa53be49a7e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('genres', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'genres')
    # ### end Alembic commands ###