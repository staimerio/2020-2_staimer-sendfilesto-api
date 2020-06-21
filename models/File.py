"""Model for files"""

# SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean

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
    filename = Column(String(50))
    description = Column(String(280), default="")
    cloud = Column(String(50), unique=True)
    parent = Column(String(100))
    size = Column(Integer)
    mimetype = Column(String(20))
    extension = Column(String(10))
    email_to = Column(String(50))
    email_from = Column(String(50))
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now())
    deleted_at = Column(DateTime, nullable=True)

    """Serialize settings"""
    serialize_only = (
        'file', 'filename', 'description', 'cloud', 'parent',
        'size', 'mimetype', 'extension',
    )
