"""Admin Pydantic schemas for API serialization and validation."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr, ConfigDict


class AdminBase(BaseModel):
    """Base admin schema with common fields."""
    
    username: str = Field(..., min_length=3, max_length=50, description="Admin username")
    email: EmailStr = Field(..., description="Admin email address")
    is_active: bool = Field(default=True, description="Admin active status")


class AdminCreate(AdminBase):
    """Schema for creating a new admin."""
    
    password: str = Field(..., min_length=6, description="Admin password")


class AdminUpdate(BaseModel):
    """Schema for updating an existing admin."""
    
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=6)


class AdminResponse(AdminBase):
    """Schema for admin API responses."""
    
    id: UUID
    created_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class AdminLogin(BaseModel):
    """Schema for admin login."""
    
    username: str = Field(..., description="Admin username")
    password: str = Field(..., description="Admin password")


class TokenResponse(BaseModel):
    """Schema for JWT token response."""
    
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UploadHistoryResponse(BaseModel):
    """Schema for upload history responses."""
    
    id: UUID
    admin_id: UUID
    admin_username: str
    filename: str
    total_rows: int
    successful_rows: int
    failed_rows: int
    status: str
    error_details: Optional[Dict[str, Any]] = None
    uploaded_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UploadHistoryListResponse(BaseModel):
    """Schema for paginated upload history list responses."""
    
    items: List[UploadHistoryResponse]
    total: int
    page: int
    size: int
    pages: int
