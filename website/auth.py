from flask import Blueprint, render_template, request, flash
import bcrypt


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

        return render_template("sign-up.html")


@auth.route("/login")
def login():
    return render_template("login.html")


@auth.route("/logout")
def logout():
    return render_template("index.html")
