from flask import Blueprint, render_template, redirect
from flask_login import login_remembered, current_user
from .models import *
import requests
import base64

# from .models import *

views = Blueprint("views", __name__)


@views.route("/")
def home():
    return render_template("index.html")


@views.route("/test", methods=["GET"])
def test():
    return "<a href='/test2'> Login with Spotify </a>"


@views.route("/test2", methods=["GET"])
def test2():
    params = {
        "client_id": "b2817ab1a6a6471dae92088510ed25f1",
        "response_type": "code",
        "redirect_uri": "http://127.0.0.1:5000/",
        "show_dialog": True,
    }

    authURL = "https://accounts.spotify.com/authorize"

    r = requests.get(authURL, params=params)
    print(r.url)
    return redirect(r.url)

    code = r

    client_id = "b2817ab1a6a6471dae92088510ed25f1"
    client_secret = "d4fad7b2dbac4eca9c558e39c584a6d0"
