from flask import Flask
from app.routes import main_routes

app = Flask(__name__)
app.config["SECRET_KEY"] = "6LehvUQsAAAAANusKcHRfF0w5DkX0L1JYl8Ae28Q"

app.register_blueprint(main_routes)

if __name__ == "__main__":
    app.run(debug=True)
