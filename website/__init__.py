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
    from .track import track_blueprint

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(track_blueprint, url_prefix="/")

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-new-music-tracker.db"
    db.init_app(app)
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return db.session.execute(db.select(User).filter_by(id=id)).scalar_one_or_none()

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "error"

    return app
