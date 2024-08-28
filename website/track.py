from flask import Blueprint, render_template, redirect, url_for, request, flash
import requests
from requests.auth import HTTPBasicAuth
from .models import *
from flask_login import login_required, current_user
import base64

track_blueprint = Blueprint("track", __name__)


class SearchResultTrack:
    def __init__(self, name, picture, link, id):
        self.name = name
        self.picture = picture
        self.link = link
        self.id = id


class NewMusic:
    def __init__(self, artistName, albumName, picture, date, type, flag, albumID, tag):
        self.artistName = artistName
        self.albumName = albumName
        self.picture = picture
        self.date = date
        self.type = type
        self.flag = flag
        self.albumID = albumID
        self.tag = tag


class UserPlaylists:
    def __init__(self, name, playlistID, image, tracks):
        self.name = name
        self.playlistID = playlistID
        self.image = image
        self.tracks = tracks


class Artist:
    def __init__(self, id, name, image):
        self.id = id
        self.name = name
        self.image = image


# class Tags:
#     def __init__(self, tags)
#         self.tags = tags


# class UserTags(db.Model):
#     __tablename__ = "userTags"

#     id: Mapped[int] = mapped_column(primary_key=True)
#     user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
#     tag: Mapped[str] = mapped_column(nullable=False)


# def addTag(tag):
#     check = db.session.execute(
#         db.select(UserTags.tag).where(UserTags.user_id == current_user.id)
#     ).scalars()

#     if tag in check.all():
#         # print("tag is already in")
#         return None

#     addTag = UserTags(user_id=current_user.id, tag=tag)
#     db.session.add(addTag)
#     db.session.commit()

#     check = db.session.execute(
#         db.select(UserTags.tag).where(UserTags.user_id == current_user.id)
#     ).scalars()
#     print(check.all())
#     return None


def addArtist(name, id, tag):

    check = db.session.execute(
        db.select(AddedArtists.artist_id).where(AddedArtists.user_id == current_user.id)
    ).scalars()

    if id in check.all():
        # print("this artist is already in the user's addedartists database")
        return None

    addArtist = AddedArtists(user_id=current_user.id, artist_id=id, name=name, tag=tag)
    db.session.add(addArtist)
    db.session.commit()

    check = db.session.execute(
        db.select(AddedArtists.artist_id).where(AddedArtists.user_id == current_user.id)
    ).scalars()
    # print(check.all())
    # print("artist successfully added")
    return None


# addArtist = AddedArtists(
#     user_id=current_user.id, artist_id=list(request.form.keys())[0]
# )
# db.session.add(addArtist)
# db.session.commit()
# flash("Artist has been successfully added.", category="success")

# userArtists = db.session.execute(
#     db.select(AddedArtists.artist_id).where(
#         AddedArtists.user_id == current_user.id
#     )
# ).scalars()
# print(userArtists.all())

# return render_template("track.html", searchResultList=searchResultList)


# r = requests.post(
#     "https://accounts.spotify.com/api/token",
#     headers={
#         "Content-Type": "application/x-www-form-urlencoded",
#     },
#     data={
#         "grant_type": "authorization_code",
#         "client_id": "b2817ab1a6a6471dae92088510ed25f1",
#         "client_secret": "d4fad7b2dbac4eca9c558e39c584a6d0",
#     },
# )

# access_token = r.json()["access_token"]
# headers = {"Authorization": "Bearer " + access_token}

headers = {}


@track_blueprint.route("/spotifyauth", methods=["GET"])
@login_required
def spotifyauth():
    authURL = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": "b2817ab1a6a6471dae92088510ed25f1",
        "response_type": "code",
        "redirect_uri": "http://127.0.0.1:5000/callback",
        # "scope": "playlist-read-private playlist-read-collaborative",
        # "show_dialog": True,
    }

    r = requests.get(authURL, params=params)

    # print(r.text)

    return redirect(r.url)


