import sqlite3
import os

DB_PATH = "database.db"  # ajusta si tu path es distinto

def col_exists(cursor, table, col):
    cursor.execute(f"PRAGMA table_info({table})")
    return col in [r[1] for r in cursor.fetchall()]

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# nuevas columnas para filtros “tipo tienda”
cols_to_add = [
    ("categoria", "TEXT"),
    ("precio", "REAL"),
    ("stock", "INTEGER"),
    ("estado", "TEXT"),        # activo / inactivo
    ("created_at", "TEXT"),    # ISO: YYYY-MM-DD
]

for col, typ in cols_to_add:
    if not col_exists(cur, "registros", col):
        cur.execute(f"ALTER TABLE registros ADD COLUMN {col} {typ}")
        print(f"✅ Agregada columna: {col}")
    else:
        print(f"✅ Ya existe: {col}")

conn.commit()
conn.close()
print("✅ Migración terminada")
