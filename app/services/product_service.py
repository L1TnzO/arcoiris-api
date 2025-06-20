"""Product service for business logic."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductSearchQuery


class ProductService:
    """Service class for product-related business logic."""
    
    def __init__(self, db: Session):
        """Initialize service with database session."""
        self.db = db
    
    def create_product(self, product_data: ProductCreate) -> Product:
        """Create a new product."""
        
        # Convert to dict and create product
        product_dict = product_data.dict()
        product = Product(**product_dict)
        
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        
        return product
    
    def get_product_by_id(self, product_id: UUID, include_inactive: bool = False) -> Optional[Product]:
        """Get product by ID."""
        
        query = self.db.query(Product).filter(Product.id == product_id)
        
        if not include_inactive:
            query = query.filter(Product.is_active == True)
        
        return query.first()
    
    def get_product_by_sku(self, sku: str, include_inactive: bool = False) -> Optional[Product]:
        """Get product by SKU."""
        
        query = self.db.query(Product).filter(Product.sku == sku)
        
        if not include_inactive:
            query = query.filter(Product.is_active == True)
        
        return query.first()
    
    def get_products(
        self,
        skip: int = 0,
        limit: int = 20,
        include_inactive: bool = False,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        in_stock: Optional[bool] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> tuple[List[Product], int]:
        """Get products with filtering and pagination."""
        
        # Build base query
        query = self.db.query(Product)
        
        if not include_inactive:
            query = query.filter(Product.is_active == True)
        
        # Apply filters
        if category:
            query = query.filter(Product.category.ilike(f"%{category}%"))
        
        if brand:
            query = query.filter(Product.brand.ilike(f"%{brand}%"))
        
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        
        if in_stock is not None:
            if in_stock:
                query = query.filter(Product.stock_quantity > 0)
            else:
                query = query.filter(Product.stock_quantity == 0)
        
        # Apply sorting
        if hasattr(Product, sort_by):
            order_column = getattr(Product, sort_by)
            if sort_order == "desc":
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        products = query.offset(skip).limit(limit).all()
        
        return products, total
    
    def search_products(
        self,
        search_query: str,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None
    ) -> tuple[List[Product], int]:
        """Search products by name and description."""
        
        # Build search filter
        search_filter = or_(
            Product.name.ilike(f"%{search_query}%"),
            Product.description.ilike(f"%{search_query}%")
        )
        
        query = self.db.query(Product).filter(
            and_(
                Product.is_active == True,
                search_filter
            )
        )
        
        # Apply additional filters
        if category:
            query = query.filter(Product.category.ilike(f"%{category}%"))
        
        if brand:
            query = query.filter(Product.brand.ilike(f"%{brand}%"))
        
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        
        # Order by relevance (name matches first)
        query = query.order_by(
            Product.name.ilike(f"%{search_query}%").desc(),
            Product.created_at.desc()
        )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        products = query.offset(skip).limit(limit).all()
        
        return products, total
    
    def update_product(self, product_id: UUID, product_data: ProductUpdate) -> Optional[Product]:
        """Update an existing product."""
        
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None
        
        # Update fields
        update_data = product_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        
        self.db.commit()
        self.db.refresh(product)
        
        return product
    
    def delete_product(self, product_id: UUID, soft_delete: bool = True) -> bool:
        """Delete a product (soft delete by default)."""
        
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return False
        
        if soft_delete:
            # Soft delete - set is_active to False
            product.is_active = False
            self.db.commit()
        else:
            # Hard delete - remove from database
            self.db.delete(product)
            self.db.commit()
        
        return True
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all available categories with product counts."""
        
        categories = self.db.query(
            Product.category,
            func.count(Product.id).label('count')
        ).filter(
            and_(
                Product.is_active == True,
                Product.category.isnot(None),
                Product.category != ""
            )
        ).group_by(Product.category).all()
        
        return [
            {"name": category, "count": count}
            for category, count in categories
        ]
    
    def get_brands(self) -> List[Dict[str, Any]]:
        """Get all available brands with product counts."""
        
        brands = self.db.query(
            Product.brand,
            func.count(Product.id).label('count')
        ).filter(
            and_(
                Product.is_active == True,
                Product.brand.isnot(None),
                Product.brand != ""
            )
        ).group_by(Product.brand).all()
        
        return [
            {"name": brand, "count": count}
            for brand, count in brands
        ]
    
    def update_stock(self, product_id: UUID, quantity: int) -> Optional[Product]:
        """Update product stock quantity."""
        
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None
        
        product.stock_quantity = quantity
        self.db.commit()
        self.db.refresh(product)
        
        return product
    
    def bulk_update_status(self, product_ids: List[UUID], is_active: bool) -> int:
        """Bulk update product status."""
        
        updated_count = self.db.query(Product).filter(
            Product.id.in_(product_ids)
        ).update(
            {"is_active": is_active},
            synchronize_session=False
        )
        
        self.db.commit()
        return updated_count
