import os
import signal
import subprocess
import sys
import time
from website.models import *
from website import create_app
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_login import current_user
import requests
import datetime
import base64

app = create_app()

process = subprocess.Popen("flask run")
time.sleep(5)

uris = []

if process.poll() is None:
    with app.app_context():
        tagList = (
            db.session.execute(db.select(UserTags).where(UserTags.auto_update == True))
            .scalars()
            .all()
        )
        for tag in tagList:
            access_token = (
                db.session.execute(
                    db.select(AccessToken.access_token).where(
                        AccessToken.user_id == tag.user_id
                    )
                )
                .scalars()
                .all()[0]
            )
            headers = {"Authorization": "Bearer " + access_token}
            artistList = (
                db.session.execute(
                    db.select(AddedArtists).where(AddedArtists.tag_id == tag.id)
                )
                .scalars()
                .all()
            )
            for artist in artistList:
                params = {"include_groups": "album,single"}
                r = requests.get(
                    "https://api.spotify.com/v1/artists/"
                    + artist.artist_id
                    + "/albums",
                    params=params,
                    headers=headers,
                )
                if r.status_code == 401:
                    refresh_token = db.session.execute(
                        db.select(AccessToken.refresh_token).where(
                            AccessToken.user_id == tag.user_id
                        )
                    )
                    body = {
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                    }
                    authorization = str(
                        base64.b64encode(
                            b"b2817ab1a6a6471dae92088510ed25f1:d4fad7b2dbac4eca9c558e39c584a6d0"
                        ).decode()
                    )

                    headersAuth = {
                        "Authorization": "Basic " + authorization,
                        "Content-Type": "application/x-www-form-urlencoded",
                    }

                    r = requests.post(
                        "https://accounts.spotify.com/api/token",
                        headers=headersAuth,
                        data=body,
                    )
                    access_token_object = (
                        db.session.execute(
                            db.select(AccessToken).where(
                                AccessToken.user_id == tag.user_id
                            )
                        )
                        .scalars()
                        .all()[0]
                    )
                    access_token_object.access_token = r.json()["access_token"]
                    db.session.commit()

                    r = requests.get(
                        "https://api.spotify.com/v1/artists/"
                        + artist.artist_id
                        + "/albums",
                        params=params,
                        headers=headers,
                    )
                    access_token = (
                        db.session.execute(
                            db.select(AccessToken.access_token).where(
                                AccessToken.user_id == tag.user_id
                            )
                        )
                        .scalars()
                        .all()[0]
                    )
                    headers = {"Authorization": "Bearer " + access_token}
                    print(r.json())
                    os.kill(os.getpid(), signal.SIGINT)
                rdict = r.json()
                for item in range(len(rdict["items"])):
                    print(rdict["items"][item]["release_date"])
                    release_date = rdict["items"][item]["release_date"]
                    print(len(rdict["items"][item]["release_date"]) == 4)
                    if len(rdict["items"][item]["release_date"]) == 4:
                        release_date = datetime.datetime(int(release_date[0:4]), 1, 1)
                    else:
                        release_date = datetime.datetime(
                            int(release_date[0:4]),
                            int(release_date[5:7]),
                            int(release_date[8:]),
                        )
                    if tag.auto_update_date_last_checked < release_date:
                        # if True:
                        albumID = rdict["items"][item]["id"]
                        r = requests.get(
                            "https://api.spotify.com/v1/albums/{}/tracks".format(
                                albumID
                            ),
                            headers=headers,
                        )
                        for item in range(len(r.json()["items"])):
                            uris.append(r.json()["items"][item]["uri"])

            URITempArray = []
            a = 0
            b = 99
            if len(uris) > 100:
                while True:
                    if a == b:
                        URITempArray = uris[a]
                    else:
                        URITempArray = uris[a:b]
                    data = {"uris": URITempArray}
                    r = requests.post(
                        "https://api.spotify.com/v1/playlists/{}/tracks".format(
                            tag.auto_update_playlist_id
                        ),
                        headers=headers,
                        json=data,
                    )
                    if b == len(uris) - 1:
                        break
                    a += 100
                    b += 100
                    if b > len(uris) - 1:
                        b = len(uris) - 1
                print("check it")

            else:
                data = {"uris": uris}
                r = requests.post(
                    "https://api.spotify.com/v1/playlists/{}/tracks".format(
                        tag.auto_update_playlist_id
                    ),
                    headers=headers,
                    json=data,
                )
                print("check it")
            tag.auto_update_date_last_checked = datetime.datetime.now()
            db.session.commit()


os.kill(os.getpid(), signal.SIGINT)

# x = datetime.datetime(1, 1, 1)
# y = datetime.datetime(2, 1, 1)
# z = datetime.datetime.now()
# print(x)
# print(y)
# print(x < y)
# print(z)

# go through the tags and see which auto update is set to true
# if it's true then you go to the associated artists' music in the spotify api
# and then you're like ok do you have new music
# so to identify the new music there's gonna be a permanent variable about this is the last time I checked
# and it's like ok so you're searching all the music until you hit the music for the last time you checked
# i think it makes more sense to just start from the time they said to track it
