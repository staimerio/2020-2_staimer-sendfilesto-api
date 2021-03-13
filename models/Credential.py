"""Model for folders"""

# SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, LargeBinary
from sqlalchemy.orm import relationship

# SQLAlchemy_serializer
from sqlalchemy_serializer import SerializerMixin

# Services
from services.sqlalchemy.base import Base

# Time
from datetime import datetime


class Credential(Base, SerializerMixin):
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

    """Relationships"""
    """Serialize settings"""
    serialize_only = (
        'credential', 'title', 'key', 'picky', 'created_at'
    )
