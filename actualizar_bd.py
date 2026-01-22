import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Ver columnas actuales
cursor.execute("PRAGMA table_info(formularios)")
cols = [c[1] for c in cursor.fetchall()]

if "foto_tipo" not in cols:
    cursor.execute("ALTER TABLE formularios ADD COLUMN foto_tipo TEXT")
    conn.commit()
    print("✅ Columna foto_tipo agregada.")
else:
    print("✅ La columna foto_tipo ya existe.")

conn.close()
