"""create platform table

Revision ID: f84cd93dd71a
Revises: 
Create Date: 2020-10-30 12:33:58.883611

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import ForeignKey, orm, Table
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()


# revision identifiers, used by Alembic.
revision = 'f84cd93dd71a'
down_revision = None
branch_labels = None
depends_on = None


PLATFORMS = [
    {u'title': "Drive", u"slug": "drive"},
    {u'title': "Photos", u"slug": "photos"}
]
# Declare all models


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
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now())
    deleted_at = Column(DateTime, nullable=True)


def upgrade():
    _bind = op.get_bind()
    _session = orm.Session(bind=_bind)

    # Create tables
    op.create_table("platforms",
                    Column("platform", Integer, primary_key=True),
                    Column("title", String(50), nullable=False),
                    Column("slug", String(50), unique=True, nullable=False),
                    Column("is_active", Boolean, default=True),
                    Column("is_deleted", Boolean, default=False),
                    Column("created_at", DateTime, default=datetime.now()),
                    Column("deleted_at", DateTime, nullable=True)
                    )
    op.add_column("folders", sa.Column('platform', sa.Integer,
                                       sa.ForeignKey('platforms.platform'))
                  )
    op.add_column("files", sa.Column('width', sa.Integer, default=None))
    op.add_column("files", sa.Column('height', sa.Integer, default=None))
    # create all default languages
    _platforms = [
        Platform(
            title=_platform["title"],
            slug=_platform["slug"],
        ) for _platform in PLATFORMS
    ]
    _session.add_all(_platforms)
    _session.flush()
    # set languages for novels
    for _folder in _session.query(Folder):
        _folder.platform = _platforms[0].platform
    _session.commit()
    _session.close()


def downgrade():
    op.drop_column('folders', 'platform')
    op.drop_column('files', 'width')
    op.drop_column('files', 'height')
    op.drop_table("platforms")
