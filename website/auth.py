from flask import Blueprint, render_template, request, flash
import bcrypt
import sqlite3

# from flask_login import LoginManager

auth = Blueprint("auth", __name__)

con = sqlite3.connect("new-new-music-tracker.db", check_same_thread=False)
cur = con.cursor()


@auth.route("sign-up", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("sign-up.html")
    if request.method == "POST":
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        if password1 != password2:
            flash("Passwords do not match.", category="error")
            return render_template("sign-up.html")

        # res = cur.execute("SELECT name from sqlite_master")
        # print(res.fetchone())

        res = cur.execute("SELECT COUNT(*) FROM users")
        if res.fetchone()[0] == 0:
            check = "INSERT INTO users VALUES ('{username}', '{password}')".format(
                username=username, password=password1
            )
            cur.execute(check)
            con.commit()
            return render_template("sign-up.html")

        res = cur.execute(
            "SELECT username FROM users WHERE username='{username}'".format(
                username=username
            )
        )
        if len(res.fetchone()) != 0:
            flash("This username already exists.", category="error")
            return render_template("sign-up.html")

        # password = b"super super secret password"
        # hashedpw = bcrypt.hashpw(password, bcrypt.gensalt())

        else:
            check = "INSERT INTO users VALUES ('{username}', '{password}')".format(
                username=username, password=password1
            )
            cur.execute(check)
            con.commit()
            # res = cur.execute("SELECT *, password FROM users")
            # print(res.fetchall())

            return render_template("sign-up.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        res = cur.execute(
            "SELECT password FROM users WHERE username='{username}'".format(
                username=username
            )
        )
        # print(password)
        # testpw = res.fetchone()[0]
        # print(testpw)
        if password != res.fetchone()[0]:
            flash("Password is incorrect.", category="error")
            return render_template("login.html")
        else:
            flash("You have logged in successfully.", category="success")
            return render_template("index.html")


@auth.route("/logout")
def logout():
    return render_template("index.html")
