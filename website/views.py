from flask import Blueprint, render_template
from flask_login import login_remembered, current_user
from .models import *
import requests

# from .models import *

views = Blueprint("views", __name__)


@views.route("/")
def home():

    r = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "grant_type": "client_credentials",
            "client_id": "b2817ab1a6a6471dae92088510ed25f1",
            "client_secret": "d4fad7b2dbac4eca9c558e39c584a6d0",
        },
    )
    print(r.text)
    print(r.json()["access_token"])
    access_token = r.json()["access_token"]
    print(access_token)

    r = requests.get(
        "https://api.spotify.com/v1/artists/2hGh5VOeeqimQFxqXvfCUf?si=GbHu7fEJSP6OvAXiU9ki4Q",
        headers={"Authorization": "Bearer " + access_token},
    )

    print(r.text)
    return render_template("index.html")
