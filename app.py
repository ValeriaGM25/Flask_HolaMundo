from flask import Flask

app = Flask(__name__)

@app.route("/")
def hola():
    return "Hola Mundo desde Flask en Hosting 🚀"

# ❌ NO pongas app.run()
