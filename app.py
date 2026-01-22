from flask import Flask, render_template, request, redirect, url_for

import sqlite3
import requests
import re
import imghdr
import base64

app = Flask(__name__)
# -----------------------------
# FORMATOS DE IMAGEN PERMITIDOS
# -----------------------------
FORMATOS_PERMITIDOS = {"jpeg", "jpg", "png", "webp"}

REGEX_NOMBRE = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$"
REGEX_CORREO = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"


SITE_KEY = "6LehvUQsAAAAAGldvO1QR8Da4yc3upv2yP3sgmgR"
SECRET_KEY = "6LehvUQsAAAAANusKcHRfF0w5DkX0L1JYl8Ae28Q"

def get_db():
    return sqlite3.connect("database.db")

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS registros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        mensaje TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route("/", methods=["GET", "POST"])
def index():
    mensaje = ""

    if request.method == "POST":
        recaptcha_response = request.form.get("g-recaptcha-response")

        data = {
            "secret": SECRET_KEY,
            "response": recaptcha_response
        }

        r = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data=data
        )

        result = r.json()

        if result["success"]:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO registros (nombre, mensaje)
                VALUES (?, ?)
            """, ("Prueba", "Desarrollo Web"))
            conn.commit()
            conn.close()

            mensaje = "Datos guardados correctamente ✅"
        else:
            mensaje = "reCAPTCHA inválido ❌"

    # Obtener registros
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, mensaje FROM registros")

    registros = cursor.fetchall()
    conn.close()

    return render_template(
        "index.html",
        site_key=SITE_KEY,
        mensaje=mensaje,
        registros=registros
    )
    
@app.route("/eliminar/<int:id>", methods=["POST"])
def eliminar_registro(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM registros WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))



@app.route("/bienvenida")
def bienvenida():
    return render_template("bienvenida.html")

# -----------------------------
# CALCULADORA (SIN VALIDACIÓN)
# -----------------------------
@app.route("/operaciones", methods=["GET", "POST"])
def operaciones():
    suma = None
    division = None

    if request.method == "POST":
        a = request.form.get("a")
        b = request.form.get("b")
        c = request.form.get("c")
        d = request.form.get("d")

        # SIN validación a propósito
        suma = int(a) + int(b)
        division = int(c) / int(d)

    return render_template(
        "operaciones.html",
        suma=suma,
        division=division
    )


# -----------------------------
# FORMULARIO CON VALIDACIÓN
# -----------------------------
@app.route("/validacion", methods=["GET", "POST"])
def validacion():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    mensaje = None

    if request.method == "POST":

        nombre = request.form.get("nombre", "").strip()
        fecha_nacimiento = request.form.get("fecha_nacimiento")
        sexo = request.form.get("sexo")
        telefono = request.form.get("telefono")
        correo = request.form.get("correo", "").strip()
        correo2 = request.form.get("correo2", "").strip()
        direccion = request.form.get("direccion")
        observaciones = request.form.get("observaciones")

        # -----------------------------
        # VALIDAR NOMBRE (SOLO LETRAS)
        # -----------------------------
        if not re.match(REGEX_NOMBRE, nombre):
            mensaje = "❌ El nombre solo debe contener letras y espacios"

        # -----------------------------
        # VALIDAR CORREO (SINTAXIS)
        # -----------------------------
        elif not re.match(REGEX_CORREO, correo):
            mensaje = "❌ El correo no tiene un formato válido"

        # -----------------------------
        # VALIDAR CORREOS IGUALES
        # -----------------------------
        elif correo != correo2:
            mensaje = "❌ Los correos no coinciden"

        else:
            # -----------------------------
            # VALIDAR IMAGEN
            # -----------------------------
            foto = request.files.get("foto")

            if not foto:
                mensaje = "❌ Debes subir una fotografía"
            else:
                foto_bytes = foto.read()
                tipo_imagen = imghdr.what(None, foto_bytes)

                if tipo_imagen not in FORMATOS_PERMITIDOS:
                    mensaje = "❌ Solo se permiten imágenes JPG, PNG o WEBP"
                else:
                    foto_base64 = base64.b64encode(foto_bytes).decode("utf-8")

                    # -----------------------------
                    # GUARDAR EN BD
                    # -----------------------------
                    cursor.execute("""
                        INSERT INTO formularios
                        (nombre, fecha_nacimiento, sexo, telefono, correo, direccion, observaciones, foto)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        nombre,
                        fecha_nacimiento,
                        sexo,
                        telefono,
                        correo,
                        direccion,
                        observaciones,
                        foto_base64
                    ))

                    conn.commit()
                    mensaje = "✅ Registro guardado correctamente"

    # -----------------------------
    # OBTENER REGISTROS
    # -----------------------------
    cursor.execute("""
        SELECT nombre, fecha_nacimiento, correo, foto
        FROM formularios
        ORDER BY id DESC
    """)
    registros = cursor.fetchall()

    conn.close()

    return render_template(
        "validacion.html",
        mensaje=mensaje,
        registros=registros
    )

    mensaje = ""

    if request.method == "POST":
        nombre = request.form.get("nombre")
        edad = request.form.get("edad")
        correo = request.form.get("correo")
        correo2 = request.form.get("correo2")
        foto = request.files.get("foto")

        if not nombre or not edad or not correo or not correo2 or not foto:
            mensaje = "Todos los campos son obligatorios"
        elif not edad.isdigit():
            mensaje = "La edad debe ser numérica"
        elif correo != correo2:
            mensaje = "Los correos no coinciden"
        else:
            foto_bytes = foto.read()

            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO formularios (nombre, edad, correo, foto)
                VALUES (?, ?, ?, ?)
            """, (nombre, int(edad), correo, foto_bytes))
            conn.commit()
            conn.close()

            mensaje = "Formulario guardado correctamente ✅"

    # 🔽 OBTENER DATOS PARA MOSTRAR
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, edad, correo, foto FROM formularios")
    datos = cursor.fetchall()
    conn.close()

    # Convertir imagen a Base64
    registros = []
    for d in datos:
        imagen_base64 = base64.b64encode(d[3]).decode("utf-8")
        registros.append((d[0], d[1], d[2], imagen_base64))

    return render_template(
        "validacion.html",
        mensaje=mensaje,
        registros=registros
    )

# -----------------------------
# PÁGINA DE ERRORES (MANUAL)
# -----------------------------
@app.route("/error")
def error():
    return render_template("error.html", error="Página de errores")


# -----------------------------
# MANEJO DE ERRORES
# -----------------------------
@app.errorhandler(404)
def error_404(e):
    return render_template("error.html", error="404 - Página no encontrada"), 404


@app.errorhandler(500)
def error_500(e):
    return render_template("error.html", error="500 - Error interno del servidor"), 500

if __name__ == "__main__":
    app.run(debug=True)
