"""Excel file export service for product data."""

import io
import logging
from datetime import datetime
from typing import List, Optional

import pandas as pd
from sqlalchemy.orm import Session

from app.models.product import Product

# Setup logging
logger = logging.getLogger(__name__)


class ExcelExporter:
    """Excel file exporter for product data."""
    
    # Column headers for the Excel export (matching import format)
    COLUMN_HEADERS = [
        'Product Name',      # Column A: name
        'Description',       # Column B: description  
        'Price',            # Column C: price
        'Category',         # Column D: category
        'Brand',            # Column E: brand
        'SKU',              # Column F: sku
        'Stock Quantity',   # Column G: stock_quantity
        'Image URL',        # Column H: image_url
        'Tags',             # Column I: tags
    ]
    
    def __init__(self, db: Session):
        """Initialize exporter with database session."""
        self.db = db
    
    def export_products_to_excel(
        self, 
        include_inactive: bool = False,
        category_filter: Optional[str] = None,
        brand_filter: Optional[str] = None
    ) -> bytes:
        """Export products to Excel file and return bytes."""
        
        logger.info(f"Exporting products to Excel. Include inactive: {include_inactive}")
        
        try:
            # Build query
            query = self.db.query(Product)
            
            if not include_inactive:
                query = query.filter(Product.is_active == True)
                
            if category_filter:
                query = query.filter(Product.category.ilike(f"%{category_filter}%"))
                
            if brand_filter:
                query = query.filter(Product.brand.ilike(f"%{brand_filter}%"))
            
            # Order by creation date (newest first)
            query = query.order_by(Product.created_at.desc())
            
            # Get all products
            products = query.all()
            
            # Convert to list of dictionaries
            data = []
            for product in products:
                # Convert tags JSON to comma-separated string
                tags_str = ""
                if product.tags and isinstance(product.tags, dict) and "tags" in product.tags:
                    tags_str = ", ".join(product.tags["tags"])
                
                data.append({
                    'Product Name': product.name,
                    'Description': product.description or "",
                    'Price': float(product.price) if product.price else 0,
                    'Category': product.category or "",
                    'Brand': product.brand or "",
                    'SKU': product.sku or "",
                    'Stock Quantity': product.stock_quantity or 0,
                    'Image URL': product.image_url or "",
                    'Tags': tags_str,
                })
            
            # Create DataFrame
            df = pd.DataFrame(data, columns=self.COLUMN_HEADERS)
            
            # Create Excel file in memory
            excel_buffer = io.BytesIO()
            
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                # Write data to Excel
                df.to_excel(writer, sheet_name='Products', index=False, header=True)
                
                # Get the workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Products']
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    # Set column width with some padding
                    adjusted_width = min(max_length + 2, 50)  # Max width of 50
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                # Add some formatting to headers
                from openpyxl.styles import Font, PatternFill
                
                header_font = Font(bold=True, color="FFFFFF")
                header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                
                for cell in worksheet[1]:  # First row (headers)
                    cell.font = header_font
                    cell.fill = header_fill
            
            excel_buffer.seek(0)
            excel_content = excel_buffer.getvalue()
            
            logger.info(f"Successfully exported {len(products)} products to Excel")
            return excel_content
            
        except Exception as e:
            logger.error(f"Failed to export products to Excel: {str(e)}")
            raise Exception(f"Failed to generate Excel file: {str(e)}")
    
    def generate_filename(self, include_inactive: bool = False) -> str:
        """Generate a filename for the exported Excel file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        status = "all" if include_inactive else "active"
        return f"productos_{status}_{timestamp}.xlsx"