@track_blueprint.route("/callback", methods=["GET"])
@login_required
def callback():
    # print("we're here")
    # print(request.url)
    # print(request.base_url
    # print()

    url = "https://accounts.spotify.com/api/token"

    params = {
        "grant_type": "authorization_code",
        "code": request.args["code"],
        "redirect_uri": "http://127.0.0.1:5000/callback",
    }

    client_id = "b2817ab1a6a6471dae92088510ed25f1"
    client_secret = "d4fad7b2dbac4eca9c558e39c584a6d0"
    b64client_id = base64.b64encode(b"b2817ab1a6a6471dae92088510ed25f1")
    b64client_secret = base64.b64encode(b"d4fad7b2dbac4eca9c558e39c584a6d0")
    authorization = str(
        base64.b64encode(
            b"b2817ab1a6a6471dae92088510ed25f1:d4fad7b2dbac4eca9c558e39c584a6d0"
        ).decode()
    )
    # print(authorization)
    # print("Basic " + authorization)

    headersauth = {
        "Authorization": "Basic " + authorization,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    r = requests.post(url, params=params, headers=headersauth)
    # print(r.json())

    global headers
    headers = {"Authorization": "Bearer " + r.json()["access_token"]}
    # print(headers)

    # params = {"q": "John Coltrane", "type": "artist"}
    # r = requests.get(
    #     "https://api.spotify.com/v1/search", headers=headers, params=params
    # )
    # print(r.json())

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
    return redirect("/newmusic")


@track_blueprint.route("/track", methods=["GET", "POST"])
@login_required
def track():

    if not headers:
        # print("headers is empty.")
        flash("Please sign in to spotify to continue.", category="error")
        return redirect("/")

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

            print(request.form.keys())
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
                user_id=current_user.id,
                artist_id=list(request.form.keys())[0],
                name=request.form.keys()[1],
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

    if not headers:
        print("headers is empty.")
        flash("Please sign in to spotify to continue.", category="error")
        return redirect("/")

    # try:

    if request.method == "GET":

        trackedArtists = db.session.execute(
            db.select(AddedArtists).where(AddedArtists.user_id == current_user.id)
        ).scalars()

        trackedArtistsList = trackedArtists.all()

        if not trackedArtistsList:
            return render_template("/newmusic.html")

        #  userTags = [
        #     tag
        #     for tag in db.session.query(AddedArtists.tag)
        #     .filter_by(user_id=current_user.id)
        #     .distinct()
        # ]

        userTags = []
        for artist in trackedArtistsList:
            if artist.tag not in userTags:
                userTags.append(artist.tag)
        # print(userTags)
        return render_template("/newmusic.html", userTags=userTags)
        # print(trackedArtistsList)
        # print(type(trackedArtists.all()))
        # test = trackedArtists.all()
        # # print(trackedArtists.all()[0])
        # print(test)

        # if not trackedArtistsList:
        #     return render_template("newmusic.html")

        newMusicList = []
        for artist in trackedArtistsList:
            # endpoint = "https://api.spotify.com/v1/artists/" + artist.id

            # # except:
            # #     flash("Please track ")
            # # print(artistID)

            # r = requests.get(endpoint, headers=headers)
            # print(r.json())
            # print(r.json()["name"])
            # artistName = r.json()["name"]
            # print(r.json()["name"])

            endpoint = (
                "https://api.spotify.com/v1/artists/" + artist.artist_id + "/albums"
            )

            r = requests.get(endpoint, headers=headers)
            # print(r.json())

            #         class NewMusic:
            # def __init__(self, artistName, albumName, picture, date, type, flag, albumID, tag):
            #     self.artistName = artistName
            #     self.albumName = albumName
            #     self.picture = picture
            #     self.date = date
            #     self.type = type
            #     self.flag = flag
            #     self.albumID = albumID
            #     self.tag = tag

            for i in range(20):
                newMusicList.append(
                    NewMusic(
                        artist.name,
                        r.json()["items"][i]["name"],
                        r.json()["items"][i]["images"][0]["url"],
                        r.json()["items"][i]["release_date"],
                        r.json()["items"][i]["album_type"],
                        False,
                        r.json()["items"][i]["id"],
                        artist.tag,
                    )
                )
        # print(newMusicList[0].flag)

        # print(newMusicList)

        def returnDate(newMusicObj):
            return newMusicObj.date

        newMusicList.sort(reverse=True, key=returnDate)
        # print(newMusicList)

        return render_template("newmusic.html", newMusicList=newMusicList)
    if request.method == "POST":

        if "tagFilter" in list(request.form.values()):
            # print(list(request.form.keys()))
            # print(list(request.form.keys())[0])

            tagList = list(request.form.keys())
            print(tagList)
            artistList = []

            for tag in tagList:

                taggedArtists = db.session.execute(
                    db.select(AddedArtists)
                    .where(AddedArtists.user_id == current_user.id)
                    .where(AddedArtists.tag == tag)
                ).scalars()

                for artist in taggedArtists.all():
                    artistList.append(artist)

            # return redirect("/newmusic")

            # if not trackedArtistsList:
            #     return render_template("newmusic.html")

            newMusicList = []
            for artist in artistList:

                endpoint = (
                    "https://api.spotify.com/v1/artists/" + artist.artist_id + "/albums"
                )

                r = requests.get(endpoint, headers=headers)

                for i in range(20):
                    newMusicList.append(
                        NewMusic(
                            artist.name,
                            r.json()["items"][i]["name"],
                            r.json()["items"][i]["images"][0]["url"],
                            r.json()["items"][i]["release_date"],
                            r.json()["items"][i]["album_type"],
                            False,
                            r.json()["items"][i]["id"],
                            artist.tag,
                        )
                    )

            def returnDate(newMusicObj):
                return newMusicObj.date

            newMusicList.sort(reverse=True, key=returnDate)

            userTags = [
                tag
                for tag in db.session.query(AddedArtists.tag)
                .filter_by(user_id=current_user.id)
                .distinct()
            ]

            print(userTags)

            return render_template(
                "/newmusic.html", newMusicList=newMusicList, userTags=userTags
            )

        # if not trackedArtistsList:
        #     return render_template("/newmusic.html")

        print(request.form)

        if (not request.form["newTag"]) and ("userTag" not in request.form.values()):
            # print("there is not a new tag in here")
            flash(
                "Please make sure to assign at least one tag to the added artists.",
                category="error",
            )
            return redirect("track-artists")

        print(request.form)
        newTag = request.form["newTag"]
        # addTag(newTag)
        # print(newTag)
        artistsDict = request.form.to_dict()
        del artistsDict["newTag"]
        print(artistsDict)
        if not artistsDict:
            flash(
                "Please make sure to select at least one artist.",
                category="error",
            )
            return redirect("track-artists")

        # print(request.form["newTag"])
        # print(request.form["artist"])
        # artistList = request.form["artist"]
        # print(type(artistList))
        # artistList = artistList.replace("'", "")
        # artistList = artistList.strip("()")
        # artistList = artistList.split(",")
        # artistList[1] = artistList[1].strip()
        # # artistList = artistList.replace("'", "")
        # print(artistList)

        # print(request.form["artist"])
        # print(type(request.form["artist"]))

        # print(artistList)
        # print(list(request.form["artist"]))
        # print(request.form["artist"][0])
        # print(list(request.form.keys()))
        # print(list(request.form.items()))
        # print(list(request.form.items())[1][0])
        print(list(artistsDict.keys()))

        for artistKey in list(artistsDict.keys()):
            addArtist(artistKey, artistsDict[artistKey], newTag)
        # addArtist()

        return redirect("/newmusic")


# class UserPlaylists:
#     def __init__(self, name, playlistID):
#         self.name = name
#         self.playlistID = playlistID
#         # self.images = []


@track_blueprint.route("track-artists", methods=["GET", "POST"])
@login_required
def trackArtists():

    if not headers:
        # print("headers is empty.")
        flash("Please sign in to spotify to continue.", category="error")
        return redirect("/")

    if request.method == "GET":
        r = requests.get("https://api.spotify.com/v1/me/playlists", headers=headers)
        # print(headers)
        userPlaylists = []
        for item in range(r.json()["total"]):
            if not r.json()["items"][item]["images"][0]:
                userPlaylists.append(
                    UserPlaylists(
                        r.json()["items"][item]["name"],
                        r.json()["items"][item]["id"],
                        "",
                        r.json()["items"][item]["tracks"]["href"],
                    )
                )
            else:
                userPlaylists.append(
                    UserPlaylists(
                        r.json()["items"][item]["name"],
                        r.json()["items"][item]["id"],
                        r.json()["items"][item]["images"][0]["url"],
                        r.json()["items"][item]["tracks"]["href"],
                    )
                )
            # print(r.json()["items"][item]["tracks"]["href"])

        userPlaylistsOdd = []
        userPlaylistsEven = []

        for playlist in range(len(userPlaylists)):
            if playlist % 2 == 1:
                # print("this one is odd")
                userPlaylistsOdd.append(userPlaylists[playlist])
            else:
                userPlaylistsEven.append(userPlaylists[playlist])

        # for item in range(len(userPlaylistsOdd)):
        #     print(userPlaylistsOdd[item].name)
        return render_template(
            "track-artists.html",
            userPlaylistsOdd=userPlaylistsOdd,
            userPlaylistsEven=userPlaylistsEven,
        )


@track_blueprint.route("/track-artists-callback", methods=["POST"])
@login_required
def trackArtistsCallback():
    if not headers:
        # print("headers is empty.")
        flash("Please sign in to spotify to continue.", category="error")
        return redirect("/")

    if request.method == "POST":

        #     class Artist:
        # def __init__(self, id, name):
        #     self.id = id
        #     self.name = name

        # print(request.form)
        # print(list(request.form.keys()))
        # print(headers)

        playlistID = list(request.form.keys())[0]

        # url = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlistID)
        url = list(request.form.keys())[1]
        params = {"fields": "limit,total,next,previous,items(track(artists(id,name)))"}
        # print(url)
        # params = {"limit": "50"}
        # print(headers)

        r = requests.get(url, headers=headers, params=params)
        # print(r.json())

        artistList = []
        artistIDList = []
        # if not artistList:
        #     print("it's empty")

        counter = 0

        # print(r.json()["limit"])
        # print(r.json()["total"])
        # print(r.json()["next"])

        # while (r.json()["total"] == 100)

        # while (r.json()["total"] - (counter * r.json()["limit"])) > 0:
        while (r.json()["next"] != None) or (r.json()["previous"] == None):
            counter += 1
            # print(r.json()["limit"])
            # print(r.json()["total"])
            # print(r.json()["next"])

            for item in range(len(r.json()["items"])):
                for artist in range(len(r.json()["items"][item]["track"]["artists"])):
                    # print(r.json()["items"][item]["track"]["artists"][artist]["id"])
                    if (
                        r.json()["items"][item]["track"]["artists"][artist]["id"]
                        not in artistIDList
                    ):
                        r2 = requests.get(
                            "https://api.spotify.com/v1/artists/{}".format(
                                r.json()["items"][item]["track"]["artists"][artist][
                                    "id"
                                ]
                            ),
                            headers=headers,
                        )
                        artistIDList.append(
                            r.json()["items"][item]["track"]["artists"][artist]["id"]
                        )
                        if r2.json()["images"]:
                            artistList.append(
                                Artist(
                                    r.json()["items"][item]["track"]["artists"][artist][
                                        "id"
                                    ],
                                    r.json()["items"][item]["track"]["artists"][artist][
                                        "name"
                                    ],
                                    r2.json()["images"][0]["url"],
                                )
                            )
                        else:
                            artistList.append(
                                Artist(
                                    r.json()["items"][item]["track"]["artists"][artist][
                                        "id"
                                    ],
                                    r.json()["items"][item]["track"]["artists"][artist][
                                        "name"
                                    ],
                                    "",
                                )
                            )
            if r.json()["next"] == None:
                break
            else:
                r = requests.get(r.json()["next"], headers=headers, params=params)

        # userTags = db.session.execute(
        #     db.select(AddedArtists.tag).filter_by(user_id=current_user.id)
        # ).scalars()
        # userTags = userTags.all()

        userTags = db.session.execute(
            db.select(AddedArtists.tag).where(AddedArtists.user_id == current_user.id)
        )
        userTags = userTags.scalars().unique().all()
        # print(userTags)
        # userTagsList = []
        # for tag in userTags:
        #     print(type(tag))
        #     test = tag.strip("(',)")
        #     print(test)
        #     userTagsList.append(test)

        # userTags = [
        #     tag
        #     for tag in db.session.query(AddedArtists.tag)
        #     .filter_by(user_id=current_user.id)
        #     .distinct()
        # ]
        # print(userTags)
        # print(userTags[0])
        # print(type(userTags[0]))

        # return render_template("track-artists-callback.html", artistList=artistList)
        return render_template(
            "track-artists-callback.html", artistList=artistList, userTags=userTags
        )


# @track_blueprint.route("/test", methods=["GET"])
# def test():
#     return render_template("test.html")
