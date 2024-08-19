from flask import Blueprint, render_template, redirect
from flask_login import login_remembered, current_user
from .models import *
import requests
import base64

# from .models import *

views = Blueprint("views", __name__)


@views.route("/")
def home():
    # if current_user.is_authenticated:
    #     r = requests.get(
    #         "https://accounts.spotify.com/authorize",
    #         headers={
    #             "Content-Type": "application/x-www-form-urlencoded",
    #         },
    #         params={
    #             "client_id": "b2817ab1a6a6471dae92088510ed25f1",
    #             "response_type": "code",
    #             "redirect_uri": "http://127.0.0.1:5000/",
    #         },
    #     )

    #     print(r)

    # code = r

    # client_id = "b2817ab1a6a6471dae92088510ed25f1"
    # client_secret = "d4fad7b2dbac4eca9c558e39c584a6d0"
    # # b64client_id = base64.b64encode(b"b2817ab1a6a6471dae92088510ed25f1")
    # # b64client_secret = base64.b64encode(b"d4fad7b2dbac4eca9c558e39c584a6d0")
    # # b64client_id = b'b2817ab1a6a6471dae92088510ed25f1'
    # # b64client_secret = b'd4fad7b2dbac4eca9c558e39c584a6d0'
    # authorization = base64.urlsafe_b64encode(
    #     b"Basic: b2817ab1a6a6471dae92088510ed25f1:d4fad7b2dbac4eca9c558e39c584a6d0"
    # )
    # print(authorization)
    # test = "{}:{}".format(client_id, client_secret)
    # print(test)
    # # authorization = base64.urlsafe_b64encode(test)
    # # print(authorization)
    # authorization = base64.urlsafe_b64encode(test.encode()).decode()
    # print(authorization)

    # # print(teststring)

    # r = requests.post(
    #     "https://accounts.spotify.com/api/token",
    #     headers={
    #         "Authorization": authorization,
    #         "Content-Type": "application/x-www-form-urlencoded",
    #     },
    #     params={
    #         "grant_type": "authorization_code",
    #         "code": code,
    #         "redirect_uri": "http://127.0.0.1:5000/",
    #     },
    # )

    # r = requests.post(
    #     "https://accounts.spotify.com/api/token",
    #     headers={
    #         "Content-Type": "application/x-www-form-urlencoded",
    #     },
    #     params={
    #         "grant_type": "authorization_code",
    #         "code": code,
    #         "redirect_uri": "http://127.0.0.1:5000/",
    #         "client_id": client_id,
    #         "client_secret": client_secret,
    #     },
    # )

    # print(r.json())

    # access_token = r.json()["access_token"]
    # headers = {"Authorization": "Bearer " + access_token}
    return render_template("index.html")


@views.route("/test", methods=["GET"])
def test():
    return "<a href='/test2'> Login with Spotify </a>"


@views.route("/test2", methods=["GET"])
def test2():
    # headers = {
    #     "Content-Type": "application/x-www-form-urlencoded",
    # }
    params = {
        "client_id": "b2817ab1a6a6471dae92088510ed25f1",
        "response_type": "code",
        "redirect_uri": "http://127.0.0.1:5000/",
        # "scope": "user-read-private",
        "show_dialog": True,
    }

    # r = requests.get(
    #     "https://accounts.spotify.com/authorize",
    #     ,
    # )

    authURL = "https://accounts.spotify.com/authorize"

    r = requests.get(authURL, params=params)
    print(r.url)
    return redirect(r.url)

    # print(r)

    code = r

    client_id = "b2817ab1a6a6471dae92088510ed25f1"
    client_secret = "d4fad7b2dbac4eca9c558e39c584a6d0"
