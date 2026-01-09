from flask import Flask, render_template, request
import sqlite3
import requests

app = Flask(__name__)

SITE_KEY = "6LehvUQsAAAAAGldvO1QR8Da4yc3upv2yP3sgmgR"
SECRET_KEY = "6LehvUQsAAAAANusKcHRfF0w5DkX0L1JYl8Ae28Q"

# Conexión a la BD
def get_db():
    return sqlite3.connect("database.db")

@app.route("/", methods=["GET", "POST"])
def index():
    mensaje = ""

    if request.method == "POST":
        recaptcha_response = request.form.get("g-recaptcha-response")

        if not recaptcha_response:
            mensaje = "Debes marcar el reCAPTCHA ❌"
        else:
            data = {
                "secret": SECRET_KEY,
                "response": recaptcha_response
            }

            r = requests.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data=data
            )

            result = r.json()

            if result.get("success"):
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO registros (nombre, mensaje)
                    VALUES (?, ?)
                """, ("Valeria", "Enviado"))
                conn.commit()
                conn.close()

                mensaje = "Datos guardados correctamente ✅"
            else:
                mensaje = "reCAPTCHA inválido ❌"

    return render_template("index.html", site_key=SITE_KEY, mensaje=mensaje)

if __name__ == "__main__":
    app.run(debug=True)
