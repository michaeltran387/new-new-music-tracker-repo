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
import requests


auth = Blueprint("auth", __name__)


@auth.route("sign-up", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
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
            flash("Account has been successfully created.", category="success")
            flash("Please log in to continue.", category="success")
            return redirect(url_for("auth.login"))
        else:
            flash("Username already exists.", category="error")
            return render_template("sign-up.html")

        return render_template("login.html")


@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = db.session.execute(
            db.select(User).filter_by(username=username)
        ).scalar_one_or_none()

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

            return redirect(url_for("views.home"))


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/delete-account", methods=["GET", "POST"])
@login_required
def deleteAccount():
    if request.method == "GET":
        return render_template("delete-account.html")
    if request.method == "POST":
        id = current_user.get_id()

        user_added_artists = (
            db.session.execute(db.select(AddedArtists).filter_by(user_id=id))
            .scalars()
            .all()
        )
        if user_added_artists:
            for artist in user_added_artists:
                db.session.delete(artist)

        user_tags = (
            db.session.execute(db.select(UserTags).filter_by(user_id=id))
            .scalars()
            .all()
        )
        if user_tags:
            for tag in user_tags:
                db.session.delete(tag)

        access_token = (
            db.session.execute(db.select(AccessToken).filter_by(user_id=id))
            .scalars()
            .all()
        )
        if access_token:
            db.session.delete(access_token[0])

        user = db.session.execute(db.select(User).filter_by(id=id)).scalars().all()[0]
        db.session.delete(user)
        db.session.commit()
        logout_user()

        return redirect("/")
