from flask import Blueprint, render_template, request, flash, redirect, url_for
import bcrypt
from .models import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from . import views

# from .__init__ import load_user

# import sqlite3


auth = Blueprint("auth", __name__)

# con = sqlite3.connect("new-new-music-tracker.db", check_same_thread=False)
# cur = con.cursor()


@auth.route("sign-up", methods=["GET", "POST"])
def signup():
    if request.method == "GET":

        # user = db.session.execute(db.select(User)).scalars()
        # print(user.fetchall()[0].password)
        # print(User.get(id))

        return render_template("sign-up.html")
    if request.method == "POST":
        username = request.form.get("username")
        displayname = request.form.get("displayname")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        if password1 != password2:
            flash("Passwords do not match.", category="error")
            return render_template("sign-up.html")

        if (
            db.session.execute(
                db.select(User).filter_by(username=username)
            ).scalar_one_or_none()
            == None
        ):
            hashedpw = generate_password_hash(password1, method="scrypt")
            user = User(username=username, displayname=displayname, password=hashedpw)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("auth.login"))
        else:
            flash("Username already exists.", category="error")
            return render_template("sign-up.html")

        # password = b"super super secret password"
        # hashedpw = bcrypt.hashpw(password, bcrypt.gensalt())
        # print(hashedpw)
        # print(*hashedpw)

        # print(hashedpw)
        # unhashedpw = check_password_hash(hashedpw, password1)
        # print(unhashedpw)

        # res = cur.execute("SELECT name from sqlite_master")
        # print(res.fetchone())

        # res = cur.execute("SELECT COUNT(*) FROM users")
        # if res.fetchone()[0] == 0:
        #     check = "INSERT INTO users VALUES ('{username}', '{password}')".format(
        #         username=username, password=password1
        #     )
        #     cur.execute(check)
        #     con.commit()
        #     return render_template("sign-up.html")

        # res = cur.execute(
        #     "SELECT username FROM users WHERE username='{username}'".format(
        #         username=username
        #     )
        # )
        # if len(res.fetchone()) != 0:
        #     flash("This username already exists.", category="error")
        #     return render_template("sign-up.html")

        # else:
        #     check = "INSERT INTO users VALUES ('{username}', '{password}')".format(
        #         username=username, password=password1
        #     )
        #     cur.execute(check)
        #     con.commit()
        #     # res = cur.execute("SELECT *, password FROM users")
        # print(res.fetchall())

        return render_template("login.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # res = cur.execute(
        #     "SELECT password FROM users WHERE username='{username}'".format(
        #         username=username
        #     )
        # )
        # print(password)
        # testpw = res.fetchone()[0]
        # print(testpw)

        user = db.session.execute(
            db.select(User).filter_by(username=username)
        ).scalar_one_or_none()
        # print(user)
        # print(type(user))
        # print(user.username)
        # print(user.password)
        # print(user.password[15:])
        # print(check_password_hash(user.password, password))
        if user == None:
            flash("Username does not exist.", category="error")
            return render_template("login.html")
        elif check_password_hash(user.password, password) == False:
            flash("Password is incorrect.", category="error")
            return render_template("login.html")
        else:
            flash("You have logged in successfully.", category="success")
            print(user.is_authenticated)
            print(current_user.is_authenticated)
            user.is_authenticated = True
            db.session.commit()
            print(user.is_authenticated)
            print(current_user.is_authenticated)
            login_user(user)
            # print(current_user)
            # print(current_user.id)
            # login_user(user)
            # print(type(user.get_id()))
            # user = db.session.execute(db.select(User).filter_by(id=id)).scalar_one()
            # print(user)
            # print(user.get_id())
            return redirect(url_for("views.home"))


@auth.route("/logout")
@login_required
def logout():
    print(current_user)
    print(current_user.get_id())
    print(current_user.is_authenticated)
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/delete")
@login_required
def deleteaccount():
    db.session.delete(user)
    db.session.commit()
    return render_template("index.html")
