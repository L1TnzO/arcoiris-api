"""Product database model."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional

from sqlalchemy import Column, String, Text, DECIMAL, Integer, Boolean, DateTime, JSON, Index
from sqlalchemy.sql import func

from app.core.database import Base


class Product(Base):
    """Product model for storing furniture product information."""
    
    __tablename__ = "products"
    
    # Primary key - use String for UUID compatibility with SQLite
    id = Column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4()),
        index=True
    )
    
    # Core product information
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(precision=10, scale=2), nullable=False)
    category = Column(String(100), nullable=True, index=True)
    brand = Column(String(100), nullable=True)
    sku = Column(String(100), nullable=True, unique=True, index=True)
    
    # Inventory
    stock_quantity = Column(Integer, default=0, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Media
    image_url = Column(Text, nullable=True)
    
    # Flexible metadata as JSON
    tags = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(),
        nullable=False
    )
    
    # Database indexes for performance
    __table_args__ = (
        Index('idx_product_name_category', 'name', 'category'),
        Index('idx_product_price_active', 'price', 'is_active'),
        Index('idx_product_created_at', 'created_at'),
    )
    
    def __repr__(self) -> str:
        """String representation of Product."""
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert product to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "price": float(self.price) if self.price else None,
            "category": self.category,
            "brand": self.brand,
            "sku": self.sku,
            "stock_quantity": self.stock_quantity,
            "is_active": self.is_active,
            "image_url": self.image_url,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @property
    def is_in_stock(self) -> bool:
        """Check if product is in stock."""
        return self.stock_quantity > 0
    
    @property
    def formatted_price(self) -> str:
        """Get formatted price as string."""
        return f"${self.price:.2f}" if self.price else "$0.00"
