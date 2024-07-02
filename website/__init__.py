from flask import Flask
import sqlite3


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "supersecretkey"

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    conn = sqlite3.connect("new-new-music-tracker.db")
    c = conn.cursor()
    check = c.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name = 'users'"
    )
    if len(*check) == 0:
        c.execute(
            """
        CREATE TABLE users (
        username text
        password text
                )"""
        )

    return app
