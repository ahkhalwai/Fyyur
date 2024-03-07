"""empty message

Revision ID: a553574d0a27
Revises: 71a72a4e5457
Create Date: 2024-03-07 19:48:54.885541

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a553574d0a27'
down_revision = '71a72a4e5457'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.alter_column('genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Artist', schema=None) as batch_op:
        batch_op.alter_column('genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)

    # ### end Alembic commands ###