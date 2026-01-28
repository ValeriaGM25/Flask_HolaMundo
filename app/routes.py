from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3
import requests
import re
import imghdr
import base64

import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from . import get_db   

main_routes = Blueprint("main", __name__)

# -----------------------------
# CONFIG / CONSTANTES
# -----------------------------
FORMATOS_PERMITIDOS = {"jpeg", "jpg", "png", "webp"}
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
REGEX_NUMERO = r"^[0-9]+$"
REGEX_NOMBRE = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$"
REGEX_CORREO = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

SITE_KEY = " 6LehvUQsAAAAAGldvO1QR8Da4yc3upv2yP3sgmgR"
SECRET_KEY = " 6LehvUQsAAAAANusKcHRfF0w5DkX0L1JYl8Ae28Q"

def get_db():
    return sqlite3.connect("database.db")


def allowed_file(filename: str) -> bool:
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext in ALLOWED_EXTENSIONS


def breadcrumb_home():
    return [{"label": "Inicio", "url": url_for("main.home")}]


# -----------------------------
# BIENVENIDA -> HOME
# -----------------------------
@main_routes.route("/")
def welcome():
    return render_template(
        "welcome.html",
        breadcrumb=[{"label": "Bienvenida", "url": url_for("main.welcome")}],
    )

@main_routes.route("/home", methods=["GET", "POST"])
def home():
    mensaje = ""

    if request.method == "POST":
        recaptcha_response = request.form.get("g-recaptcha-response")

        data = {"secret": SECRET_KEY, "response": recaptcha_response}
        r = requests.post("https://www.google.com/recaptcha/api/siteverify", data=data)
        result = r.json()

        if result.get("success"):
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

    # ---- registros (lo tuyo) ----
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, mensaje FROM registros")
    registros = cursor.fetchall()

    # ---- imágenes carrusel (nuevo) ----
    cursor.execute("SELECT id, filename FROM carousel_images ORDER BY id DESC")
    carousel_images = cursor.fetchall()

    conn.close()

    return render_template(
        "index.html",
        site_key=SITE_KEY,
        mensaje=mensaje,
        registros=registros,
        carousel_images=carousel_images,
        breadcrumb=[
            {"label": "Inicio", "url": url_for("main.home")},
            {"label": "Home", "url": url_for("main.home")},
        ],
    )

    mensaje = ""

    if request.method == "POST":
        recaptcha_response = request.form.get("g-recaptcha-response")

        data = {"secret": SECRET_KEY, "response": recaptcha_response}
        r = requests.post("https://www.google.com/recaptcha/api/siteverify", data=data)
        result = r.json()

        if result.get("success"):
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
    
@main_routes.route("/upload_slide", methods=["POST"])
def upload_slide():
    file = request.files.get("slide")

    if not file or file.filename.strip() == "":
        return redirect(url_for("main.home"))

    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in ALLOWED_EXTENSIONS:
        return redirect(url_for("main.home"))

    # carpeta static/uploads
    upload_folder = os.path.join(current_app.static_folder, "uploads")
    os.makedirs(upload_folder, exist_ok=True)

    # nombre único para evitar choques
    new_name = f"{uuid.uuid4().hex}.{ext}"
    file.save(os.path.join(upload_folder, new_name))

    # guardar en BD
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO carousel_images (filename) VALUES (?)", (new_name,))
    conn.commit()
    conn.close()

    return redirect(url_for("main.home"))


@main_routes.route("/eliminar/<int:id>", methods=["POST"])
def eliminar_registro(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM registros WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("main.home"))


