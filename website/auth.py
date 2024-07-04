from flask import Blueprint, render_template, request, flash
import bcrypt
import sqlite3

con = sqlite3.connect("new-new-music-tracker.db", check_same_thread=False)
cur = con.cursor()


auth = Blueprint("auth", __name__)


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

        # sqlstatement = "SELECT EXISTS(SELECT 1 from users WHERE username={username})".format(username=username)

        password = b"super super secret password"
        hashedpw = bcrypt.hashpw(password, bcrypt.gensalt())
        check = "INSERT INTO users (username, password) VALUES ('{username}', '{password}')".format(
            username=username, password="hashedpw"
        )
        print(check)
        # print(hashedpw[])
        cur.execute(check)
        con.commit()
        res = cur.execute("SELECT username FROM users")
        res.fetchall()
        print(res.fetchall())

        return render_template("sign-up.html")


@auth.route("/login")
def login():
    return render_template("login.html")


@auth.route("/logout")
def logout():
    return render_template("index.html")
