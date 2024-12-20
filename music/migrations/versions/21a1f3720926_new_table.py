"""new table

Revision ID: 21a1f3720926
Revises: 4deae2c95938
Create Date: 2024-12-02 23:07:14.038902

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '21a1f3720926'
down_revision = '4deae2c95938'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('genre',
    sa.Column('genre_id', sa.Integer(), nullable=False),
    sa.Column('genre_name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('genre_id'),
    sa.UniqueConstraint('genre_name')
    )
    op.create_table('user_genre',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('genre_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['genre_id'], ['genre.genre_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ),
    sa.PrimaryKeyConstraint('user_id', 'genre_id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('preferred_artists')
        batch_op.drop_column('preferred_genres')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('preferred_genres', sa.VARCHAR(length=200), nullable=True))
        batch_op.add_column(sa.Column('preferred_artists', sa.VARCHAR(length=200), nullable=True))

    op.drop_table('user_genre')
    op.drop_table('genre')
    # ### end Alembic commands ###
