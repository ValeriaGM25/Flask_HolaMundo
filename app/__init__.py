from flask import Flask
import sqlite3
import os

# Carpeta raíz del proyecto (Flask_HolaMundo/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def get_db():
    return sqlite3.connect(DB_PATH)

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

    # ✅ NUEVO: tabla para imágenes del carrusel
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS carousel_images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "6LehvUQsAAAAANusKcHRfF0w5DkX0L1JYl8Ae28Q"

    # ✅ NUEVO: carpeta donde se guardan las imágenes subidas
    app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder, "uploads")

    init_db()

    from .routes import main_routes
    app.register_blueprint(main_routes)

    return app
