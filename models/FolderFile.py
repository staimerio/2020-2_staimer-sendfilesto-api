"""Model for folder with files"""

# SQLAlchemy
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy import ForeignKey, DateTime, Boolean

# SQLAlchemy_serializer
from sqlalchemy_serializer import SerializerMixin

# Services
from services.sqlalchemy.base import Base

# Time
from datetime import datetime


class FolderFile(Base, SerializerMixin):
    __tablename__ = "folders_files"

    folder = Column(Integer, ForeignKey('folders.folder'), primary_key=True)
    file = Column(Integer, ForeignKey('files.file'), primary_key=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now())
    deleted_at = Column(DateTime, nullable=True)

    """Serialize settings"""
    serialize_only = (
        'folder', 'file'
    )
