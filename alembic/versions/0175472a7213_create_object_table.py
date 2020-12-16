"""create object table

Revision ID: 0175472a7213
Revises: f84cd93dd71a
Create Date: 2020-12-14 08:59:29.993886

"""
from alembic import op
from sqlalchemy import ForeignKey, Table
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '0175472a7213'
down_revision = 'f84cd93dd71a'
branch_labels = None
depends_on = None

# Declare all models


def upgrade():
    # Create tables
    op.create_table("objects",
                    Column("object", Integer, primary_key=True),
                    Column("content", Text),
                    Column("code", String(50), unique=True),
                    Column("parent", String(100)),
                    Column("is_active", Boolean, default=True),
                    Column("is_deleted", Boolean, default=False),
                    Column("created_at", DateTime, default=datetime.now()),
                    Column("deleted_at", DateTime, nullable=True)
                    )

    op.create_table("folders_objects",
                    Column("folder", Integer, ForeignKey(
                        'folders.folder'), primary_key=True),
                    Column("object", Integer, ForeignKey(
                        'objects.object'), primary_key=True),
                    Column("is_active", Boolean, default=True),
                    Column("is_deleted", Boolean, default=False),
                    Column("created_at", DateTime, default=datetime.now()),
                    Column("deleted_at", DateTime, nullable=True)
                    )


def downgrade():
    op.drop_table("folders_objects")
    op.drop_table("objects")
