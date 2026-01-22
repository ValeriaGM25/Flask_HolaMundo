import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# ==============================
# Tabla para index (reCAPTCHA)
# ==============================
cursor.execute("""
CREATE TABLE IF NOT EXISTS registros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    mensaje TEXT NOT NULL
)
""")

# ==============================
# Tabla formulario profesional
# ==============================
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
    foto BLOB NOT NULL
)
""")

conn.commit()
conn.close()

print("Base de datos creada / actualizada correctamente")
