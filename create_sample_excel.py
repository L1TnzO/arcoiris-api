"""Crea un archivo Excel de muestra para importar productos (catálogo en español, precios CLP)."""

import pandas as pd
import random

# Datos de productos de muestra
data = [
    ["Sofá Moderno", "Sofá de 3 plazas con tela premium y diseño contemporáneo", 459990, "Muebles", "ConfortChile", "SOF001", 8, f"https://picsum.photos/id/{random.randint(1, 100)}/200/300", "moderno,cómodo,sala de estar"],
    ["Mesa de Comedor", "Mesa de comedor de madera sólida para 6 personas", 329990, "Muebles", "MaderasNativas", "MES001", 4, f"https://picsum.photos/id/{random.randint(1, 100)}/200/300", "comedor,madera,familiar"],
    ["Silla de Oficina", "Silla ergonómica con soporte lumbar ajustable", 119990, "Oficina", "ErgoPlus", "SIL001", 12, f"https://picsum.photos/id/{random.randint(1, 100)}/200/300", "oficina,ergonómica,soporte"],
    ["Librero", "Librero de 5 niveles en madera natural", 89990, "Almacenamiento", "MaderasNativas", "LIB001", 6, f"https://picsum.photos/id/{random.randint(1, 100)}/200/300", "almacenamiento,libros,madera"],
    ["Mesa de Centro", "Mesa de centro con cubierta de vidrio y patas metálicas", 129990, "Muebles", "HogarModerno", "MCE001", 10, f"https://picsum.photos/id/{random.randint(1, 100)}/200/300", "centro,vidrio,moderna"],
    ["Ropero", "Ropero grande con puertas corredizas y amplio espacio", 249990, "Almacenamiento", "EspacioPlus", "ROP001", 3, f"https://picsum.photos/id/{random.randint(1, 100)}/200/300", "almacenamiento,ropa,corredizo"],
    ["Lámpara de Escritorio", "Lámpara LED con brillo regulable y diseño minimalista", 29990, "Iluminación", "LuzTech", "LAM001", 18, f"https://picsum.photos/id/{random.randint(1, 100)}/200/300", "iluminación,LED,ajustable"],
    ["Puf", "Puf grande para sala de estar, ideal para relajarse", 49990, "Muebles", "ConfortChile", "PUF001", 15, f"https://picsum.photos/id/{random.randint(1, 100)}/200/300", "relajación,comodidad,casual"],
]

# Crear DataFrame
df = pd.DataFrame(data, columns=[
    "Nombre del Producto",
    "Descripción",
    "Precio (CLP)",
    "Categoría",
    "Marca",
    "SKU",
    "Stock",
    "URL Imagen",
    "Etiquetas"
])

# Guardar en Excel
df.to_excel("catalogo_productos_clp.xlsx", index=False, header=True)

print("¡Archivo Excel 'catalogo_productos_clp.xlsx' creado exitosamente!")
print("\nEl archivo contiene los siguientes productos:")
for i, row in enumerate(data, 1):
    print(f"{i}. {row[0]} - ${row[2]:,} CLP ({row[4]})")
