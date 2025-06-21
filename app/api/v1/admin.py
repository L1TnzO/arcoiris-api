"""Admin API endpoints - Authentication required."""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.core.database import get_db
from app.core.security import verify_password, create_access_token, get_password_hash
from app.core.config import get_settings
from app.api.deps import get_current_active_admin
from app.models.admin import Admin, UploadHistory
from app.models.product import Product
from app.schemas.admin import (
    AdminResponse,
    TokenResponse,
    UploadHistoryResponse,
    UploadHistoryListResponse
)
from app.schemas.product import (
    ProductResponse,
    ProductListResponse,
    ProductUpdate,
    ExcelImportResult
)
from app.services.excel_processor import ExcelProcessor
from app.services.excel_exporter import ExcelExporter

settings = get_settings()
router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Admin login endpoint."""
    
    # Find admin by username
    admin = db.query(Admin).filter(Admin.username == form_data.username).first()
    
    if not admin or not verify_password(form_data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive admin account"
        )
    
    # Update last login
    admin.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        subject=admin.username, expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.get("/me", response_model=AdminResponse)
async def get_current_admin_info(
    current_admin: Admin = Depends(get_current_active_admin)
):
    """Get current admin information."""
    return current_admin


@router.get("/products/", response_model=ProductListResponse)
async def get_all_products(
    include_inactive: bool = False,
    category: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin)
):
    """Get all products (including inactive ones for admin)."""
    
    # Build query
    query = db.query(Product)
    
    if not include_inactive:
        query = query.filter(Product.is_active == True)
    
    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    
    # Order by created date (newest first)
    query = query.order_by(Product.created_at.desc())
    
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


@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin)
):
    """Update a product."""
    
    # Find product
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Update fields
    update_data = product_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    # Update timestamp
    product.updated_at = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(product)
        return product
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update product: {str(e)}"
        )


@router.delete("/products/{product_id}")
async def delete_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin)
):
    """Soft delete a product (set is_active to False)."""
    
    # Find product
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Soft delete
    product.is_active = False
    product.updated_at = datetime.utcnow()
    
    try:
        db.commit()
        return {"message": "Product deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete product: {str(e)}"
        )


@router.post("/upload-excel", response_model=ExcelImportResult)
async def upload_excel_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin)
):
    """Upload Excel file to update products."""
    
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # Check file extension
    file_ext = file.filename.lower().split('.')[-1]
    if f".{file_ext}" not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {settings.allowed_extensions}"
        )
    
    # Check file size
    if file.size and file.size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.max_file_size} bytes"
        )
    
    try:
        # Process Excel file
        processor = ExcelProcessor(db)
        result = await processor.process_excel_file(file, current_admin)
        
        # Record upload history
        upload_record = UploadHistory(
            admin_id=current_admin.id,
            admin_username=current_admin.username,
            filename=file.filename,
            total_rows=result.total_rows,
            successful_rows=result.successful_rows,
            failed_rows=result.failed_rows,
            status="success" if result.failed_rows == 0 else ("partial" if result.successful_rows > 0 else "failed"),
            error_details={"errors": result.errors, "warnings": result.warnings} if result.errors or result.warnings else None
        )
        
        db.add(upload_record)
        db.commit()
        
        return result
        
    except Exception as e:
        # Record failed upload
        upload_record = UploadHistory(
            admin_id=current_admin.id,
            admin_username=current_admin.username,
            filename=file.filename,
            total_rows=0,
            successful_rows=0,
            failed_rows=0,
            status="failed",
            error_details={"error": str(e)}
        )
        
        db.add(upload_record)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process Excel file: {str(e)}"
        )


@router.get("/download-excel")
async def download_excel_products(
    include_inactive: bool = False,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_active_admin)
):
    """Download all products as Excel file."""
    
    try:
        # Create Excel exporter
        exporter = ExcelExporter(db)
        
        # Generate Excel file content
        excel_content = exporter.export_products_to_excel(
            include_inactive=include_inactive,
            category_filter=category,
            brand_filter=brand
        )
        
        # Generate filename
        filename = exporter.generate_filename(include_inactive=include_inactive)
        
        # Create streaming response
        def iterfile():
            yield excel_content
        
        return StreamingResponse(
            iterfile(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate Excel file: {str(e)}"
        )
