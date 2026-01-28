import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# -----------------------------
# ACTUALIZAR TABLA formularios
# -----------------------------
cursor.execute("PRAGMA table_info(formularios)")
cols = [c[1] for c in cursor.fetchall()]

if "foto_tipo" not in cols:
    cursor.execute("ALTER TABLE formularios ADD COLUMN foto_tipo TEXT")
    print("✅ Columna foto_tipo agregada.")
else:
    print("✅ La columna foto_tipo ya existe.")

# -----------------------------
# CREAR TABLA carousel_images
# -----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS carousel_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")
print("✅ Tabla carousel_images verificada/creada.")

conn.commit()
conn.close()

print("🎉 Base de datos actualizada correctamente.")
