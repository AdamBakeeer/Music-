"""new table

Revision ID: 4deae2c95938
Revises: 04d524be3bf5
Create Date: 2024-12-02 23:02:09.851486

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4deae2c95938'
down_revision = '04d524be3bf5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_artist',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.String(length=80), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.artist_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ),
    sa.PrimaryKeyConstraint('user_id', 'artist_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_artist')
    # ### end Alembic commands ###