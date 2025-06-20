"""Product API endpoints - Public access."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.core.database import get_db
from app.models.product import Product
from app.schemas.product import (
    ProductResponse, 
    ProductListResponse,
    ProductSearchQuery,
    CategoryResponse
)

router = APIRouter()


@router.get("/", response_model=ProductListResponse)
async def get_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock availability"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """Get all active products with filtering and pagination."""
    
    # Build query
    query = db.query(Product).filter(Product.is_active == True)
    
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
    offset = (page - 1) * size
    products = query.offset(offset).limit(size).all()
    
    # Calculate total pages
    pages = (total + size - 1) // size
    
    return ProductListResponse(
        items=products,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/search", response_model=ProductListResponse)
async def search_products(
    q: str = Query(..., min_length=1, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """Search products by name and description."""
    
    # Build search query
    search_filter = or_(
        Product.name.ilike(f"%{q}%"),
        Product.description.ilike(f"%{q}%")
    )
    
    query = db.query(Product).filter(
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
    
    # Order by relevance (products with name matches first)
    query = query.order_by(
        Product.name.ilike(f"%{q}%").desc(),
        Product.created_at.desc()
    )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * size
    products = query.offset(offset).limit(size).all()
    
    # Calculate total pages
    pages = (total + size - 1) // size
    
    return ProductListResponse(
        items=products,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    """Get all available product categories with product counts."""
    
    categories = db.query(
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
        CategoryResponse(name=category, count=count)
        for category, count in categories
    ]


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a single product by ID."""
    
    product = db.query(Product).filter(
        and_(
            Product.id == product_id,
            Product.is_active == True
        )
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product
