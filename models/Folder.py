"""Model for folders"""

# SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship

# SQLAlchemy_serializer
from sqlalchemy_serializer import SerializerMixin

# Services
from services.sqlalchemy.base import Base

# Time
from datetime import datetime


class Folder(Base, SerializerMixin):
    """Folder Model"""
    __tablename__ = "folders"

    """Attributes"""
    folder = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True)
    description = Column(String(280), default="")
    parent = Column(String(100), nullable=True)
    # TODO: Implement email functionality.
    # email_to = Column(String(50))
    # email_from = Column(String(50))
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now())
    deleted_at = Column(DateTime, nullable=True)

    """Relationships"""
    files = relationship('File', secondary='folders_files')

    """Serialize settings"""
    serialize_only = (
        'code', 'description', 'parent', 'created_at'
    )
