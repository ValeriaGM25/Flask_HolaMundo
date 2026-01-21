import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Tabla para index (reCAPTCHA)
cursor.execute("""
CREATE TABLE IF NOT EXISTS registros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    mensaje TEXT NOT NULL
)
""")

# Tabla para formulario con foto
cursor.execute("""
CREATE TABLE IF NOT EXISTS formularios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    edad INTEGER NOT NULL,
    correo TEXT NOT NULL,
    foto BLOB NOT NULL
)
""")

conn.commit()
conn.close()

print("Base de datos creada/actualizada correctamente")
