import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO registros (nombre, mensaje)
    VALUES (?, ?)
""", ("Prueba", "Desarrolloweb"))


conn.commit()
conn.close()

print("Base de datos creada")
