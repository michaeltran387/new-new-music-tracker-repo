from flask import Flask
import sqlite3
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from .models import *


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "supersecretkey"

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-new-music-tracker.db"
    db.init_app(app)
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        user = db.session.execute(db.select(User).filter_by(id=id)).scalar_one_or_none()
        if (
            db.session.execute(db.select(User).filter_by(id=id)).scalar_one_or_none()
            == None
        ):
            return None
        else:
            return user

    # con = sqlite3.connect("new-new-music-tracker.db")
    # cur = con.cursor()
    # res = cur.execute(
    #     "SELECT name FROM sqlite_master WHERE type='table' AND name = 'users'"
    # )
    # if len(res.fetchall()) == 0:
    #     cur.execute("CREATE TABLE users(username, password)")
    # res = cur.execute("SELECT name from sqlite_master")
    # print(res.fetchone())
    # con.close()

    return app
