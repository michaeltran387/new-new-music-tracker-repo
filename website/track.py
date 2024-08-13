from flask import Blueprint, render_template, redirect, url_for, request
import requests
from .models import *
from flask_login import login_required, current_user

track_blueprint = Blueprint("track", __name__)


class SearchResult:
    def __init__(self, name, picture, link, id):
        self.name = name
        self.picture = picture
        self.link = link
        self.id = id


@track_blueprint.route("/track", methods=["GET", "POST"])
@login_required
def track():
    if request.method == "GET":
        return render_template("track.html")
    if request.method == "POST":
        if "search" in request.form:

            print(request.form)

            search = request.form.get("search")

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

            access_token = r.json()["access_token"]
            headers = {"Authorization": "Bearer " + access_token}
            type = ["artist"]
            # print(type)

            payload = {"q": search, "type": type}

            r = requests.get(
                "https://api.spotify.com/v1/search", params=payload, headers=headers
            )

            # print(r.json())
            # print(r.json()["artists"]["items"][0]["name"])
            # print(r.json()["artists"]["items"][0]["images"][0]["url"])
            # print(r.json()["artists"]["items"][0]["external_urls"]["spotify"])

            searchResultList = []

            for i in range(5):
                searchResultList.append(
                    SearchResult(
                        r.json()["artists"]["items"][i]["name"],
                        r.json()["artists"]["items"][i]["images"][0]["url"],
                        r.json()["artists"]["items"][i]["external_urls"]["spotify"],
                        r.json()["artists"]["items"][i]["id"],
                    )
                )

            # print(searchResultList[1].name)

            # searchResult1 = SearchResult(
            #     r.json()["artists"]["items"][0]["name"],
            #     r.json()["artists"]["items"][0]["images"][0]["url"],
            #     r.json()["artists"]["items"][0]["external_urls"]["spotify"],
            # )

            # r = requests.get(
            #     "https://api.spotify.com/v1/artists/2hGh5VOeeqimQFxqXvfCUf?si=GbHu7fEJSP6OvAXiU9ki4Q",
            #     headers={"Authorization": "Bearer " + access_token},
            # )

            # print(r.text)
            return render_template("track.html", searchResultList=searchResultList)
        else:
            print(request.form.keys())
            print(list(request.form.keys()))
            print(list(request.form.keys())[0])

            addedArtistsID = list(request.form.keys())[0]

            userArtists = db.session.execute(
                db.select(AddedArtists.artist_spotify_id).where(
                    AddedArtists.user_id == current_user.id
                )
            ).scalars()

            if addedArtistsID in userArtists.all():
                print("You are already tracking this artist.")

            addArtist = AddedArtists(
                user_id=current_user.id, artist_spotify_id=list(request.form.keys())[0]
            )
            db.session.add(addArtist)
            db.session.commit()

            userArtists = db.session.execute(
                db.select(AddedArtists.artist_spotify_id).where(
                    AddedArtists.user_id == current_user.id
                )
            ).scalars()
            print(userArtists.all())

        return render_template("track.html")
