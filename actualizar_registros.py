import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Ver columnas actuales
cursor.execute("PRAGMA table_info(registros)")
columnas = [col[1] for col in cursor.fetchall()]

def agregar_columna(nombre, tipo, default=None):
    if nombre not in columnas:
        if default is not None:
            cursor.execute(f"ALTER TABLE registros ADD COLUMN {nombre} {tipo} DEFAULT {default}")
        else:
            cursor.execute(f"ALTER TABLE registros ADD COLUMN {nombre} {tipo}")
        print(f"✅ Columna {nombre} agregada.")
    else:
        print(f"✔ La columna {nombre} ya existe.")

# Nuevas columnas
agregar_columna("categoria", "TEXT")
agregar_columna("precio", "REAL", 0)
agregar_columna("stock", "INTEGER", 0)
agregar_columna("estado", "TEXT", "'activo'")
agregar_columna("created_at", "TEXT")

conn.commit()
conn.close()

print("🎯 Base de datos actualizada correctamente.")
