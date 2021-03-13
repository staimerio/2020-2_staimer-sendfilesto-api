"""create credential table

Revision ID: 965d9eb4b2fd
Revises: 0175472a7213
Create Date: 2021-03-07 19:23:07.386898

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import ForeignKey, orm, Table
from sqlalchemy import Column, Integer, String, DateTime, Boolean, LargeBinary, Text
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# revision identifiers, used by Alembic.
revision = '965d9eb4b2fd'
down_revision = '0175472a7213'
branch_labels = None
depends_on = None


class Credential(Base):
    """Platform Model"""
    __tablename__ = "credentials"

    """Attributes"""
    credential = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    key = Column(Text)    
    picky = Column(LargeBinary(length=5242880))
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now())
    deleted_at = Column(DateTime, nullable=True)

class Platform(Base):
    """Platform Model"""
    __tablename__ = "platforms"

    """Attributes"""
    platform = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now())
    deleted_at = Column(DateTime, nullable=True)

class Folder(Base):
    """Folder Model"""
    __tablename__ = "folders"

    """Attributes"""
    folder = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True)
    description = Column(String(280), default="")
    parent = Column(String(100), nullable=True)
    platform = Column(Integer, ForeignKey('platforms.platform'))
    credential = Column(Integer, ForeignKey('credentials.credential'))
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now())
    deleted_at = Column(DateTime, nullable=True)


def upgrade():
    _bind = op.get_bind()
    _session = orm.Session(bind=_bind)

    # Create tables
    op.create_table("credentials",
                    Column("credential", Integer, primary_key=True),
                    Column("title", String(50), nullable=False),
                    Column("key", Text),
                    Column("picky", LargeBinary(length=5242880)),
                    Column("is_active", Boolean, default=True),
                    Column("is_deleted", Boolean, default=False),
                    Column("created_at", DateTime, default=datetime.now()),
                    Column("deleted_at", DateTime, nullable=True)
                    )
    op.add_column("folders", sa.Column('credential', sa.Integer,
                                       sa.ForeignKey('credentials.credential'))
                  )


    _session.flush()
    # set languages for novels
    for _folder in _session.query(Folder):
        _folder.credential = 1
    _session.commit()
    _session.close()


def downgrade():
    op.drop_column('folders', 'credential')
    op.drop_table("credentials")
