from flask import Flask, render_template, request
import sqlite3
import requests

app = Flask(__name__)

SITE_KEY = "6LehvUQsAAAAAGldvO1QR8Da4yc3upv2yP3sgmgR"
SECRET_KEY = "6LehvUQsAAAAANusKcHRfF0w5DkX0L1JYl8Ae28Q"

def get_db():
    return sqlite3.connect("database.db")

@app.route("/", methods=["GET", "POST"])
def index():
    mensaje = ""

    if request.method == "POST":
        recaptcha_response = request.form.get("g-recaptcha-response")

        data = {
            "secret": SECRET_KEY,
            "response": recaptcha_response
        }

        r = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data=data
        )

        result = r.json()

        if result["success"]:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO registros (nombre, mensaje)
                VALUES (?, ?)
            """, ("Prueba", "Desarrollo Web"))
            conn.commit()
            conn.close()

            mensaje = "Datos guardados correctamente ✅"
        else:
            mensaje = "reCAPTCHA inválido ❌"

    # Obtener registros
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, mensaje FROM registros")
    registros = cursor.fetchall()
    conn.close()

    return render_template(
        "index.html",
        site_key=SITE_KEY,
        mensaje=mensaje,
        registros=registros
    )

@app.route("/bienvenida")
def bienvenida():
    return render_template("bienvenida.html")

# -----------------------------
# CALCULADORA (SIN VALIDACIÓN)
# -----------------------------
@app.route("/operaciones", methods=["GET", "POST"])
def operaciones():
    suma = None
    division = None

    if request.method == "POST":
        a = request.form.get("a")
        b = request.form.get("b")
        c = request.form.get("c")
        d = request.form.get("d")

        # SIN validación a propósito
        suma = int(a) + int(b)
        division = int(c) / int(d)

    return render_template(
        "operaciones.html",
        suma=suma,
        division=division
    )


# -----------------------------
# FORMULARIO CON VALIDACIÓN
# -----------------------------
@app.route("/validacion", methods=["GET", "POST"])
def validacion():
    mensaje = ""

    if request.method == "POST":
        nombre = request.form.get("nombre")
        edad = request.form.get("edad")
        correo = request.form.get("correo")
        correo2 = request.form.get("correo2")

        if not nombre or not edad or not correo or not correo2:
            mensaje = "Todos los campos son obligatorios"
        elif not edad.isdigit():
            mensaje = "La edad debe ser numérica"
        elif correo != correo2:
            mensaje = "Los correos no coinciden"
        else:
            mensaje = "Formulario validado correctamente ✅"

    return render_template("validacion.html", mensaje=mensaje)


# -----------------------------
# PÁGINA DE ERRORES (MANUAL)
# -----------------------------
@app.route("/error")
def error():
    return render_template("error.html", error="Página de errores")


# -----------------------------
# MANEJO DE ERRORES
# -----------------------------
@app.errorhandler(404)
def error_404(e):
    return render_template("error.html", error="404 - Página no encontrada"), 404


@app.errorhandler(500)
def error_500(e):
    return render_template("error.html", error="500 - Error interno del servidor"), 500


if __name__ == "__main__":
    app.run(debug=True)
