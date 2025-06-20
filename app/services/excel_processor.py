"""Excel file processing service for bulk product imports."""

import io
import logging
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any, Optional
from uuid import UUID

import pandas as pd
from fastapi import UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.product import Product
from app.models.admin import Admin
from app.schemas.product import ExcelImportResult

# Setup logging
logger = logging.getLogger(__name__)


class ExcelProcessor:
    """Excel file processor for product imports."""
    
    # Expected column mapping
    COLUMN_MAPPING = {
        0: 'name',           # Column A: Product Name (required)
        1: 'description',    # Column B: Description (optional)
        2: 'price',          # Column C: Price (required, numeric)
        3: 'category',       # Column D: Category (optional)
        4: 'brand',          # Column E: Brand (optional)
        5: 'sku',            # Column F: SKU (optional, unique)
        6: 'stock_quantity', # Column G: Stock Quantity (optional, default=0)
        7: 'image_url',      # Column H: Image URL (optional)
        8: 'tags',           # Column I: Tags (optional, comma-separated)
    }
    
    def __init__(self, db: Session):
        """Initialize processor with database session."""
        self.db = db
    
    async def process_excel_file(
        self, 
        file: UploadFile, 
        admin: Admin
    ) -> ExcelImportResult:
        """Process uploaded Excel file and import products."""
        
        logger.info(f"Processing Excel file: {file.filename} by admin: {admin.username}")
        
        # Read file content
        content = await file.read()
        
        try:
            # Read Excel file into DataFrame
            df = pd.read_excel(io.BytesIO(content), header=None)
            
            # Initialize result tracking
            result = ExcelImportResult(
                filename=file.filename,
                total_rows=len(df),
                successful_rows=0,
                failed_rows=0,
                errors=[],
                warnings=[]
            )
            
            if df.empty:
                result.errors.append({
                    "row": 0,
                    "error": "Empty file or no data found"
                })
                return result
            
            # Process each row
            for index, row in df.iterrows():
                try:
                    row_number = index + 1
                    product_data = self._parse_row(row, row_number)
                    
                    if product_data:
                        success = await self._upsert_product(product_data, row_number, result)
                        if success:
                            result.successful_rows += 1
                        else:
                            result.failed_rows += 1
                    else:
                        result.failed_rows += 1
                        
                except Exception as e:
                    logger.error(f"Error processing row {index + 1}: {str(e)}")
                    result.failed_rows += 1
                    result.errors.append({
                        "row": index + 1,
                        "error": f"Unexpected error: {str(e)}"
                    })
            
            # Commit all changes
            self.db.commit()
            
            logger.info(f"Excel processing completed. Success: {result.successful_rows}, Failed: {result.failed_rows}")
            return result
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to process Excel file: {str(e)}")
            raise Exception(f"Failed to read Excel file: {str(e)}")
    
    def _parse_row(self, row: pd.Series, row_number: int) -> Optional[Dict[str, Any]]:
        """Parse a single row from the Excel file."""
        
        try:
            # Skip empty rows
            if row.isna().all():
                return None
            
            # Extract data based on column mapping
            product_data = {}
            
            for col_index, field_name in self.COLUMN_MAPPING.items():
                if col_index < len(row):
                    value = row.iloc[col_index]
                    
                    # Handle NaN values
                    if pd.isna(value):
                        value = None
                    elif isinstance(value, str):
                        value = value.strip()
                        if value == "":
                            value = None
                    
                    product_data[field_name] = value
            
            # Validate required fields
            if not product_data.get('name'):
                raise ValueError("Product name is required")
            
            # Validate and convert price
            if product_data.get('price') is not None:
                try:
                    price = float(product_data['price'])
                    if price <= 0:
                        raise ValueError("Price must be positive")
                    product_data['price'] = Decimal(str(price)).quantize(Decimal('0.01'))
                except (ValueError, InvalidOperation):
                    raise ValueError("Invalid price format")
            else:
                raise ValueError("Price is required")
            
            # Validate and convert stock quantity
            if product_data.get('stock_quantity') is not None:
                try:
                    stock = int(float(product_data['stock_quantity']))
                    if stock < 0:
                        raise ValueError("Stock quantity cannot be negative")
                    product_data['stock_quantity'] = stock
                except (ValueError, TypeError):
                    raise ValueError("Invalid stock quantity format")
            else:
                product_data['stock_quantity'] = 0
            
            # Process tags (convert comma-separated string to JSON)
            if product_data.get('tags'):
                try:
                    tags_str = str(product_data['tags'])
                    tags_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
                    product_data['tags'] = {"tags": tags_list} if tags_list else None
                except Exception:
                    product_data['tags'] = None
            
            # Normalize category and brand
            if product_data.get('category'):
                product_data['category'] = str(product_data['category']).strip().title()
            
            if product_data.get('brand'):
                product_data['brand'] = str(product_data['brand']).strip()
            
            # Normalize SKU
            if product_data.get('sku'):
                product_data['sku'] = str(product_data['sku']).strip().upper()
            
            # Set default values
            product_data['is_active'] = True
            
            return product_data
            
        except Exception as e:
            logger.error(f"Error parsing row {row_number}: {str(e)}")
            raise
    
    async def _upsert_product(
        self, 
        product_data: Dict[str, Any], 
        row_number: int, 
        result: ExcelImportResult
    ) -> bool:
        """Insert or update a product based on SKU or name."""
        
        try:
            existing_product = None
            
            # Try to find existing product by SKU first, then by name
            if product_data.get('sku'):
                existing_product = self.db.query(Product).filter(
                    Product.sku == product_data['sku']
                ).first()
            
            if not existing_product and product_data.get('name'):
                existing_product = self.db.query(Product).filter(
                    Product.name == product_data['name']
                ).first()
            
            if existing_product:
                # Update existing product
                for field, value in product_data.items():
                    if field != 'id' and value is not None:
                        setattr(existing_product, field, value)
                
                result.warnings.append({
                    "row": row_number,
                    "message": f"Updated existing product: {product_data['name']}"
                })
                
                logger.debug(f"Updated product: {product_data['name']}")
                
            else:
                # Create new product
                new_product = Product(**product_data)
                self.db.add(new_product)
                
                logger.debug(f"Created new product: {product_data['name']}")
            
            # Flush to catch any database constraints
            self.db.flush()
            return True
            
        except IntegrityError as e:
            self.db.rollback()
            error_msg = "Duplicate SKU or name" if "unique" in str(e).lower() else str(e)
            result.errors.append({
                "row": row_number,
                "error": f"Database constraint error: {error_msg}"
            })
            logger.error(f"Integrity error for row {row_number}: {str(e)}")
            return False
            
        except Exception as e:
            self.db.rollback()
            result.errors.append({
                "row": row_number,
                "error": f"Failed to save product: {str(e)}"
            })
            logger.error(f"Error saving product for row {row_number}: {str(e)}")
            return False
