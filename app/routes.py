# app/routes.py
from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, jsonify, current_app
)
import sqlite3
import requests
import re
import imghdr
import base64
import os
import uuid
from datetime import date
from werkzeug.utils import secure_filename

# ✅ IMPORTA get_db DESDE __init__.py (NO lo redefinas aquí)
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

SITE_KEY = "6LehvUQsAAAAAGldvO1QR8Da4yc3upv2yP3sgmgR"
SECRET_KEY = "6LehvUQsAAAAANusKcHRfF0w5DkX0L1JYl8Ae28Q"


def allowed_file(filename: str) -> bool:
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext in ALLOWED_EXTENSIONS


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
            cursor.execute(
                """
                INSERT INTO registros (nombre, mensaje)
                VALUES (?, ?)
                """,
                ("Prueba", "Desarrollo Web"),
            )
            conn.commit()
            conn.close()
            mensaje = "Datos guardados correctamente ✅"
        else:
            mensaje = "reCAPTCHA inválido ❌"

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, nombre, mensaje FROM registros ORDER BY id DESC")
    registros = cursor.fetchall()

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
            {"label": "Inicio", "url": url_for("main.welcome")},
            {"label": "Home", "url": url_for("main.home")},
        ],
    )


@main_routes.route("/upload_slide", methods=["POST"])
def upload_slide():
    file = request.files.get("slide")

    if not file or file.filename.strip() == "":
        return redirect(url_for("main.home"))

    filename = secure_filename(file.filename)
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in ALLOWED_EXTENSIONS:
        flash("❌ Formato no permitido. Solo JPG, JPEG, PNG o WEBP.", "danger")
        return redirect(url_for("main.home"))

    upload_folder = os.path.join(current_app.static_folder, "uploads")
    os.makedirs(upload_folder, exist_ok=True)

    new_name = f"{uuid.uuid4().hex}.{ext}"
    file.save(os.path.join(upload_folder, new_name))

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO carousel_images (filename) VALUES (?)", (new_name,))
    conn.commit()
    conn.close()

    flash("✅ Imagen subida al carrusel.", "success")
    return redirect(url_for("main.home"))


