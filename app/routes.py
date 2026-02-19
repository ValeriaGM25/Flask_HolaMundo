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
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask import jsonify

main_routes = Blueprint("main", __name__)

# -----------------------------
# CONFIG / CONSTANTES
# -----------------------------
FORMATOS_PERMITIDOS = {"jpeg", "jpg", "png", "webp"}
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
REGEX_NUMERO = r"^[0-9]+$"
REGEX_NOMBRE = r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$"
REGEX_CORREO = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

SITE_KEY = "6LehvUQsAAAAAGldvO1QR8Da4yc3upv2yP3sgmgR"
SECRET_KEY = "6LehvUQsAAAAANusKcHRfF0w5DkX0L1JYl8Ae28Q"

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

#-------------------------------
#CRUD
#-------------------------------
from datetime import date
from flask import render_template, request, redirect, url_for, flash

@main_routes.route("/crud", methods=["GET", "POST"])
def crud():
    conn = get_db()
    cursor = conn.cursor()

    # --------------------------
    # CREAR (POST)
    # --------------------------
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        mensaje = request.form.get("mensaje", "").strip()
        categoria = request.form.get("categoria", "").strip()
        estado = request.form.get("estado", "activo").strip()

        # numéricos (con default)
        try:
            precio = float(request.form.get("precio", "0") or 0)
        except ValueError:
            precio = -1

        try:
            stock = int(request.form.get("stock", "0") or 0)
        except ValueError:
            stock = -1

        if not nombre or not mensaje:
            flash("❌ Nombre y Mensaje son obligatorios.", "danger")
            conn.close()
            return redirect(url_for("main.crud"))

        if precio < 0:
            flash("❌ Precio inválido.", "danger")
            conn.close()
            return redirect(url_for("main.crud"))

        if stock < 0:
            flash("❌ Stock inválido.", "danger")
            conn.close()
            return redirect(url_for("main.crud"))

        created_at = request.form.get("created_at") or date.today().isoformat()

        cursor.execute("""
            INSERT INTO registros (nombre, mensaje, categoria, precio, stock, estado, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nombre, mensaje, categoria, precio, stock, estado, created_at))
        conn.commit()
        conn.close()
        flash("✅ Registro creado correctamente.", "success")
        return redirect(url_for("main.crud"))

    # --------------------------
    # FILTROS (GET) COMPLEJOS
    # --------------------------
    q = request.args.get("q", "").strip()
    categoria = request.args.get("categoria", "").strip()
    estado = request.args.get("estado", "").strip()

    precio_min = request.args.get("precio_min", "").strip()
    precio_max = request.args.get("precio_max", "").strip()

    stock_min = request.args.get("stock_min", "").strip()
    stock_max = request.args.get("stock_max", "").strip()

    fecha_desde = request.args.get("fecha_desde", "").strip()
    fecha_hasta = request.args.get("fecha_hasta", "").strip()

    orden = request.args.get("orden", "recientes")  # recientes, precio_asc, precio_desc, nombre_asc

    where = []
    params = []

    # texto libre sobre nombre o mensaje
    if q:
        where.append("(nombre LIKE ? OR mensaje LIKE ?)")
        params.extend([f"%{q}%", f"%{q}%"])

    if categoria:
        where.append("categoria = ?")
        params.append(categoria)

    if estado:
        where.append("estado = ?")
        params.append(estado)

    # rangos numéricos
    if precio_min:
        where.append("precio >= ?")
        params.append(float(precio_min))
    if precio_max:
        where.append("precio <= ?")
        params.append(float(precio_max))

    if stock_min:
        where.append("stock >= ?")
        params.append(int(stock_min))
    if stock_max:
        where.append("stock <= ?")
        params.append(int(stock_max))

    # rango de fechas (YYYY-MM-DD)
    if fecha_desde:
        where.append("created_at >= ?")
        params.append(fecha_desde)
    if fecha_hasta:
        where.append("created_at <= ?")
        params.append(fecha_hasta)

    sql = """
        SELECT id, nombre, mensaje, categoria, precio, stock, estado, created_at
        FROM registros
    """
    if where:
        sql += " WHERE " + " AND ".join(where)

    # orden
    if orden == "precio_asc":
        sql += " ORDER BY precio ASC"
    elif orden == "precio_desc":
        sql += " ORDER BY precio DESC"
    elif orden == "nombre_asc":
        sql += " ORDER BY nombre ASC"
    else:
        sql += " ORDER BY id DESC"

    cursor.execute(sql, params)
    registros = cursor.fetchall()

    # para llenar select de categorías disponibles
    cursor.execute("SELECT DISTINCT categoria FROM registros WHERE categoria IS NOT NULL AND categoria <> '' ORDER BY categoria")
    categorias_db = [r[0] for r in cursor.fetchall()]

    conn.close()

    breadcrumb = [
        {"label": "Bienvenida", "url": url_for("main.welcome")},
        {"label": "Home", "url": url_for("main.home")},
        {"label": "CRUD", "url": url_for("main.crud")}
    ]

    return render_template(
        "crud.html",
        registros=registros,
        breadcrumb=breadcrumb,
        # filtros
        q=q, categoria=categoria, estado=estado,
        precio_min=precio_min, precio_max=precio_max,
        stock_min=stock_min, stock_max=stock_max,
        fecha_desde=fecha_desde, fecha_hasta=fecha_hasta,
        orden=orden,
        categorias_db=categorias_db
    )

from datetime import date
from flask import render_template, request, redirect, url_for, flash

@main_routes.route("/crud/editar/<int:id>", methods=["GET", "POST"])
def crud_editar(id):
    conn = get_db()
    cursor = conn.cursor()

    # Traer registro
    cursor.execute("""
        SELECT id, nombre, mensaje, categoria, precio, stock, estado, created_at
        FROM registros
        WHERE id = ?
    """, (id,))
    registro = cursor.fetchone()

    if not registro:
        conn.close()
        flash("❌ Registro no encontrado.", "danger")
        return redirect(url_for("main.crud"))

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        mensaje = request.form.get("mensaje", "").strip()
        categoria = request.form.get("categoria", "").strip()
        estado = request.form.get("estado", "activo").strip()
        created_at = request.form.get("created_at") or (registro[7] or date.today().isoformat())

        # numéricos
        try:
            precio = float(request.form.get("precio", "0") or 0)
        except ValueError:
            precio = -1

        try:
            stock = int(request.form.get("stock", "0") or 0)
        except ValueError:
            stock = -1

        # validaciones básicas
        if not nombre or not mensaje:
            flash("❌ Nombre y Mensaje son obligatorios.", "danger")
            conn.close()
            return redirect(url_for("main.crud_editar", id=id))

        if precio < 0:
            flash("❌ Precio inválido.", "danger")
            conn.close()
            return redirect(url_for("main.crud_editar", id=id))

        if stock < 0:
            flash("❌ Stock inválido.", "danger")
            conn.close()
            return redirect(url_for("main.crud_editar", id=id))

        cursor.execute("""
            UPDATE registros
            SET nombre = ?, mensaje = ?, categoria = ?, precio = ?, stock = ?, estado = ?, created_at = ?
            WHERE id = ?
        """, (nombre, mensaje, categoria, precio, stock, estado, created_at, id))

        conn.commit()
        conn.close()

        flash("✅ Registro actualizado.", "success")
        return redirect(url_for("main.crud"))

    conn.close()

    breadcrumb = [
        {"label": "Bienvenida", "url": url_for("main.welcome")},
        {"label": "CRUD", "url": url_for("main.crud")},
        {"label": f"Editar #{registro[0]}", "url": url_for("main.crud_editar", id=id)}
    ]

    return render_template(
        "crud_editar.html",
        registro=registro,
        breadcrumb=breadcrumb
    )


@main_routes.route("/crud/eliminar/<int:id>", methods=["POST"])
def crud_eliminar(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM registros WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("🗑️ Registro eliminado.", "success")
    return redirect(url_for("main.crud"))


# -------------------------------
# API (FETCH) - LISTAR CON FILTROS
# -------------------------------
@main_routes.route("/api/registros", methods=["GET"])
def api_registros_listar():
    conn = get_db()
    cursor = conn.cursor()

    # mismos filtros que tu /crud
    q = request.args.get("q", "").strip()
    categoria = request.args.get("categoria", "").strip()
    estado = request.args.get("estado", "").strip()

    precio_min = request.args.get("precio_min", "").strip()
    precio_max = request.args.get("precio_max", "").strip()

    stock_min = request.args.get("stock_min", "").strip()
    stock_max = request.args.get("stock_max", "").strip()

    fecha_desde = request.args.get("fecha_desde", "").strip()
    fecha_hasta = request.args.get("fecha_hasta", "").strip()

    orden = request.args.get("orden", "recientes")

    where = []
    params = []

    if q:
        where.append("(nombre LIKE ? OR mensaje LIKE ?)")
        params.extend([f"%{q}%", f"%{q}%"])

    if categoria:
        where.append("categoria = ?")
        params.append(categoria)

    if estado:
        where.append("estado = ?")
        params.append(estado)

    # rangos numéricos con try por si mandan basura
    try:
        if precio_min:
            where.append("precio >= ?")
            params.append(float(precio_min))
        if precio_max:
            where.append("precio <= ?")
            params.append(float(precio_max))
    except ValueError:
        conn.close()
        return jsonify({"ok": False, "error": "precio_min/precio_max inválido"}), 400

    try:
        if stock_min:
            where.append("stock >= ?")
            params.append(int(stock_min))
        if stock_max:
            where.append("stock <= ?")
            params.append(int(stock_max))
    except ValueError:
        conn.close()
        return jsonify({"ok": False, "error": "stock_min/stock_max inválido"}), 400

    if fecha_desde:
        where.append("created_at >= ?")
        params.append(fecha_desde)
    if fecha_hasta:
        where.append("created_at <= ?")
        params.append(fecha_hasta)

    sql = """
        SELECT id, nombre, mensaje, categoria, precio, stock, estado, created_at
        FROM registros
    """
    if where:
        sql += " WHERE " + " AND ".join(where)

    if orden == "precio_asc":
        sql += " ORDER BY precio ASC"
    elif orden == "precio_desc":
        sql += " ORDER BY precio DESC"
    elif orden == "nombre_asc":
        sql += " ORDER BY nombre ASC"
    else:
        sql += " ORDER BY id DESC"

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()

    items = [{
        "id": r[0],
        "nombre": r[1],
        "mensaje": r[2],
        "categoria": r[3],
        "precio": r[4],
        "stock": r[5],
        "estado": r[6],
        "created_at": r[7],
    } for r in rows]

    return jsonify({"ok": True, "items": items})


# -------------------------------
# API (FETCH) - CREAR
# -------------------------------
@main_routes.route("/api/registros", methods=["POST"])
def api_registros_crear():
    body = request.get_json(silent=True) or {}

    nombre = (body.get("nombre") or "").strip()
    mensaje = (body.get("mensaje") or "").strip()
    categoria = (body.get("categoria") or "").strip()
    estado = (body.get("estado") or "activo").strip()
    created_at = (body.get("created_at") or date.today().isoformat()).strip()

    try:
        precio = float(body.get("precio", 0) or 0)
        stock = int(body.get("stock", 0) or 0)
    except ValueError:
        return jsonify({"ok": False, "error": "Precio/Stock inválidos"}), 400

    if not nombre or not mensaje:
        return jsonify({"ok": False, "error": "Nombre y Mensaje son obligatorios"}), 400
    if precio < 0 or stock < 0:
        return jsonify({"ok": False, "error": "Precio/Stock no pueden ser negativos"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO registros (nombre, mensaje, categoria, precio, stock, estado, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nombre, mensaje, categoria, precio, stock, estado, created_at))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({"ok": True, "id": new_id})


# -------------------------------
# API (FETCH) - ELIMINAR
# -------------------------------
@main_routes.route("/api/registros/<int:id>", methods=["DELETE"])
def api_registros_eliminar(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM registros WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


# -------------------------------
# API (FETCH) - EDITAR (PUT) (opcional recomendado)
# -------------------------------
@main_routes.route("/api/registros/<int:id>", methods=["PUT"])
def api_registros_editar(id):
    body = request.get_json(silent=True) or {}

    nombre = (body.get("nombre") or "").strip()
    mensaje = (body.get("mensaje") or "").strip()
    categoria = (body.get("categoria") or "").strip()
    estado = (body.get("estado") or "activo").strip()
    created_at = (body.get("created_at") or date.today().isoformat()).strip()

    try:
        precio = float(body.get("precio", 0) or 0)
        stock = int(body.get("stock", 0) or 0)
    except ValueError:
        return jsonify({"ok": False, "error": "Precio/Stock inválidos"}), 400

    if not nombre or not mensaje:
        return jsonify({"ok": False, "error": "Nombre y Mensaje son obligatorios"}), 400
    if precio < 0 or stock < 0:
        return jsonify({"ok": False, "error": "Precio/Stock no pueden ser negativos"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE registros
        SET nombre = ?, mensaje = ?, categoria = ?, precio = ?, stock = ?, estado = ?, created_at = ?
        WHERE id = ?
    """, (nombre, mensaje, categoria, precio, stock, estado, created_at, id))
    conn.commit()
    conn.close()

    return jsonify({"ok": True})
