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
from werkzeug.utils import secure_filename

# ✅ IMPORTA get_db DESDE __init__.py
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
# BIENVENIDA Y HOME
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
        if r.json().get("success"):
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO registros (nombre, mensaje) VALUES (?, ?)", ("Prueba", "Desarrollo Web"))
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
            {"label": "Home", "url": url_for("main.home")}
        ],
    )

@main_routes.route("/upload_slide", methods=["POST"])
def upload_slide():
    if 'slide' not in request.files:
        flash("No se seleccionó ningún archivo", "danger")
        return redirect(url_for('main.home'))
    
    file = request.files['slide']
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        upload_path = os.path.join(current_app.root_path, 'static', 'uploads')
        
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
            
        file.save(os.path.join(upload_path, filename))
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO carousel_images (filename) VALUES (?)", (filename,))
        conn.commit()
        conn.close()
        flash("Imagen añadida al carrusel ✅", "success")
        
    return redirect(url_for('main.home'))

@main_routes.route("/eliminar_registro/<int:id>", methods=["POST"])
def eliminar_registro(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM registros WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Registro eliminado con éxito", "info")
    return redirect(url_for('main.home'))

# -----------------------------
# CALCULADORA / FORMULARIO
# -----------------------------

@main_routes.route("/operaciones", methods=["GET", "POST"])
def operaciones():
    suma, division = None, None
    if request.method == "POST":
        op = request.form.get("op")
        if op == "sumar":
            a, b = request.form.get("a", ""), request.form.get("b", "")
            if re.match(REGEX_NUMERO, a) and re.match(REGEX_NUMERO, b):
                suma = int(a) + int(b)
        elif op == "dividir":
            c, d = request.form.get("c", ""), request.form.get("d", "")
            if re.match(REGEX_NUMERO, c) and re.match(REGEX_NUMERO, d) and int(d) != 0:
                division = int(c) / int(d)
                
    return render_template(
        "operaciones.html",
        suma=suma, division=division,
        breadcrumb=[{"label": "Inicio", "url": url_for("main.welcome")}, {"label": "Calculadora", "url": url_for("main.operaciones")}]
    )

@main_routes.route("/validacion", methods=["GET", "POST"])
def validacion():
    mensaje = None
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        correo = request.form.get("correo", "").strip()
        foto = request.files.get("foto")
        
        if re.match(REGEX_NOMBRE, nombre) and re.match(REGEX_CORREO, correo) and foto:
            foto_bytes = foto.read()
            foto_base64 = base64.b64encode(foto_bytes).decode("utf-8")
            cursor.execute("""
                INSERT INTO formularios (nombre, fecha_nacimiento, sexo, telefono, correo, direccion, observaciones, foto, foto_tipo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (nombre, request.form.get("fecha_nacimiento"), request.form.get("sexo"), 
                  request.form.get("telefono"), correo, request.form.get("direccion"), 
                  request.form.get("observaciones"), foto_base64, foto.mimetype))
            conn.commit()
            mensaje = "✅ Registro guardado"

    cursor.execute("SELECT id, nombre, correo, foto, foto_tipo FROM formularios ORDER BY id DESC")
    registros = cursor.fetchall()
    conn.close()
    return render_template("validacion.html", mensaje=mensaje, registros=registros, 
                           breadcrumb=[{"label": "Inicio", "url": url_for("main.welcome")}, {"label": "Formulario", "url": url_for("main.validacion")}])

# -----------------------------
# CRUD USUARIOS (VISTAS Y API)
# -----------------------------

@main_routes.route("/usuarios")
def usuarios():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT departamento FROM usuarios WHERE departamento != '' AND departamento IS NOT NULL ORDER BY departamento")
    depts = [r[0] for r in cursor.fetchall()]
    conn.close()
    return render_template("usuarios.html", departamentos_db=depts, 
                           breadcrumb=[{"label": "Inicio", "url": url_for("main.welcome")}, {"label": "Usuarios", "url": url_for("main.usuarios")}])

@main_routes.route("/usuarios/editar/<int:id>", methods=["GET", "POST"])
def usuarios_editar(id):
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == "POST":
        try:
            nombre = request.form.get("nombre")
            email = request.form.get("email")
            depto = request.form.get("departamento")
            fecha = request.form.get("fecha_nacimiento")
            
            cursor.execute("""
                UPDATE usuarios 
                SET nombre = ?, email = ?, departamento = ?, fecha_nacimiento = ? 
                WHERE id = ?
            """, (nombre, email, depto, fecha, id))
            conn.commit()
            flash("Usuario actualizado con éxito ✅", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Error al actualizar: {str(e)} ❌", "danger")
        finally:
            conn.close()
        return redirect(url_for("main.usuarios"))

    cursor.execute("SELECT id, nombre, email, departamento, fecha_nacimiento FROM usuarios WHERE id = ?", (id,))
    usuario = cursor.fetchone()
    conn.close()
    
    if not usuario:
        flash("Usuario no encontrado 🔍", "danger")
        return redirect(url_for("main.usuarios"))
        
    return render_template("usuarios_editar.html", usuario=usuario)

@main_routes.route("/api/usuarios", methods=["GET"])
def api_usuarios_listar():
    page = request.args.get("page", 1, type=int)
    q = request.args.get("q", "").strip()
    departamento = request.args.get("departamento", "").strip()
    fecha_inicio = request.args.get("fecha_inicio", "").strip()
    fecha_fin = request.args.get("fecha_fin", "").strip()
    
    limit = 5
    offset = (page - 1) * limit
    
    conn = get_db()
    cursor = conn.cursor()
    
    base_query = "FROM usuarios WHERE 1=1"
    sql_params = []
    
    if q:
        base_query += " AND (nombre LIKE ? OR email LIKE ?)"
        sql_params.extend([f"%{q}%", f"%{q}%"])
        
    if departamento:
        if departamento == "Sin asignar":
            base_query += " AND (departamento IS NULL OR departamento = '' OR departamento = 'Sin asignar')"
        else:
            base_query += " AND departamento = ?"
            sql_params.append(departamento)
            
    if fecha_inicio:
        base_query += " AND fecha_nacimiento >= ?"
        sql_params.append(fecha_inicio)
        
    if fecha_fin:
        base_query += " AND fecha_nacimiento <= ?"
        sql_params.append(fecha_fin)

    cursor.execute(f"SELECT COUNT(*) {base_query}", sql_params)
    total = cursor.fetchone()[0]
    
    cursor.execute(f"SELECT id, nombre, email, departamento, fecha_nacimiento {base_query} ORDER BY id DESC LIMIT ? OFFSET ?", 
                   (*sql_params, limit, offset))
    
    rows = cursor.fetchall()
    conn.close()
    
    items = [{"id": r[0], "nombre": r[1], "email": r[2], "departamento": r[3], "fecha_nacimiento": r[4]} for r in rows]
    
    return jsonify({
        "ok": True, 
        "items": items, 
        "total_pages": (total + limit - 1) // limit if total > 0 else 1, 
        "page": page,
        "total_items": total
    })

@main_routes.route("/api/usuarios", methods=["POST"])
def api_usuarios_crear():
    try:
        data = request.get_json()
        if not data or not data.get('nombre') or not data.get('email'):
            return jsonify({"ok": False, "error": "Datos insuficientes"}), 400

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO usuarios (nombre, email, departamento, fecha_nacimiento) 
            VALUES (?, ?, ?, ?)
        """, (
            data['nombre'], 
            data['email'], 
            data.get('departamento', 'Sin asignar'), 
            data.get('fecha_nacimiento')
        ))
        conn.commit()
        conn.close()
        return jsonify({"ok": True}), 201
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@main_routes.route("/api/usuarios/<int:id>", methods=["DELETE"])
def api_usuarios_eliminar(id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# -----------------------------
# ERRORES
# -----------------------------

@main_routes.route("/error")
def error_page():
    return render_template("error.html", error="Página de errores", breadcrumb=[{"label": "Errores", "url": ""}])

@main_routes.app_errorhandler(404)
def error_404(e):
    return render_template("error.html", error="404 - No encontrado"), 404