# -----------------------------
# CALCULADORA
# -----------------------------
@main_routes.route("/operaciones", methods=["GET", "POST"])
def operaciones():
    suma = None
    division = None

    REGEX_NUMERO = r"^[0-9]+$"

    if request.method == "POST":
        op = request.form.get("op")

        # -----------------
        # SUMA
        # -----------------
        if op == "sumar":
            a = request.form.get("a", "").strip()
            b = request.form.get("b", "").strip()

            if not re.match(REGEX_NUMERO, a) or not re.match(REGEX_NUMERO, b):
                return render_template(
                    "error.html",
                    error="❌ Solo se permiten números enteros (sin letras ni símbolos)"
                ), 400

            suma = int(a) + int(b)

        # -----------------
        # DIVISIÓN
        # -----------------
        elif op == "dividir":
            c = request.form.get("c", "").strip()
            d = request.form.get("d", "").strip()

            if not re.match(REGEX_NUMERO, c) or not re.match(REGEX_NUMERO, d):
                return render_template(
                    "error.html",
                    error="❌ Solo se permiten números enteros (sin letras ni símbolos)"
                ), 400

            divisor = int(d)
            if divisor == 0:
                return render_template(
                    "error.html",
                    error="❌ No se puede dividir entre cero"
                ), 400

            division = int(c) / divisor

        # -----------------
        # OPERACIÓN INVÁLIDA
        # -----------------
        else:
            return render_template(
                "error.html",
                error="❌ Operación no válida"
            ), 400

    return render_template(
        "operaciones.html",
        suma=suma,
        division=division,
        breadcrumb=[
            {"label": "Inicio", "url": url_for("main.home")},
            {"label": "Calculadora", "url": url_for("main.operaciones")},
        ],
    )
    
    
# -----------------------------
# FORMULARIO CON VALIDACIÓN
# -----------------------------
@main_routes.route("/validacion", methods=["GET", "POST"])
def validacion():
    conn = get_db()
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

        if not re.match(REGEX_NOMBRE, nombre):
            mensaje = "❌ El nombre solo debe contener letras y espacios"
        elif not re.match(REGEX_CORREO, correo):
            mensaje = "❌ El correo no tiene un formato válido"
        elif correo != correo2:
            mensaje = "❌ Los correos no coinciden"
        else:
            foto = request.files.get("foto")
            if not foto:
                mensaje = "❌ Debes subir una fotografía"
            else:
                foto_bytes = foto.read()
                tipo_imagen = imghdr.what(None, foto_bytes)

                if tipo_imagen not in FORMATOS_PERMITIDOS:
                    mensaje = "❌ Solo se permiten imágenes JPG, PNG o WEBP"
                else:
                    # Base64 de la imagen
                    foto_base64 = base64.b64encode(foto_bytes).decode("utf-8")

                    # MIME type real para mostrar en HTML (data:image/...;base64,)
                    # Ej: image/png, image/jpeg, image/webp
                    foto_tipo = foto.mimetype or f"image/{tipo_imagen}"

                    # Normalizar jpg -> jpeg
                    if foto_tipo == "image/jpg":
                        foto_tipo = "image/jpeg"

                    cursor.execute("""
                        INSERT INTO formularios
                        (nombre, fecha_nacimiento, sexo, telefono, correo, direccion, observaciones, foto, foto_tipo)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        nombre,
                        fecha_nacimiento,
                        sexo,
                        telefono,
                        correo,
                        direccion,
                        observaciones,
                        foto_base64,
                        foto_tipo
                    ))

                    conn.commit()
                    mensaje = "✅ Registro guardado correctamente"

    cursor.execute("""
        SELECT nombre, fecha_nacimiento, correo, foto, foto_tipo
        FROM formularios
        ORDER BY id DESC
    """)
    registros = cursor.fetchall()
    conn.close()

    return render_template("validacion.html", mensaje=mensaje, registros=registros,  breadcrumb=[
            {"label": "Inicio", "url": url_for("main.home")},
            {"label": "Formulario", "url": url_for("main.validacion")},
        ],)

@main_routes.route("/eliminar_formulario/<int:id>", methods=["POST"])
def eliminar_formulario(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM formularios WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("main.validacion"))


# -----------------------------
# ERRORES
# -----------------------------
@main_routes.route("/error")
def error_page():
    return render_template("error.html", error="Página de errores",breadcrumb=[
            {"label": "Inicio", "url": url_for("main.home")},
            {"label": "Errores", "url": url_for("main.error_page")},
        ],
)

@main_routes.app_errorhandler(404)
def error_404(e):
    return render_template("error.html", error="404 - Página no encontrada"), 404

@main_routes.app_errorhandler(500)
def error_500(e):
    return render_template("error.html", error="500 - Error interno del servidor"), 500
