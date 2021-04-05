"""Model for files"""

# SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship

# SQLAlchemy_serializer
from sqlalchemy_serializer import SerializerMixin

# Services
from services.sqlalchemy.base import Base

# Time
from datetime import datetime


class File(Base, SerializerMixin):
    """File Model"""
    __tablename__ = "files"

    """Attributes"""
    file = Column(Integer, primary_key=True)
    filename = Column(String(250))
    title = Column(String(250))
    cloud = Column(String(250))
    code = Column(String(50), unique=True)
    parent = Column(String(100))
    size = Column(Integer)
    mimetype = Column(String(50))
    extension = Column(String(10))
    width = Column(Integer, default=None)
    height = Column(Integer, default=None)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now())
    deleted_at = Column(DateTime, nullable=True)

    """Relationships"""
    folders = relationship('Folder', secondary='folders_files')

    """Serialize settings"""
    serialize_only = (
        'file', 'filename', 'code', 'size',
        'mimetype', 'extension', 'created_at',
        'width', 'height', 'title', 'parent'
    )
