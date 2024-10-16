from flask import Blueprint, render_template, redirect, url_for, request, flash
import requests
from requests.auth import HTTPBasicAuth
from .models import *
from flask_login import login_required, current_user
import base64
import json
import random


track_blueprint = Blueprint("track", __name__)


class SearchResultTrack:
    def __init__(self, name, picture, link, id):
        self.name = name
        self.picture = picture
        self.link = link
        self.id = id


def addArtist(name, id, tag):

    check = db.session.execute(
        db.select(AddedArtists.artist_id).where(AddedArtists.user_id == current_user.id)
    ).scalars()

    if id in check.all():
        return None

    tag_id = (
        db.session.execute(
            db.select(UserTags.id)
            .where(UserTags.user_id == current_user.id)
            .where(UserTags.tag == tag)
        )
        .scalars()
        .all()[0]
    )

    addArtist = AddedArtists(
        user_id=current_user.id, tag_id=tag_id, artist_id=id, name=name, tag=tag
    )
    db.session.add(addArtist)
    db.session.commit()

    # check = db.session.execute(
    #     db.select(AddedArtists.artist_id).where(AddedArtists.user_id == current_user.id)
    # ).scalars()

    return None


headers = {}


@track_blueprint.route("/spotifyauth", methods=["GET"])
@login_required
def spotifyauth():
    authURL = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": "b2817ab1a6a6471dae92088510ed25f1",
        "response_type": "code",
        "redirect_uri": "http://127.0.0.1:5000/callback",
        "scope": "playlist-read-private,playlist-modify-public,playlist-modify-private",
        # "show_dialog": True,
    }

    r = requests.get(authURL, params=params)

    # print(r.text)

    return redirect(r.url)