@main_routes.route("/eliminar/<int:id>", methods=["POST"])
def eliminar_registro(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM registros WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("🗑️ Registro eliminado.", "success")
    return redirect(url_for("main.home"))


# -----------------------------
# CALCULADORA
# -----------------------------
@main_routes.route("/operaciones", methods=["GET", "POST"])
def operaciones():
    suma = None
    division = None

    if request.method == "POST":
        op = request.form.get("op")

        if op == "sumar":
            a = request.form.get("a", "").strip()
            b = request.form.get("b", "").strip()

            if not re.match(REGEX_NUMERO, a) or not re.match(REGEX_NUMERO, b):
                return (
                    render_template(
                        "error.html",
                        error="❌ Solo se permiten números enteros (sin letras ni símbolos)",
                        breadcrumb=[
                            {"label": "Inicio", "url": url_for("main.welcome")},
                            {"label": "Calculadora", "url": url_for("main.operaciones")},
                        ],
                    ),
                    400,
                )

            suma = int(a) + int(b)

        elif op == "dividir":
            c = request.form.get("c", "").strip()
            d = request.form.get("d", "").strip()

            if not re.match(REGEX_NUMERO, c) or not re.match(REGEX_NUMERO, d):
                return (
                    render_template(
                        "error.html",
                        error="❌ Solo se permiten números enteros (sin letras ni símbolos)",
                        breadcrumb=[
                            {"label": "Inicio", "url": url_for("main.welcome")},
                            {"label": "Calculadora", "url": url_for("main.operaciones")},
                        ],
                    ),
                    400,
                )

            divisor = int(d)
            if divisor == 0:
                return (
                    render_template(
                        "error.html",
                        error="❌ No se puede dividir entre cero",
                        breadcrumb=[
                            {"label": "Inicio", "url": url_for("main.welcome")},
                            {"label": "Calculadora", "url": url_for("main.operaciones")},
                        ],
                    ),
                    400,
                )

            division = int(c) / divisor

        else:
            return (
                render_template(
                    "error.html",
                    error="❌ Operación no válida",
                    breadcrumb=[
                        {"label": "Inicio", "url": url_for("main.welcome")},
                        {"label": "Calculadora", "url": url_for("main.operaciones")},
                    ],
                ),
                400,
            )

    return render_template(
        "operaciones.html",
        suma=suma,
        division=division,
        breadcrumb=[
            {"label": "Inicio", "url": url_for("main.welcome")},
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
                    foto_base64 = base64.b64encode(foto_bytes).decode("utf-8")
                    foto_tipo = foto.mimetype or f"image/{tipo_imagen}"
                    if foto_tipo == "image/jpg":
                        foto_tipo = "image/jpeg"

                    cursor.execute(
                        """
                        INSERT INTO formularios
                        (nombre, fecha_nacimiento, sexo, telefono, correo, direccion, observaciones, foto, foto_tipo)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            nombre,
                            fecha_nacimiento,
                            sexo,
                            telefono,
                            correo,
                            direccion,
                            observaciones,
                            foto_base64,
                            foto_tipo,
                        ),
                    )

                    conn.commit()
                    mensaje = "✅ Registro guardado correctamente"

    cursor.execute(
        """
        SELECT nombre, fecha_nacimiento, correo, foto, foto_tipo
        FROM formularios
        ORDER BY id DESC
        """
    )
    registros = cursor.fetchall()
    conn.close()

    return render_template(
        "validacion.html",
        mensaje=mensaje,
        registros=registros,
        breadcrumb=[
            {"label": "Inicio", "url": url_for("main.welcome")},
            {"label": "Formulario", "url": url_for("main.validacion")},
        ],
    )


@main_routes.route("/eliminar_formulario/<int:id>", methods=["POST"])
def eliminar_formulario(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM formularios WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("🗑️ Formulario eliminado.", "success")
    return redirect(url_for("main.validacion"))


# -----------------------------
# ERRORES
# -----------------------------
@main_routes.route("/error")
def error_page():
    return render_template(
        "error.html",
        error="Página de errores",
        breadcrumb=[
            {"label": "Inicio", "url": url_for("main.welcome")},
            {"label": "Errores", "url": url_for("main.error_page")},
        ],
    )


@main_routes.app_errorhandler(404)
def error_404(e):
    return render_template("error.html", error="404 - Página no encontrada"), 404


@main_routes.app_errorhandler(500)
def error_500(e):
    return render_template("error.html", error="500 - Error interno del servidor"), 500

# ============================================================
# ✅ CRUD DE USUARIOS (PÁGINA)
# ============================================================
@main_routes.route("/usuarios")
def usuarios():
    breadcrumb = [
        {"label": "Bienvenida", "url": url_for("main.welcome")},
        {"label": "Home", "url": url_for("main.home")},
        {"label": "Usuarios", "url": url_for("main.usuarios")},
    ]

    # (Opcional) para llenar el select de departamentos en el template
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT departamento FROM usuarios WHERE departamento IS NOT NULL AND TRIM(departamento) != '' ORDER BY departamento")
    departamentos_db = [r[0] for r in cursor.fetchall()]
    conn.close()

    return render_template(
        "usuarios.html",
        breadcrumb=breadcrumb,
        q=request.args.get("q", "").strip(),
        departamento=request.args.get("departamento", "").strip(),
        departamentos_db=departamentos_db,
    )


# ============================================================
# ✅ API USUARIOS (FETCH): LISTAR (q + departamento)
# ============================================================
@main_routes.route("/api/usuarios", methods=["GET"])
def api_usuarios_listar():
    conn = get_db()
    cursor = conn.cursor()

    q = request.args.get("q", "").strip()
    departamento = request.args.get("departamento", "").strip()

    where = []
    params = []

    if q:
        # búsqueda por nombre o email (y si tú guardas nombre completo, funciona perfecto)
        where.append("(nombre LIKE ? OR email LIKE ?)")
        params.extend([f"%{q}%", f"%{q}%"])

    if departamento:
        where.append("departamento = ?")
        params.append(departamento)

    where_sql = (" WHERE " + " AND ".join(where)) if where else ""

    cursor.execute(
        f"""
        SELECT id, nombre, email, departamento, fecha_nacimiento
        FROM usuarios
        {where_sql}
        ORDER BY id DESC
        """,
        params,
    )
    rows = cursor.fetchall()
    conn.close()

    items = [
        {
            "id": r[0],
            "nombre": r[1],
            "email": r[2],
            "departamento": r[3] or "Sin asignar",
            "fecha_nacimiento": r[4],
        }
        for r in rows
    ]

    return jsonify({"ok": True, "items": items})


# ============================================================
# ✅ API USUARIOS (FETCH): CREAR
# ============================================================
@main_routes.route("/api/usuarios", methods=["POST"])
def api_usuarios_crear():
    body = request.get_json(silent=True) or {}

    nombre = (body.get("nombre") or "").strip()
    email = (body.get("email") or "").strip().lower()
    departamento = (body.get("departamento") or "").strip() or "Sin asignar"
    fecha_nacimiento = (body.get("fecha_nacimiento") or "").strip()

    if not nombre or not email or not fecha_nacimiento:
        return jsonify({"ok": False, "error": "Nombre, email y fecha de nacimiento son obligatorios."}), 400

    if not re.match(REGEX_CORREO, email):
        return jsonify({"ok": False, "error": "Email inválido."}), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO usuarios (nombre, email, departamento, fecha_nacimiento)
            VALUES (?, ?, ?, ?)
            """,
            (nombre, email, departamento, fecha_nacimiento),
        )
        conn.commit()
        new_id = cursor.lastrowid

    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"ok": False, "error": "Ese email ya existe."}), 400

    conn.close()
    return jsonify({"ok": True, "id": new_id})


# ============================================================
# ✅ API USUARIOS (FETCH): ELIMINAR
# ============================================================
@main_routes.route("/api/usuarios/<int:id>", methods=["DELETE"])
def api_usuarios_eliminar(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


# ============================================================
# ✅ (OPCIONAL) RUTA PARA EDITAR EN PÁGINA /usuarios/editar/<id>
#     (porque tu template tiene link a /usuarios/editar/<id>)
# ============================================================
@main_routes.route("/usuarios/editar/<int:id>", methods=["GET", "POST"])
def usuarios_editar(id):
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip().lower()
        departamento = (request.form.get("departamento", "") or "").strip() or "Sin asignar"
        fecha_nacimiento = request.form.get("fecha_nacimiento", "").strip()

        if not nombre or not email or not fecha_nacimiento:
            conn.close()
            flash("❌ Nombre, email y fecha de nacimiento son obligatorios.", "danger")
            return redirect(url_for("main.usuarios_editar", id=id))

        if not re.match(REGEX_CORREO, email):
            conn.close()
            flash("❌ Email inválido.", "danger")
            return redirect(url_for("main.usuarios_editar", id=id))

        try:
            cursor.execute(
                """
                UPDATE usuarios
                SET nombre=?, email=?, departamento=?, fecha_nacimiento=?
                WHERE id=?
                """,
                (nombre, email, departamento, fecha_nacimiento, id),
            )
            conn.commit()
            conn.close()
            flash("✅ Usuario actualizado.", "success")
            return redirect(url_for("main.usuarios"))

        except sqlite3.IntegrityError:
            conn.close()
            flash("❌ Ese email ya existe.", "danger")
            return redirect(url_for("main.usuarios_editar", id=id))

    # GET
    cursor.execute(
        "SELECT id, nombre, email, departamento, fecha_nacimiento FROM usuarios WHERE id=?",
        (id,),
    )
    u = cursor.fetchone()
    conn.close()

    if not u:
        return render_template("error.html", error="Usuario no encontrado"), 404

    usuario = {
        "id": u[0],
        "nombre": u[1],
        "email": u[2],
        "departamento": u[3] or "Sin asignar",
        "fecha_nacimiento": u[4],
    }

    breadcrumb = [
        {"label": "Bienvenida", "url": url_for("main.welcome")},
        {"label": "Home", "url": url_for("main.home")},
        {"label": "Usuarios", "url": url_for("main.usuarios")},
        {"label": "Editar", "url": url_for("main.usuarios_editar", id=id)},
    ]

    return render_template("usuarios_editar.html", usuario=usuario, breadcrumb=breadcrumb)

@main_routes.route("/usuarios/eliminar/<int:id>", methods=["POST"])
def usuarios_eliminar_form(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("🗑️ Usuario eliminado.", "success")
    return redirect(url_for("main.usuarios"))