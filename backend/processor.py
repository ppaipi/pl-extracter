import pdfplumber
import re
import math
import pandas as pd

# -----------------------------
# REGLAS DE PRECIO
# -----------------------------
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


# -----------------------------
# EXTRACCIÓN PDF
# -----------------------------
def extraer_productos(path_pdf):
    productos = []

    codigo_regex = r"[A-Z]{4,5}\d{2}"

    # precios: acepta 11683,92 o 21040 o 11683.92
    precio_regex = r"\d+(?:[.,]\d+)?"

    with pdfplumber.open(path_pdf) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    for cell in row:
                        if not cell:
                            continue

                        texto = cell.replace("\n", " ").strip()

                        # 1) Buscar código
                        codigos = re.findall(codigo_regex, texto)
                        if not codigos:
                            continue

                        for codigo in codigos:
                            try:
                                # 2) Detectar precios (2 últimos números)
                                nums = re.findall(precio_regex, texto)

                                if len(nums) < 2:
                                    continue

                                # precios en formato seguro
                                precio_unitario_str = nums[-2].replace(",", ".")
                                precio_unitario = float(precio_unitario_str)

                                # 3) Nombre: texto entre código y primer precio
                                pos_codigo = texto.find(codigo)
                                pos_precio = texto.find(nums[-2])

                                nombre = texto[pos_codigo + len(codigo):pos_precio].strip()

                                if nombre == "":
                                    nombre = "(SIN NOMBRE)"

                                productos.append({
                                    "codigo": codigo,
                                    "nombre": nombre,
                                    "precio": precio_unitario,
                                    "precio_venta": precio_venta(precio_unitario)
                                })

                            except Exception as e:
                                print("Error en fila:", texto)
                                print("Detalle:", e)
                                continue

    return productos


# -----------------------------
# GENERAR EXCEL
# -----------------------------
def generar_excel(productos, output_path):
    df = pd.DataFrame(productos)
    df.to_excel(output_path, index=False)
