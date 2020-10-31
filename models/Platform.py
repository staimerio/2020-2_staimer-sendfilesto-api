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


class Platform(Base, SerializerMixin):
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

    """Relationships"""
    """Serialize settings"""
    serialize_only = (
        'platform', 'title', 'slug', 'description', 'created_at'
    )
