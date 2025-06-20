"""Admin user database model."""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import Column, String, Boolean, DateTime, Integer, JSON
from sqlalchemy.sql import func

from app.core.database import Base


class Admin(Base):
    """Admin user model for system administrators."""
    
    __tablename__ = "admins"
    
    # Primary key - use String for UUID compatibility with SQLite
    id = Column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4()),
        index=True
    )
    
    # Authentication credentials
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self) -> str:
        """String representation of Admin."""
        return f"<Admin(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert admin to dictionary (excluding sensitive data)."""
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }


class UploadHistory(Base):
    """Track Excel upload history for auditing."""
    
    __tablename__ = "upload_history"
    
    id = Column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4()),
        index=True
    )
    
    # Admin who performed the upload
    admin_id = Column(String(36), nullable=False, index=True)
    admin_username = Column(String(50), nullable=False)
    
    # Upload details
    filename = Column(String(255), nullable=False)
    total_rows = Column(Integer, default=0)
    successful_rows = Column(Integer, default=0)
    failed_rows = Column(Integer, default=0)
    
    # Status and errors
    status = Column(String(20), nullable=False)  # success, partial, failed
    error_details = Column(JSON, nullable=True)
    
    # Timestamp
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self) -> str:
        """String representation of UploadHistory."""
        return f"<UploadHistory(id={self.id}, filename='{self.filename}', status='{self.status}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert upload history to dictionary."""
        return {
            "id": str(self.id),
            "admin_id": str(self.admin_id),
            "admin_username": self.admin_username,
            "filename": self.filename,
            "total_rows": self.total_rows,
            "successful_rows": self.successful_rows,
            "failed_rows": self.failed_rows,
            "status": self.status,
            "error_details": self.error_details,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
        }
