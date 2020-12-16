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


class Object(Base, SerializerMixin):
    """Object Model"""
    __tablename__ = "objects"

    """Attributes"""
    object = Column(Integer, primary_key=True)
    content = Column(Text)
    code = Column(String(50), unique=True)
    parent = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now())
    deleted_at = Column(DateTime, nullable=True)

    """Relationships"""
    folders = relationship('Folder', secondary='folders_objects')

    """Serialize settings"""
    serialize_only = (
        'object', 'code', 'created_at',
        'content', 'parent'
    )
