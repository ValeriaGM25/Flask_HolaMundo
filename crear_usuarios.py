import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

cur.execute("""
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
print("✅ Tabla usuarios lista")