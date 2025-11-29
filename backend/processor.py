import pdfplumber
import re
import math
import pandas as pd


codigo_regex = r"[A-Z]{4,5}\d{2}"
num_regex = r"-?\d+(?:[.,]\d+)"  # Detecta números con coma o punto


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


def extraer_productos(path_pdf):
    productos = []

    with pdfplumber.open(path_pdf) as pdf:
        for page in pdf.pages:
            lineas = [l.strip() for l in page.extract_text().split("\n")]

            buffer_nombre = []  # Guarda líneas de nombre previas al código

            for i, linea in enumerate(lineas):

                # Ignorar descuentos
                if "General" in linea and re.search(r"-\d", linea):
                    continue

                # Detectar línea con código + precios
                cod_match = re.search(codigo_regex, linea)
                if not cod_match:
                    # Si no hay código, esta línea puede ser parte del nombre
                    if linea and not re.match(num_regex, linea):
                        buffer_nombre.append(linea)
                    continue

                codigo = cod_match.group(0)

                # Extraer números de la línea
                nums = re.findall(num_regex, linea.replace(",", "."))

                # Casos AMAN02: código + nombre + precios en una sola línea
                if len(nums) >= 3:
                    cantidad = float(nums[-3])
                    unitario = float(nums[-2])
                    total = float(nums[-1])
                else:
                    continue

                # Quitar código y números para dejar solo lo que es nombre
                texto_sin_codigo = re.sub(codigo_regex, "", linea)
                texto_sin_nums = re.sub(num_regex, "", texto_sin_codigo)
                texto_sin_iva = texto_sin_nums.replace("(21.00)", "").strip()

                nombre_linea = texto_sin_iva

                # Armar nombre completo combinando buffer + nombre de la misma línea
                nombre_partes = buffer_nombre.copy()
                if nombre_linea:
                    nombre_partes.append(nombre_linea)

                nombre = " ".join(nombre_partes).strip()

                # Guardar producto
                productos.append({
                    "codigo": codigo,
                    "nombre": nombre,
                    "precio": unitario,
                    "precio_venta": precio_venta(unitario)
                })

                # Resetear buffer porque empieza un producto nuevo
                buffer_nombre = []

    return productos


def generar_excel(productos, output_path="resultado.xlsx"):
    df = pd.DataFrame(productos)
    df.to_excel(output_path, index=False)
    print("✔ Excel generado:", output_path)