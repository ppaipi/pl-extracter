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

# Regex generales
codigo_regex = r"[A-Z]{4,5}\d{2}"
precio_regex = r"\d{1,3}(?:\.\d{3})*,\d{2}"  # acepta 11.234,56 ó 234,50

def limpiar_precio(p):
    """ Convertir 11.234,56 -> 11234.56 """
    p = p.replace(".", "").replace(",", ".")
    return float(p)

def extraer_productos(path_pdf):
    productos = []

    with pdfplumber.open(path_pdf) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            lineas = text.split("\n")

            for linea in lineas:
                codigos = re.findall(codigo_regex, linea)
                if not codigos:
                    continue

                codigo = codigos[0]

                # encontrar precios (puede haber 1 o 2)
                precios = re.findall(precio_regex, linea)
                if not precios:
                    continue

                precio_unitario = limpiar_precio(precios[-1])  # último precio de la línea

                # nombre = texto entre código y el primer precio encontrado
                idx_codigo = linea.find(codigo) + len(codigo)
                idx_precio = linea.find(precios[0])
                nombre = linea[idx_codigo:idx_precio].strip()

                # limpiar nombre (dobles espacios, basura)
                nombre = re.sub(r"\s+", " ", nombre)

                productos.append({
                    "codigo": codigo,
                    "nombre": nombre,
                    "precio": precio_unitario,
                    "precio_venta": precio_venta(precio_unitario)
                })

    return productos


def generar_excel(productos, output_path):
    df = pd.DataFrame(productos)
    df.to_excel(output_path, index=False)
