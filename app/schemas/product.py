"""Product Pydantic schemas for API serialization and validation."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, ConfigDict


class ProductBase(BaseModel):
    """Base product schema with common fields."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: Decimal = Field(..., gt=0, description="Product price")
    category: Optional[str] = Field(None, max_length=100, description="Product category")
    brand: Optional[str] = Field(None, max_length=100, description="Product brand")
    sku: Optional[str] = Field(None, max_length=100, description="Stock Keeping Unit")
    stock_quantity: int = Field(default=0, ge=0, description="Stock quantity")
    is_active: bool = Field(default=True, description="Product active status")
    image_url: Optional[str] = Field(None, description="Product image URL")
    tags: Optional[Dict[str, Any]] = Field(None, description="Product tags and metadata")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate product name."""
        if not v or not v.strip():
            raise ValueError('Product name cannot be empty')
        return v.strip()
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        """Normalize category capitalization."""
        if v:
            return v.strip().title()
        return v
    
    @field_validator('sku')
    @classmethod
    def validate_sku(cls, v):
        """Validate SKU format."""
        if v:
            v = v.strip().upper()
            if len(v) < 3:
                raise ValueError('SKU must be at least 3 characters long')
        return v
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        """Validate price is positive."""
        if v <= 0:
            raise ValueError('Price must be positive')
        return v


class ProductCreate(ProductBase):
    """Schema for creating a new product."""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating an existing product."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0, description="Product price")
    category: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    sku: Optional[str] = Field(None, max_length=100)
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    image_url: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate product name."""
        if v is not None and (not v or not v.strip()):
            raise ValueError('Product name cannot be empty')
        return v.strip() if v else v
    
    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        """Normalize category capitalization."""
        if v:
            return v.strip().title()
        return v
    
    @field_validator('sku')
    @classmethod
    def validate_sku(cls, v):
        """Validate SKU format."""
        if v:
            v = v.strip().upper()
            if len(v) < 3:
                raise ValueError('SKU must be at least 3 characters long')
        return v
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        """Validate price is positive."""
        if v is not None and v <= 0:
            raise ValueError('Price must be positive')
        return v


class ProductResponse(ProductBase):
    """Schema for product API responses."""
    
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    """Schema for paginated product list responses."""
    
    items: List[ProductResponse]
    total: int
    page: int
    size: int
    pages: int


class ProductSearchQuery(BaseModel):
    """Schema for product search queries."""
    
    q: Optional[str] = Field(None, description="Search query")
    category: Optional[str] = Field(None, description="Filter by category")
    brand: Optional[str] = Field(None, description="Filter by brand")
    min_price: Optional[Decimal] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[Decimal] = Field(None, ge=0, description="Maximum price")
    in_stock: Optional[bool] = Field(None, description="Filter by stock availability")
    is_active: Optional[bool] = Field(True, description="Filter by active status")
    sort_by: Optional[str] = Field("created_at", description="Sort field")
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$", description="Sort order")
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size")
    
    @field_validator('max_price')
    @classmethod
    def validate_price_range(cls, v, info):
        """Validate price range."""
        if v is not None and 'min_price' in info.data and info.data['min_price'] is not None:
            if v < info.data['min_price']:
                raise ValueError('max_price must be greater than or equal to min_price')
        return v


class CategoryResponse(BaseModel):
    """Schema for category responses."""
    
    name: str
    count: int


class ExcelImportResult(BaseModel):
    """Schema for Excel import operation results."""
    
    filename: str
    total_rows: int
    successful_rows: int
    failed_rows: int
    errors: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_rows == 0:
            return 0.0
        return (self.successful_rows / self.total_rows) * 100
