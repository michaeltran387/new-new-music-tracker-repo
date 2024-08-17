from flask import Blueprint, render_template, redirect, url_for, request, flash
import requests
from .models import *
from flask_login import login_required, current_user

track_blueprint = Blueprint("track", __name__)


class SearchResultTrack:
    def __init__(self, name, picture, link, id):
        self.name = name
        self.picture = picture
        self.link = link
        self.id = id


class NewMusic:
    def __init__(self, artistName, albumName, picture, date, type, flag, albumID):
        self.artistName = artistName
        self.albumName = albumName
        self.picture = picture
        self.date = date
        self.type = type
        self.flag = flag
        self.albumID = albumID


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


@track_blueprint.route("/track", methods=["GET", "POST"])
@login_required
def track():
    if request.method == "GET":
        return render_template("track.html")
    if request.method == "POST":
        if "search" in request.form:

            # print(request.form)

            search = request.form.get("search")
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

            global searchResultList
            searchResultList = []

            for i in range(5):
                searchResultList.append(
                    SearchResultTrack(
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
            # print(request.form.keys())
            # print(list(request.form.keys()))
            # print(list(request.form.keys())[0])

            # print(searchResultList[0].name)

            addedArtistsID = list(request.form.keys())[0]

            userArtists = db.session.execute(
                db.select(AddedArtists.artist_id).where(
                    AddedArtists.user_id == current_user.id
                )
            ).scalars()

            if addedArtistsID in userArtists.all():
                flash("You are already tracking this artist.", category="success")
                return render_template("track.html", searchResultList=searchResultList)

            addArtist = AddedArtists(
                user_id=current_user.id, artist_id=list(request.form.keys())[0]
            )
            db.session.add(addArtist)
            db.session.commit()
            flash("Artist has been successfully added.", category="success")

            userArtists = db.session.execute(
                db.select(AddedArtists.artist_id).where(
                    AddedArtists.user_id == current_user.id
                )
            ).scalars()
            print(userArtists.all())

        return render_template("track.html", searchResultList=searchResultList)


@track_blueprint.route("/newmusic", methods=["GET", "POST"])
@login_required
def newmusic():
    # try:
    if request.method == "GET":
        trackedArtists = db.session.execute(
            db.select(AddedArtists.artist_id).where(
                AddedArtists.user_id == current_user.id
            )
        ).scalars()
        # print(trackedArtists.all()[0])
        # print(type(trackedArtists.all()))
        # test = trackedArtists.all()
        # # print(trackedArtists.all()[0])
        # print(test)

        trackedArtistsList = trackedArtists.all()[0]
        if not trackedArtistsList:
            return render_template("newmusic.html")

        artistID = trackedArtistsList
        # except:
        #     flash("Please track ")
        print(artistID)
        endpoint = "https://api.spotify.com/v1/artists/" + artistID
        r = requests.get(endpoint, headers=headers)
        # print(r.json()["name"])
        artistName = r.json()["name"]
        # print(r.json()["name"])

        endpoint = "https://api.spotify.com/v1/artists/" + artistID + "/albums"

        r = requests.get(endpoint, headers=headers)
        # print(r.json())

        # class NewMusic:
        #     def __init__(self, artistName, albumName, picture, date, type, flag, albumID):
        #         self.artistName = artistName
        #         self.albumName = albumName
        #         self.picture = picture
        #         self.date = date
        #         self.type = type
        #         self.flag = flag
        #         self.albumID = albumID

        newMusicList = []

        for i in range(20):
            newMusicList.append(
                NewMusic(
                    artistName,
                    r.json()["items"][i]["name"],
                    r.json()["items"][i]["images"][0]["url"],
                    r.json()["items"][i]["release_date"],
                    r.json()["items"][i]["album_type"],
                    False,
                    r.json()["items"][i]["id"],
                )
            )
        # print(newMusicList[0].flag)

        return render_template("newmusic.html", newMusicList=newMusicList)
    if request.method == "POST":

        print(list(request.form.keys()))
        return render_template("newmusic.html")


@track_blueprint.route("track-artists", methods=["GET"])
@login_required
def trackArtists():

    # r = requests.post(
    #     "https://accounts.spotify.com/api/token",
    #     headers={
    #         "Content-Type": "application/x-www-form-urlencoded",
    #     },
    #     data={
    #         "grant_type": "client_credentials",
    #         "client_id": "b2817ab1a6a6471dae92088510ed25f1",
    #         "client_secret": "d4fad7b2dbac4eca9c558e39c584a6d0",
    #     },
    # )
    # print(r.json())

    # access_token = r.json()["access_token"]
    # headers = {"Authorization": "Bearer " + access_token}

    # r = requests.get("https://api.spotify.com/v1/me/playlists", headers=headers)
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
    print(r)

    # access_token = r.json()["access_token"]
    # headers = {"Authorization": "Bearer " + access_token}

    # r = requests.get("https://api.spotify.com/v1/me/playlists", headers=headers)
    # print(r.json())

    return render_template("track-artists.html")


@track_blueprint.route("/test", methods=["GET"])
def test():
    return render_template("test.html")
