"""new 

Revision ID: 28f59ecddbe1
Revises: 21a1f3720926
Create Date: 2024-12-03 04:52:20.892173

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '28f59ecddbe1'
down_revision = '21a1f3720926'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index('ix_user_firstname')
        batch_op.create_index(batch_op.f('ix_user_firstname'), ['firstname'], unique=False)
        batch_op.drop_index('ix_user_lastname')
        batch_op.create_index(batch_op.f('ix_user_lastname'), ['lastname'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_lastname'))
        batch_op.create_index('ix_user_lastname', ['lastname'], unique=1)
        batch_op.drop_index(batch_op.f('ix_user_firstname'))
        batch_op.create_index('ix_user_firstname', ['firstname'], unique=1)

    # ### end Alembic commands ###
