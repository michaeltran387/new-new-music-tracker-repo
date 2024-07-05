from flask import Flask
import sqlite3
from flask_login import LoginManager
from test import Test2


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
        cur.execute("CREATE TABLE users(username, password)")
    # res = cur.execute("SELECT name from sqlite_master")
    # print(res.fetchone())
    con.close()

    login_manager = LoginManager()
    login_manager.init_app(app)

    # @login_manager.user_loader
    # def load_user(id):
    #     return Test2.get(id)

    Test2.hello()

    return app
