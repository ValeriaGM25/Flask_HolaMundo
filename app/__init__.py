from flask import Flask
import sqlite3
import os

# Carpeta raíz del proyecto: /home/Valeria05/Flask_HolaMundo
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_PATH = os.path.join(BASE_DIR, "database.db")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS registros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        mensaje TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS formularios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        fecha_nacimiento TEXT NOT NULL,
        sexo TEXT NOT NULL,
        telefono TEXT NOT NULL,
        correo TEXT NOT NULL,
        direccion TEXT NOT NULL,
        observaciones TEXT,
        foto TEXT NOT NULL,
        foto_tipo TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS carousel_images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL
    )
    """)

    # ✅ TABLA PARA LA PÁGINA DE USUARIOS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        departamento TEXT DEFAULT 'Sin asignar',
        fecha_nacimiento TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

def create_app():
    app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
    app.config["SECRET_KEY"] = "6LehvUQsAAAAANusKcHRfF0w5DkX0L1JYl8Ae28Q"

    init_db()

    from .routes import main_routes
    app.register_blueprint(main_routes)

    return app