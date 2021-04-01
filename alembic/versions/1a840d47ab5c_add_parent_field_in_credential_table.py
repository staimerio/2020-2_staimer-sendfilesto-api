"""add parent field in credential table

Revision ID: 1a840d47ab5c
Revises: 965d9eb4b2fd
Create Date: 2021-03-31 13:39:23.645848

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a840d47ab5c'
down_revision = '965d9eb4b2fd'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("credentials", sa.Column(
        'parent', sa.String(100), nullable=True))


def downgrade():
    op.drop_column('credentials', 'parent')
