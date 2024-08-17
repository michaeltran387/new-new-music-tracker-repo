from flask import Blueprint, render_template
from flask_login import login_remembered, current_user
from .models import *
import requests
import base64

# from .models import *

views = Blueprint("views", __name__)


@views.route("/")
def home():
    if current_user.is_authenticated:
        r = requests.get(
            "https://accounts.spotify.com/authorize",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            params={
                "client_id": "b2817ab1a6a6471dae92088510ed25f1",
                "response_type": "code",
                "redirect_uri": "http://127.0.0.1:5000/",
            },
        )
        # print(r)
        code = r
        # client_id = "b2817ab1a6a6471dae92088510ed25f1"
        # client_secret = "d4fad7b2dbac4eca9c558e39c584a6d0"
        # b64client_id = base64.b64encode(b"b2817ab1a6a6471dae92088510ed25f1")
        # b64client_secret = base64.b64encode(b"d4fad7b2dbac4eca9c558e39c584a6d0")

        # print(teststring)

        # r = requests.post(
        #     "https://accounts.spotify.com/api/token",
        #     headers={
        #         "Authorization": "Basic " + b64client_id + ":" + b64client_secret,
        #         "Content-Type": "application/x-www-form-urlencoded",
        #     },
        #     params={
        #         "grant_type": "authorization_code",
        #         "code": code,
        #         "redirect_uri": "http://127.0.0.1:5000/",
        #     },
        # )
        # print(r.json())

        # access_token = r.json()["access_token"]
        # headers = {"Authorization": "Bearer " + access_token}
    return render_template("index.html")
