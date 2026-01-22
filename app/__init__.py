from flask import Flask
import sqlite3

def get_db():
    return sqlite3.connect("database.db")

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

    conn.commit()
    conn.close()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "clave-secreta"

    init_db()

    from .routes import main_routes
    app.register_blueprint(main_routes)

    return app
