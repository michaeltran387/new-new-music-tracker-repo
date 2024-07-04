from flask import Flask
import sqlite3


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "supersecretkey"

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    con = sqlite3.connect("new-new-music-tracker.db")
    cur = con.cursor()
    res = cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name = 'users'"
    )
    if len(res.fetchall()) == 0:
        cur.execute(
            """
        CREATE TABLE users (
        username text,
        password blob
                )"""
        )
    con.close()

    return app
