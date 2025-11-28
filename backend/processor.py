import pdfplumber
import re
import math
import pandas as pd

# -- reglas de precio --
def redondear_10(n):
    return math.ceil(n / 10) * 10

def precio_venta(precio):
    if precio > 18000:
        p = precio * 1.6
    elif precio > 12000:
        p = precio * 1.7
    elif precio > 8000:
        p = precio * 1.8
    else:
        p = precio * 2
    return redondear_10(p)

# -- extracción de productos --
def extraer_productos(path_pdf):
    productos = []

    codigo_regex = r"[A-Z]{4,5}\d{2}"

    with pdfplumber.open(path_pdf) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    for cell in row:
                        if cell is None:
                            continue

                        texto = cell.replace("\n", " ")

                        # buscar código
                        codigos = re.findall(codigo_regex, texto)
                        if not codigos:
                            continue

                        for codigo in codigos:
                            try:
                                # nombre entre código y (21.00)
                                nombre = texto.split(codigo)[1]
                                nombre = nombre.split("(21.00)")[0].strip()

                                # números al final
                                nums = re.findall(r"\d+\.\d+", texto)
                                if len(nums) < 2:
                                    continue

                                precio_unitario = float(nums[-2])

                                productos.append({
                                    "codigo": codigo,
                                    "nombre": nombre,
                                    "precio": precio_unitario,
                                    "precio_venta": precio_venta(precio_unitario)
                                })
                            except:
                                continue

    return productos

# -- exportar Excel --
def generar_excel(productos, output_path):
    df = pd.DataFrame(productos)
    df.to_excel(output_path, index=False)
