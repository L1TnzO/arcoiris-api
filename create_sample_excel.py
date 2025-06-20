"""Create sample Excel file for testing product imports."""

import pandas as pd
from decimal import Decimal

# Sample product data
sample_data = [
    ["Modern Sofa", "Comfortable 3-seater sofa with premium fabric", 1299.99, "Furniture", "ComfortCorp", "SOF001", 10, "https://example.com/sofa.jpg", "modern,comfortable,living room"],
    ["Dining Table", "Solid wood dining table for 6 people", 899.99, "Furniture", "WoodCraft", "DIN001", 5, "https://example.com/table.jpg", "dining,wood,family"],
    ["Office Chair", "Ergonomic office chair with lumbar support", 299.99, "Office", "ErgoPlus", "CHR001", 15, "https://example.com/chair.jpg", "office,ergonomic,support"],
    ["Bookshelf", "5-tier wooden bookshelf", 199.99, "Storage", "WoodCraft", "BSH001", 8, "https://example.com/bookshelf.jpg", "storage,books,wood"],
    ["Coffee Table", "Glass top coffee table with metal legs", 349.99, "Furniture", "ModernHome", "CFT001", 12, "https://example.com/coffee-table.jpg", "coffee,glass,modern"],
    ["Wardrobe", "Large wardrobe with sliding doors", 799.99, "Storage", "SpacePlus", "WAR001", 6, "https://example.com/wardrobe.jpg", "storage,clothes,sliding"],
    ["Desk Lamp", "LED desk lamp with adjustable brightness", 79.99, "Lighting", "BrightTech", "LAM001", 25, "https://example.com/lamp.jpg", "lighting,LED,adjustable"],
    ["Bean Bag", "Large bean bag chair for relaxation", 149.99, "Furniture", "ComfortCorp", "BBG001", 20, "https://example.com/beanbag.jpg", "relaxation,comfort,casual"],
]

# Create DataFrame
df = pd.DataFrame(sample_data, columns=[
    "Product Name",
    "Description", 
    "Price",
    "Category",
    "Brand",
    "SKU",
    "Stock Quantity",
    "Image URL",
    "Tags"
])

# Save to Excel
df.to_excel("sample_products.xlsx", index=False, header=False)

print("Sample Excel file 'sample_products.xlsx' created successfully!")
print("\nFile contains the following products:")
for i, row in enumerate(sample_data, 1):
    print(f"{i}. {row[0]} - ${row[2]} ({row[4]})")
