"""Test script for the new Excel download functionality."""

from datetime import datetime

from app.core.database import SessionLocal
from app.services.excel_exporter import ExcelExporter


def test_excel_export():
    """Test the Excel export functionality."""
    print("Testing Excel export functionality...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create exporter
        exporter = ExcelExporter(db)
        
        # Test export (active products only)
        print("Exporting active products...")
        excel_content = exporter.export_products_to_excel(include_inactive=False)
        
        # Save to file for testing
        filename = f"test_export_active_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with open(filename, 'wb') as f:
            f.write(excel_content)
        
        print(f"✅ Export successful! File saved as: {filename}")
        print(f"📊 File size: {len(excel_content)} bytes")
        
        # Test export (all products including inactive)
        print("Exporting all products (including inactive)...")
        excel_content_all = exporter.export_products_to_excel(include_inactive=True)
        
        filename_all = f"test_export_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        with open(filename_all, 'wb') as f:
            f.write(excel_content_all)
        
        print(f"✅ Export successful! File saved as: {filename_all}")
        print(f"📊 File size: {len(excel_content_all)} bytes")
        
        # Test filename generation
        generated_filename = exporter.generate_filename(include_inactive=False)
        print(f"📝 Generated filename (active): {generated_filename}")
        
        generated_filename_all = exporter.generate_filename(include_inactive=True)
        print(f"📝 Generated filename (all): {generated_filename_all}")
        
    except Exception as e:
        print(f"❌ Error during export: {str(e)}")
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    test_excel_export()
