from flask import Flask, request, send_file
from flask_cors import CORS
import os
from processor import extraer_productos, generar_excel

app = Flask(__name__)
CORS(app)

# Carpeta base donde está ESTE archivo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Carpetas internas del backend
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")

# Crear carpetas si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return {"error": "No se envió archivo"}, 400

    f = request.files["file"]
    pdf_path = os.path.join(UPLOAD_FOLDER, f.filename)
    f.save(pdf_path)

    productos = extraer_productos(pdf_path)

    output_path = os.path.join(OUTPUT_FOLDER, "resultado.xlsx")
    generar_excel(productos, output_path)

    return send_file(output_path, as_attachment=True)

@app.route("/")
def home():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(port=5000, debug=True)
