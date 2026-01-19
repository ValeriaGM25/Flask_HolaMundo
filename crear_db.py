import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Crear tabla si no existe
cursor.execute("""
CREATE TABLE IF NOT EXISTS registros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    mensaje TEXT
)
""")

# (Opcional) Insertar un registro de prueba
cursor.execute("""
INSERT INTO registros (nombre, mensaje)
VALUES (?, ?)
""", ("Prueba", "Desarrollo Web"))

conn.commit()
conn.close()

print("Base de datos y tabla 'registros' creadas correctamente")