@track_blueprint.route("/callback", methods=["GET"])
@login_required
def callback():

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

    headersauth = {
        "Authorization": "Basic " + authorization,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    r = requests.post(url, params=params, headers=headersauth)

    global headers
    headers = {"Authorization": "Bearer " + r.json()["access_token"]}

    check = (
        db.session.execute(
            db.select(AccessToken).where(AccessToken.user_id == current_user.id)
        )
        .scalars()
        .all()
    )
    print(check)
    if not check:
        access_token = AccessToken(
            user_id=current_user.id,
            access_token=r.json()["access_token"],
            refresh_token=r.json()["refresh_token"],
        )
        db.session.add(access_token)
        db.session.commit()
    else:
        check[0].access_token = r.json()["access_token"]
        check[0].refresh_token = r.json()["refresh_token"]
        db.session.commit()

    print(check)
    print(check[0].access_token)
    print(check[0].refresh_token)

    return redirect("/newmusic")


@track_blueprint.route("/newmusic", methods=["GET", "POST"])
@login_required
def newmusic():

    # print(request.form)

    # print(current_user)
    # print(current_user.id)

    if not headers:
        print("headers is empty.")
        flash("Please sign in to spotify to continue.", category="error")
        return redirect("/")

    if request.method == "GET":

        userTags = (
            db.session.execute(
                db.select(UserTags.tag).where(UserTags.user_id == current_user.id)
            )
            .scalars()
            .all()
        )

        if not userTags:
            return render_template("/newmusic.html")

        return render_template("/newmusic.html", userTags=userTags)

    if request.method == "POST":

        print(request.form)

        if not request.form:
            flash(
                "Please select one or more tags to show associated music.",
                category="error",
            )
            return redirect("/newmusic")

        if "tagFilter" in list(request.form.values()):

            tagList = list(request.form.keys())
            artistList = []

            for tag in tagList:

                taggedArtists = db.session.execute(
                    db.select(AddedArtists)
                    .where(AddedArtists.user_id == current_user.id)
                    .where(AddedArtists.tag == tag)
                ).scalars()

                for artist in taggedArtists.all():
                    if artist not in artistList:
                        artistList.append(artist)

            newMusicList = []

            limit = 50

            params = {"include_groups": "album,single", "limit": limit}

            class NewMusic:
                def __init__(
                    self, artistName, albumName, picture, date, type, flag, albumID, tag
                ):
                    self.artistName = artistName
                    self.albumName = albumName
                    self.picture = picture
                    self.date = date
                    self.type = type
                    self.flag = flag
                    self.albumID = albumID
                    self.tag = tag

            for artist in artistList:

                endpoint = (
                    "https://api.spotify.com/v1/artists/" + artist.artist_id + "/albums"
                )

                r = requests.get(endpoint, params=params, headers=headers)

                while True:

                    for i in range(len(r.json()["items"])):
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

                    if (r.json()["next"]) == None:
                        break
                    r = requests.get(r.json()["next"], headers=headers)

            def returnDate(newMusicObj):
                return newMusicObj.date

            newMusicList.sort(reverse=True, key=returnDate)

            userTags = (
                db.session.execute(
                    db.select(UserTags.tag).where(UserTags.user_id == current_user.id)
                )
                .scalars()
                .all()
            )

            params = {"limit": "50"}

            r = requests.get(
                "https://api.spotify.com/v1/me/playlists",
                headers=headers,
                params=params,
            )

            userPlaylists = []

            class UserPlaylists2:
                def __init__(self, name, playlistID, image):
                    self.name = name
                    self.playlistID = playlistID
                    self.image = image

            for playlist in range(len(r.json()["items"])):
                if not r.json()["items"][playlist]["images"]:
                    playlistObject = UserPlaylists2(
                        r.json()["items"][playlist]["name"],
                        r.json()["items"][playlist]["id"],
                        "",
                    )
                else:
                    playlistObject = UserPlaylists2(
                        r.json()["items"][playlist]["name"],
                        r.json()["items"][playlist]["id"],
                        r.json()["items"][playlist]["images"][0]["url"],
                    )
                userPlaylists.append(playlistObject)

            userPlaylists1 = []
            userPlaylists2 = []
            userPlaylists3 = []

            for playlistObjectIndex in range(len(userPlaylists)):
                if playlistObjectIndex % 3 == 1:
                    userPlaylists1.append(userPlaylists[playlistObjectIndex])
                if playlistObjectIndex % 3 == 2:
                    userPlaylists2.append(userPlaylists[playlistObjectIndex])
                if playlistObjectIndex % 3 == 0:
                    userPlaylists3.append(userPlaylists[playlistObjectIndex])

            # for x in userPlaylists1:
            #     print(x.image)

            return render_template(
                "/newmusic.html",
                newMusicList=newMusicList,
                userTags=userTags,
                userPlaylists1=userPlaylists1,
                userPlaylists2=userPlaylists2,
                userPlaylists3=userPlaylists3,
            )

        if "userTag" not in request.form.values():
            flash(
                "Please make sure to assign at least one tag to the added artists.",
                category="error",
            )
            return redirect("track-from-playlist")

        if "userTag" in request.form.values():

            requestDict = request.form.to_dict()
            tagList = []

            for x in list(requestDict.values()):
                if x == "userTag":
                    tag = list(requestDict.keys())[
                        list(requestDict.values()).index("userTag")
                    ]
                    tagList.append(tag)
                    del requestDict[tag]

        if not requestDict:
            flash(
                "Please make sure to select at least one artist.",
                category="error",
            )
            return redirect("track-from-playlist")

        if tagList:
            for artistKey in list(requestDict.keys()):
                for tag in tagList:
                    addArtist(artistKey, requestDict[artistKey], tag)
            return redirect("/newmusic")

        if request.form["addToPlaylistSelect"] == "newPlaylist":
            if not request.form["newPlaylistName"]:
                flash("Please enter a new playlist name.", category="error")
                return redirect("/newmusic")
            else:
                r = requests.get("https://api.spotify.com/v1/me", headers=headers)
                spotifyUserID = r.json()["id"]

                createPlaylistEndpoint = (
                    "https://api.spotify.com/v1/users/" + spotifyUserID + "/playlists"
                )
                # print(request.form)
                newPlaylistName = request.form["newPlaylistName"]
                data = {"name": newPlaylistName}

                r = requests.post(createPlaylistEndpoint, headers=headers, json=data)
                newPlaylistID = r.json()["id"]

                albumIDDict = request.form.to_dict()
                del albumIDDict["addToPlaylistSelect"]
                del albumIDDict["newPlaylistName"]

                URIArray = []

                params = {"limit": 50}

                for albumID in albumIDDict.keys():
                    getAlbumTracksEndpoint = (
                        "https://api.spotify.com/v1/albums/{}/tracks".format(albumID)
                    )
                    r = requests.get(
                        getAlbumTracksEndpoint, headers=headers, params=params
                    )
                    for i in range(len(r.json()["items"])):
                        URIArray.append(r.json()["items"][i]["uri"])

                print(URIArray)

                addItemsToPlaylistEndpoint = (
                    "https://api.spotify.com/v1/playlists/{}/tracks".format(
                        newPlaylistID
                    )
                )

                data = {"uris": URIArray}

                r = requests.post(
                    addItemsToPlaylistEndpoint, headers=headers, json=data
                )

                flash(
                    "Selected albums have been succesfully added to a new playlist.",
                    category="success",
                )
                return redirect("/newmusic")

        if request.form["addToPlaylistSelect"] == "existingPlaylist":

            userPlaylistID = request.form["userPlaylistID"]

            albumIDDict = request.form.to_dict()
            del albumIDDict["addToPlaylistSelect"]
            del albumIDDict["newPlaylistName"]
            del albumIDDict["userPlaylistID"]

            URIArray = []

            params = {"limit": 50}

            for albumID in albumIDDict.keys():
                getAlbumTracksEndpoint = (
                    "https://api.spotify.com/v1/albums/{}/tracks".format(albumID)
                )
                r = requests.get(getAlbumTracksEndpoint, headers=headers, params=params)
                for i in range(len(r.json()["items"])):
                    URIArray.append(r.json()["items"][i]["uri"])

            addItemsToPlaylistEndpoint = (
                "https://api.spotify.com/v1/playlists/" + userPlaylistID + "/tracks"
            )

            data = {"uris": URIArray}

            r = requests.post(addItemsToPlaylistEndpoint, headers=headers, json=data)

            flash(
                "Selected albums have been succesfully added to the selected playlist.",
                category="success",
            )
            return redirect("/newmusic")


@track_blueprint.route("/tag-list", methods=["GET", "POST"])
@login_required
def tagList():

    if request.method == "POST":

        print(request.form)

        if "newTag" in request.form.keys():
            result = (
                db.session.execute(
                    db.select(UserTags).where(UserTags.tag == request.form["newTag"])
                )
                .scalars()
                .all()
            )
            if not result:
                newTag = UserTags(user_id=current_user.id, tag=request.form["newTag"])
                db.session.add(newTag)
                db.session.commit()
                flash("New tag created successfully.", category="success")
            else:
                flash("Tag already exists.", category="error")

        if "editedTag" in request.form.keys():
            result = (
                db.session.execute(
                    db.select(UserTags).where(UserTags.tag == request.form["editedTag"])
                )
                .scalars()
                .all()
            )
            if result:
                flash("The edited tag already exists.", category="error")
            else:
                result = (
                    db.session.execute(
                        db.select(UserTags).where(
                            UserTags.tag == request.form["originalTag"]
                        )
                    )
                    .scalars()
                    .all()
                )
                result[0].tag = request.form["editedTag"]
                db.session.commit()
                flash("Tag name changed successfully.", category="success")
                result = (
                    db.session.execute(
                        db.select(AddedArtists).where(
                            AddedArtists.tag == request.form["originalTag"]
                        )
                    )
                    .scalars()
                    .all()
                )
                for artist in result:
                    artist.tag = request.form["editedTag"]
                db.session.commit()

        if "removeTag" in request.form:
            result = (
                db.session.execute(
                    db.select(UserTags)
                    .where(UserTags.user_id == current_user.id)
                    .where(UserTags.tag == request.form["removeTag"])
                )
                .scalars()
                .all()
            )
            print(result)
            print(result[0].tag)
            db.session.delete(result[0])
            db.session.commit()

            result = (
                db.session.execute(
                    db.select(AddedArtists)
                    .where(AddedArtists.user_id == current_user.id)
                    .where(AddedArtists.tag == request.form["removeTag"])
                )
                .scalars()
                .all()
            )
            for artist in result:
                db.session.delete(artist)
            db.session.commit()
            flash("Tag and artists deleted successfully.", category="success")

        if "removeArtist" in request.form.keys():
            print(request.form)
            AddedArtists.query.filter_by(
                artist_id=request.form["removeArtist"]
            ).delete()
            db.session.commit()
            flash("Artist removed successfully.", category="success")

    test = (
        db.session.execute(db.select(UserTags).where(UserTags.tag == "test"))
        .scalars()
        .all()[0]
    )
    print(test.auto_update_date_last_checked)
    # test.auto_update_date_last_checked = datetime.datetime(2020, 1, 1)
    # db.session.commit()
    # test2 = (
    #     db.session.execute(db.select(UserTags).where(UserTags.tag == "test"))
    #     .scalars()
    #     .all()[0]
    # )
    # print(test2.auto_update_date_last_checked)

    class UserTagsAndArtists:
        def __init__(self, editID, deleteID, tag, artists, linkedPlaylistName):
            self.editID = editID
            self.deleteID = deleteID
            self.tag = tag
            self.artists = artists
            self.linkedPlaylistName = linkedPlaylistName

    result = (
        db.session.execute(
            db.select(UserTags).where(UserTags.user_id == current_user.id)
        )
        .scalars()
        .all()
    )

    userTagsUIInfo = []
    # artistList = []
    editIDList = random.sample(range(1, len(result) + 1), len(result))
    deleteIDList = random.sample(range(1, len(result) + 1), len(result))
    for item in range(len(deleteIDList)):
        deleteIDList[item] = -abs(deleteIDList[item])
    # print(editIDList)
    # print(deleteIDList)
    counter = 0

    for userTagsObj in result:
        result = (
            db.session.execute(
                db.select(AddedArtists)
                .where(AddedArtists.tag == userTagsObj.tag)
                .where(AddedArtists.user_id == current_user.id)
            )
            .scalars()
            .all()
        )

        # print(userTagsObj.auto_update_playlist_id)
        if userTagsObj.auto_update_playlist_id is not None:
            r = requests.get(
                "https://api.spotify.com/v1/playlists/{}".format(
                    userTagsObj.auto_update_playlist_id
                ),
                headers=headers,
            )
            # print(r.json())
            obj = UserTagsAndArtists(
                editIDList[counter],
                deleteIDList[counter],
                userTagsObj.tag,
                result,
                r.json()["name"],
            )
            userTagsUIInfo.append(obj)
        else:
            obj = UserTagsAndArtists(
                editIDList[counter], deleteIDList[counter], userTagsObj.tag, result, ""
            )
            userTagsUIInfo.append(obj)
        counter += 1

    userTagsUIInfo.sort(key=lambda x: x.tag)
    # userTagsAndArtistsDict = {}

    # for counter, tag in enumerate(tagList):
    #     userTagsAndArtistsDict[tag] = artistList[counter]

    # userTagsAndArtistsDict = {
    #     k: v
    #     for k, v in sorted(
    #         userTagsAndArtistsDict.items(),
    #         key=lambda item: len(item[1]),
    #         reverse=True,
    #     )
    # }

    # userTagsAndArtistsDict = {
    #     k: v
    #     for k, v in sorted(userTagsAndArtistsDict.items(), key=lambda item: (item[0]))
    # }

    # class UserTagsAndArtists:
    #     def __init__(self, tag, artists, linkedPlaylist):
    #         self.tag = tag
    #         self.artists = artists
    #         self.linkedPlaylist = linkedPlaylist

    # userTagsAndArtistsList = []
    # for tag, artists in userTagsAndArtistsDict.items():
    #     userTagsAndArtistsObj = UserTagsAndArtists(tag, artists)
    #     userTagsAndArtistsList.append(userTagsAndArtistsObj)

    return render_template("tag-list.html", userTagsUIInfo=userTagsUIInfo)


@track_blueprint.route("/track-individual", methods=["GET", "POST"])
@login_required
def trackIndividual():

    if not headers:
        # print("headers is empty.")
        flash("Please sign in to spotify to continue.", category="error")
        return redirect("/")

    if request.method == "GET":

        return render_template("track-individual.html")
    if request.method == "POST":
        print(request.form)
        if "searchArtist" in request.form:

            searchArtist = request.form.get("searchArtist")
            type = ["artist"]

            payload = {"q": searchArtist, "type": type}

            r = requests.get(
                "https://api.spotify.com/v1/search", params=payload, headers=headers
            )
            # print(r.json())

            global searchResultList
            searchResultList = []

            for i in range(10):
                # print(r.json())
                if len(r.json()["artists"]["items"]) < 10:
                    flash(
                        "Less than 5 items were found. Please check your search and try again.",
                        category="error",
                    )
                    return redirect("add-all")
                if r.json()["artists"]["items"][i]["images"]:
                    searchResultList.append(
                        SearchResultTrack(
                            r.json()["artists"]["items"][i]["name"],
                            r.json()["artists"]["items"][i]["images"][0]["url"],
                            r.json()["artists"]["items"][i]["external_urls"]["spotify"],
                            r.json()["artists"]["items"][i]["id"],
                        )
                    )
                else:
                    searchResultList.append(
                        SearchResultTrack(
                            r.json()["artists"]["items"][i]["name"],
                            "",
                            r.json()["artists"]["items"][i]["external_urls"]["spotify"],
                            r.json()["artists"]["items"][i]["id"],
                        )
                    )

            global userTags
            userTags = (
                db.session.execute(
                    db.select(UserTags.tag).where(UserTags.user_id == current_user.id)
                )
                .scalars()
                .all()
            )

            return render_template(
                "track-individual.html",
                searchResultList=searchResultList,
                userTags=userTags,
            )
        else:

            print(request.form)

            if "selectedTag" not in request.form.values():
                flash("Please select a tag.", category="error")
                return redirect("/track-individual")

            requestDict = request.form.to_dict()
            # print(requestDict)

            tagCount = list(request.form.values()).count("selectedTag")
            # print(tagCount)

            tagList = []
            for x in range(tagCount):
                tagList.append(list(requestDict.keys())[0])
                del requestDict[list(requestDict.keys())[0]]

            print(tagList)
            print(requestDict)

            addedArtistID = list(requestDict.values())[0]

            for tag in tagList:
                check = (
                    db.session.execute(
                        db.select(AddedArtists)
                        .where(AddedArtists.user_id == current_user.id)
                        .where(AddedArtists.artist_id == addedArtistID)
                        .where(AddedArtists.tag == tag)
                    )
                    .scalars()
                    .all()
                )
                if not check:
                    tag_id = (
                        db.session.execute(
                            db.select(UserTags.id)
                            .where(UserTags.user_id == current_user.id)
                            .where(UserTags.tag == tag)
                        )
                        .scalars()
                        .all()[0]
                    )
                    print(tag_id)
                    addArtist = AddedArtists(
                        user_id=current_user.id,
                        tag_id=tag_id,
                        artist_id=addedArtistID,
                        name=list(requestDict.keys())[0],
                        tag=tag,
                    )
                    db.session.add(addArtist)
                    db.session.commit()
                    flash(
                        "Artist has been successfully added to {}.".format(tag),
                        category="success",
                    )
                else:
                    flash(
                        "You are already tracking this artist in {}.".format(tag),
                        category="success",
                    )
            return render_template(
                "track-individual.html",
                searchResultList=searchResultList,
                userTags=userTags,
            )


@track_blueprint.route("track-from-playlist", methods=["GET", "POST"])
@login_required
def trackFromPlaylist():

    if not headers:
        # print("headers is empty.")
        flash("Please sign in to spotify to continue.", category="error")
        return redirect("/")

    if request.method == "GET":

        limit = 20
        params = {"limit": limit}
        r = requests.get(
            "https://api.spotify.com/v1/me/playlists", headers=headers, params=params
        )

        class UserPlaylists:
            def __init__(self, name, playlistID, image, tracks):
                self.name = name
                self.playlistID = playlistID
                self.image = image
                self.tracks = tracks

        userPlaylists = []

        while True:
            if len(r.json()["items"]) < limit:
                limit = len(r.json()["items"])
            for item in range(limit):
                if not r.json()["items"][item]["images"]:
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
            if r.json()["next"] is None:
                break
            else:
                r = requests.get(r.json()["next"], headers=headers)

        userPlaylistsOdd = []
        userPlaylistsEven = []

        # for item in userPlaylists:
        #     print(item.name)
        userPlaylists.sort(key=lambda item: item.name)
        # for item in userPlaylists:
        #     print(item.name)

        for playlist in range(len(userPlaylists)):
            if playlist % 2 == 1:
                userPlaylistsOdd.append(userPlaylists[playlist])
            else:
                userPlaylistsEven.append(userPlaylists[playlist])

        return render_template(
            "track-from-playlist.html",
            userPlaylistsOdd=userPlaylistsOdd,
            userPlaylistsEven=userPlaylistsEven,
        )


@track_blueprint.route("/track-from-playlist-callback", methods=["POST"])
@login_required
def trackFromPlaylistCallback():
    if not headers:
        # print("headers is empty.")
        flash("Please sign in to spotify to continue.", category="error")
        return redirect("/")

    if request.method == "POST":

        playlistID = list(request.form.keys())[0]

        url = list(request.form.keys())[1]

        params = {"fields": "limit,total,next,previous,items(track(artists(id,name)))"}

        r = requests.get(url, headers=headers, params=params)
        # print(r.url)

        artistList = []
        artistIDList = []

        counter = 0

        class Artist:
            def __init__(self, id, name, image):
                self.id = id
                self.name = name
                self.image = image

        callCounter = 0

        while (r.json()["next"] != None) or (r.json()["previous"] == None):
            counter += 1

            for item in range(len(r.json()["items"])):
                for artist in range(len(r.json()["items"][item]["track"]["artists"])):
                    # print(r.json()["items"][item]["track"]["artists"])

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
                        callCounter += 1
                        artistIDList.append(
                            r.json()["items"][item]["track"]["artists"][artist]["id"]
                        )
                        # print(callCounter)
                        # print(r2.json())
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

        userTags = (
            db.session.execute(
                db.select(UserTags.tag).where(UserTags.user_id == current_user.id)
            )
            .scalars()
            .all()
        )

        return render_template(
            "track-from-playlist-callback.html",
            artistList=artistList,
            userTags=userTags,
        )


@track_blueprint.route("/auto-track", methods=["GET", "POST"])
@login_required
def autoTrack():

    if not headers:

        flash("Please sign in to spotify to continue.", category="error")
        return redirect("/")

    print(request.form)

    if request.method == "GET":

        userTags = (
            db.session.execute(
                db.select(UserTags.tag).where(UserTags.user_id == current_user.id)
            )
            .scalars()
            .all()
        )

        params = {"limit": "50"}

        r = requests.get(
            "https://api.spotify.com/v1/me/playlists",
            headers=headers,
            params=params,
        )

        r2 = requests.get("https://api.spotify.com/v1/me", headers=headers)
        spotifyUserID = r2.json()["id"]

        userPlaylists = []

        class UserPlaylists2:
            def __init__(self, name, playlistID, image):
                self.name = name
                self.playlistID = playlistID
                self.image = image

        for playlist in range(len(r.json()["items"])):
            if spotifyUserID == r.json()["items"][playlist]["owner"]["id"]:
                if not r.json()["items"][playlist]["images"]:
                    playlistObject = UserPlaylists2(
                        r.json()["items"][playlist]["name"],
                        r.json()["items"][playlist]["id"],
                        "",
                    )
                else:
                    playlistObject = UserPlaylists2(
                        r.json()["items"][playlist]["name"],
                        r.json()["items"][playlist]["id"],
                        r.json()["items"][playlist]["images"][0]["url"],
                    )
                userPlaylists.append(playlistObject)

        userPlaylists1 = []
        userPlaylists2 = []
        userPlaylists3 = []

        for playlistObjectIndex in range(len(userPlaylists)):
            if playlistObjectIndex % 3 == 1:
                userPlaylists1.append(userPlaylists[playlistObjectIndex])
            if playlistObjectIndex % 3 == 2:
                userPlaylists2.append(userPlaylists[playlistObjectIndex])
            if playlistObjectIndex % 3 == 0:
                userPlaylists3.append(userPlaylists[playlistObjectIndex])

        return render_template(
            "auto-track.html",
            userTags=userTags,
            userPlaylists1=userPlaylists1,
            userPlaylists2=userPlaylists2,
            userPlaylists3=userPlaylists3,
        )
    if request.method == "POST":

        userTags = (
            db.session.execute(
                db.select(UserTags.tag).where(UserTags.user_id == current_user.id)
            )
            .scalars()
            .all()
        )

        params = {"limit": "50"}

        r = requests.get(
            "https://api.spotify.com/v1/me/playlists",
            headers=headers,
            params=params,
        )

        userPlaylists = []

        class UserPlaylists2:
            def __init__(self, name, playlistID, image):
                self.name = name
                self.playlistID = playlistID
                self.image = image

        for playlist in range(len(r.json()["items"])):
            if not r.json()["items"][playlist]["images"]:
                playlistObject = UserPlaylists2(
                    r.json()["items"][playlist]["name"],
                    r.json()["items"][playlist]["id"],
                    "",
                )
            else:
                playlistObject = UserPlaylists2(
                    r.json()["items"][playlist]["name"],
                    r.json()["items"][playlist]["id"],
                    r.json()["items"][playlist]["images"][0]["url"],
                )
            userPlaylists.append(playlistObject)

        userPlaylists1 = []
        userPlaylists2 = []
        userPlaylists3 = []

        for playlistObjectIndex in range(len(userPlaylists)):
            if playlistObjectIndex % 3 == 1:
                userPlaylists1.append(userPlaylists[playlistObjectIndex])
            if playlistObjectIndex % 3 == 2:
                userPlaylists2.append(userPlaylists[playlistObjectIndex])
            if playlistObjectIndex % 3 == 0:
                userPlaylists3.append(userPlaylists[playlistObjectIndex])

        if "tagFilter" not in request.form.values():
            flash("Please select at least one tag.", category="error")
            return render_template(
                "auto-track.html",
                userTags=userTags,
                userPlaylists1=userPlaylists1,
                userPlaylists2=userPlaylists2,
                userPlaylists3=userPlaylists3,
            )

        if (
            request.form["addToPlaylistSelect"] == "newPlaylist"
            and not request.form["newPlaylistName"]
        ):
            flash("Please enter a name for the new playlist.", category="error")
            return render_template(
                "auto-track.html",
                userTags=userTags,
                userPlaylists1=userPlaylists1,
                userPlaylists2=userPlaylists2,
                userPlaylists3=userPlaylists3,
            )

        requestDict = request.form.to_dict()

        tagList = []

        for item in requestDict.items():
            if item[1] == "tagFilter":
                tagList.append(item[0])

        if request.form["addToPlaylistSelect"] == "newPlaylist":
            r = requests.get("https://api.spotify.com/v1/me", headers=headers)
            spotifyUserID = r.json()["id"]

            createPlaylistEndpoint = (
                "https://api.spotify.com/v1/users/" + spotifyUserID + "/playlists"
            )

            newPlaylistName = request.form["newPlaylistName"]
            data = {"name": newPlaylistName}

            r = requests.post(createPlaylistEndpoint, headers=headers, json=data)
            newPlaylistID = r.json()["id"]

            response = ""
            for tag in tagList:
                userTagsObject = db.session.execute(
                    db.select(UserTags)
                    .where(UserTags.user_id == current_user.id)
                    .where(UserTags.tag == tag)
                ).scalar_one()
                userTagsObject.auto_update = True
                userTagsObject.auto_update_playlist_id = newPlaylistID
                userTagsObject.auto_update_date_last_checked = datetime.datetime.now()
                db.session.commit()

            if len(tagList) == 1:
                flash(
                    "Tag {} has been linked to your new playlist.".format(tagList[0]),
                    category="success",
                )
            elif len(tagList) == 2:
                flash(
                    "Tags {} has been linked to your new playlist.".format(
                        "{} and {}".format(tagList[0]), tagList[1]
                    ),
                    category="success",
                )
            else:
                x = ""
                for tag in tagList:
                    x += tag
                    if tag == tagList[-2]:
                        break
                    x += ", "
                x += ", and "
                x += tagList[-1]
                flash(
                    "Tags {} have been linked to your new playlist.".format(x),
                    category="success",
                )

        if request.form["addToPlaylistSelect"] == "existingPlaylist":
            print(request.form)

            print(tagList)
            if len(list(request.form.values())) == len(tagList) + 2:
                flash("Please select an existing playlist.", category="error")
                return redirect("auto-track")

            for tag in tagList:
                userTagsObject = db.session.execute(
                    db.select(UserTags)
                    .where(UserTags.user_id == current_user.id)
                    .where(UserTags.tag == tag)
                ).scalar_one()
                userTagsObject.auto_update = True
                userTagsObject.auto_update_playlist_id = list(request.form.keys())[-1]

                userTagsObject.auto_update_date_last_checked = datetime.datetime.now()
                db.session.commit()

            if len(tagList) == 1:
                flash(
                    "Tag {} has been linked to playlist {}.".format(
                        tagList[0], list(request.form.values())[-1]
                    ),
                    category="success",
                )
            elif len(tagList) == 2:
                flash(
                    "Tags {} has been linked to playlist {}.".format(
                        "{} and {}".format(tagList[0]),
                        tagList[1],
                        list(request.form.values())[-1],
                    ),
                    category="success",
                )
            else:
                x = ""
                for tag in tagList:
                    x += tag
                    if tag == tagList[-2]:
                        break
                    x += ", "
                x += ", and "
                x += tagList[-1]
                flash(
                    "Tags {} have been linked to playlist {}.".format(
                        x, list(request.form.values())[-1]
                    ),
                    category="success",
                )

        return render_template(
            "auto-track.html",
            userTags=userTags,
            userPlaylists1=userPlaylists1,
            userPlaylists2=userPlaylists2,
            userPlaylists3=userPlaylists3,
        )


@track_blueprint.route("/add-all", methods=["GET", "POST"])
@login_required
def addAll():
    if not headers:
        # print("headers is empty.")
        flash("Please sign in to spotify to continue.", category="error")
        return redirect("/")

    if request.method == "GET":
        return render_template("add-all.html")

    if request.method == "POST":
        if "searchArtist" in request.form:

            searchArtist = request.form.get("searchArtist")
            type = ["artist"]

            payload = {"q": searchArtist, "type": type}

            r = requests.get(
                "https://api.spotify.com/v1/search", params=payload, headers=headers
            )

            global searchResultList
            searchResultList = []

            for i in range(5):
                if len(r.json()["artists"]["items"]) < 5:
                    flash(
                        "Less than 5 items were found. Please check your search and try again.",
                        category="error",
                    )
                    return redirect("add-all")
                searchResultList.append(
                    SearchResultTrack(
                        r.json()["artists"]["items"][i]["name"],
                        r.json()["artists"]["items"][i]["images"][0]["url"],
                        r.json()["artists"]["items"][i]["external_urls"]["spotify"],
                        r.json()["artists"]["items"][i]["id"],
                    )
                )

            params = {"limit": "50"}

            r = requests.get(
                "https://api.spotify.com/v1/me/playlists",
                headers=headers,
                params=params,
            )

            userPlaylists = []

            class UserPlaylists2:
                def __init__(self, name, playlistID, image):
                    self.name = name
                    self.playlistID = playlistID
                    self.image = image

            for playlist in range(len(r.json()["items"])):
                if not r.json()["items"][playlist]["images"]:
                    playlistObject = UserPlaylists2(
                        r.json()["items"][playlist]["name"],
                        r.json()["items"][playlist]["id"],
                        "",
                    )
                else:
                    playlistObject = UserPlaylists2(
                        r.json()["items"][playlist]["name"],
                        r.json()["items"][playlist]["id"],
                        r.json()["items"][playlist]["images"][0]["url"],
                    )
                userPlaylists.append(playlistObject)

            userPlaylists1 = []
            userPlaylists2 = []
            userPlaylists3 = []

            for playlistObjectIndex in range(len(userPlaylists)):
                if playlistObjectIndex % 3 == 1:
                    userPlaylists1.append(userPlaylists[playlistObjectIndex])
                if playlistObjectIndex % 3 == 2:
                    userPlaylists2.append(userPlaylists[playlistObjectIndex])
                if playlistObjectIndex % 3 == 0:
                    userPlaylists3.append(userPlaylists[playlistObjectIndex])

            for x in userPlaylists1:
                print(x.name)

            return render_template(
                "add-all.html",
                searchResultList=searchResultList,
                userPlaylists1=userPlaylists1,
                userPlaylists2=userPlaylists2,
                userPlaylists3=userPlaylists3,
            )
        else:

            if request.form["addToPlaylistSelect"] == "newPlaylist":
                if not request.form["newPlaylistName"]:
                    flash("Please enter a new playlist name.", category="error")
                    return redirect("/add-all")
                else:
                    r = requests.get("https://api.spotify.com/v1/me", headers=headers)
                    spotifyUserID = r.json()["id"]

                    createPlaylistEndpoint = (
                        "https://api.spotify.com/v1/users/"
                        + spotifyUserID
                        + "/playlists"
                    )

                    newPlaylistName = request.form["newPlaylistName"]
                    data = {"name": newPlaylistName}

                    r = requests.post(
                        createPlaylistEndpoint, headers=headers, json=data
                    )
                    newPlaylistID = r.json()["id"]

                    requestDict = request.form.to_dict()
                    del requestDict["addToPlaylistSelect"]
                    del requestDict["newPlaylistName"]

                    limit = 50

                    params = {
                        "include_groups": "album,single",
                        "limit": limit,
                    }

                    artistAlbumIDsAndDates = []

                    endpoint = (
                        "https://api.spotify.com/v1/artists/"
                        + list(requestDict.values())[0]
                        + "/albums"
                    )

                    r = requests.get(endpoint, params=params, headers=headers)

                    while True:

                        for i in range(len(r.json()["items"])):
                            artistAlbumIDsAndDates.append(
                                (
                                    r.json()["items"][i]["id"],
                                    r.json()["items"][i]["release_date"],
                                )
                            )

                        if (r.json()["next"]) == None:
                            break
                        r = requests.get(r.json()["next"], headers=headers)

                    artistAlbumIDsAndDates.sort(reverse=True, key=lambda x: x[1])

                    URIArray = []

                    params = {"limit": 50}

                    for albumIDAndDate in artistAlbumIDsAndDates:
                        getAlbumTracksEndpoint = (
                            "https://api.spotify.com/v1/albums/{}/tracks".format(
                                albumIDAndDate[0]
                            )
                        )
                        r = requests.get(
                            getAlbumTracksEndpoint, headers=headers, params=params
                        )
                        for i in range(len(r.json()["items"])):
                            URIArray.append(r.json()["items"][i]["uri"])

                    # print(URIArray)
                    # print(len(URIArray))

                    addItemsToPlaylistEndpoint = (
                        "https://api.spotify.com/v1/playlists/{}/tracks".format(
                            newPlaylistID
                        )
                    )

                    data = {"uris": URIArray}

                    a = 0
                    b = 99
                    URITempArray = []
                    if len(URIArray) > 100:
                        while True:
                            if a == b:
                                URITempArray = URIArray[a]
                            else:
                                URITempArray = URIArray[a:b]
                            data = {"uris": URITempArray}
                            requests.post(
                                addItemsToPlaylistEndpoint, headers=headers, json=data
                            )
                            if b == len(URIArray) - 1:
                                break
                            a += 100
                            b += 100
                            if b > len(URIArray) - 1:
                                b = len(URIArray) - 1

                    else:
                        data = {"uris": URIArray}
                        requests.post(
                            addItemsToPlaylistEndpoint, headers=headers, json=data
                        )

                    flash(
                        "Artist's music has been succesfully added to a new playlist.",
                        category="success",
                    )
                    return redirect("/add-all")

            if request.form["addToPlaylistSelect"] == "existingPlaylist":

                # print(request.form)

                userPlaylistID = request.form["userPlaylistID"]

                requestDict = request.form.to_dict()
                del requestDict["addToPlaylistSelect"]
                del requestDict["newPlaylistName"]
                del requestDict["userPlaylistID"]

                limit = 50

                params = {
                    "include_groups": "album,single",
                    "limit": limit,
                }

                artistAlbumIDsAndDates = []

                endpoint = (
                    "https://api.spotify.com/v1/artists/"
                    + list(requestDict.values())[0]
                    + "/albums"
                )

                r = requests.get(endpoint, params=params, headers=headers)

                while True:

                    for i in range(len(r.json()["items"])):
                        artistAlbumIDsAndDates.append(
                            (
                                r.json()["items"][i]["id"],
                                r.json()["items"][i]["release_date"],
                            )
                        )

                    if (r.json()["next"]) == None:
                        break
                    r = requests.get(r.json()["next"], headers=headers)

                artistAlbumIDsAndDates.sort(reverse=True, key=lambda x: x[1])

                URIArray = []

                params = {"limit": 50}

                for albumIDAndDate in artistAlbumIDsAndDates:
                    getAlbumTracksEndpoint = (
                        "https://api.spotify.com/v1/albums/{}/tracks".format(
                            albumIDAndDate[0]
                        )
                    )
                    r = requests.get(
                        getAlbumTracksEndpoint, headers=headers, params=params
                    )
                    for i in range(len(r.json()["items"])):
                        URIArray.append(r.json()["items"][i]["uri"])

                # print(URIArray)
                # print(len(URIArray))

                addItemsToPlaylistEndpoint = (
                    "https://api.spotify.com/v1/playlists/{}/tracks".format(
                        userPlaylistID
                    )
                )

                data = {"uris": URIArray}

                a = 0
                b = 99
                URITempArray = []
                if len(URIArray) > 100:
                    while True:
                        if a == b:
                            URITempArray = URIArray[a]
                        else:
                            URITempArray = URIArray[a:b]
                        data = {"uris": URITempArray}
                        requests.post(
                            addItemsToPlaylistEndpoint, headers=headers, json=data
                        )
                        if b == len(URIArray) - 1:
                            break
                        a += 100
                        b += 100
                        if b > len(URIArray) - 1:
                            b = len(URIArray) - 1

                else:
                    data = {"uris": URIArray}
                    requests.post(
                        addItemsToPlaylistEndpoint, headers=headers, json=data
                    )

                flash(
                    "Artist's music has been succesfully added to existing playlist.",
                    category="success",
                )
                return redirect("/add-all")


@track_blueprint.route("/shutdown", methods=["GET"])
def shutdown():
    func = request.environ.get("werkzeug.server.shutdown")
    print(func)
    func()
    return "Server is shutting down..."
