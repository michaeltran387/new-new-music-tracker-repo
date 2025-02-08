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

        # result = (
        #     db.session.execute(db.select(UserTags).where(UserTags.tag == "?General 3"))
        #     .scalars()
        #     .all()
        # )[0]
        # result.auto_update_date_last_checked = datetime.datetime(1900, 1, 1)
        # db.session.commit()

        for tag in tagList:
            uris = []
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
                limit = 5
                params = {"include_groups": "album,single", "limit": limit}
                r = requests.get(
                    "https://api.spotify.com/v1/artists/"
                    + artist.artist_id
                    + "/albums",
                    params=params,
                    headers=headers,
                )

                if r.status_code == 401:
                    print(r.json())
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
                    r = requests.get(
                        "https://api.spotify.com/v1/artists/"
                        + artist.artist_id
                        + "/albums",
                        params=params,
                        headers=headers,
                    )
                    print("access token updated")

                while True:
                    counter = 0
                    release_date = ""
                    limit = 5

                    if len(r.json()["items"]) < limit:
                        limit = len(r.json()["items"])

                    print(artist.name)
                    for item in range(limit):
                        release_date = r.json()["items"][item]["release_date"]
                        if len(r.json()["items"][item]["release_date"]) == 4:
                            release_date = datetime.datetime(
                                int(release_date[0:4]), 1, 1
                            )
                        else:
                            release_date = datetime.datetime(
                                int(release_date[0:4]),
                                int(release_date[5:7]),
                                int(release_date[8:]),
                            )

                        if tag.auto_update_date_last_checked < release_date:

                            albumID = r.json()["items"][item]["id"]
                            r2 = requests.get(
                                "https://api.spotify.com/v1/albums/{}/tracks".format(
                                    albumID
                                ),
                                headers=headers,
                                params={"limit": "50"},
                            )
                            for item in range(len(r2.json()["items"])):
                                uris.append(r2.json()["items"][item]["uri"])

                        if counter == limit - 1:
                            break
                        if tag.auto_update_date_last_checked < release_date:
                            counter += 1
                            continue
                        else:
                            break
                    if r.json()["next"] is None:
                        break
                    else:
                        r = requests.get(
                            r.json()["next"],
                            headers=headers,
                        )
                    if tag.auto_update_date_last_checked > release_date:
                        break

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

            else:
                data = {"uris": uris}
                r = requests.post(
                    "https://api.spotify.com/v1/playlists/{}/tracks".format(
                        tag.auto_update_playlist_id
                    ),
                    headers=headers,
                    json=data,
                )

        for tag in tagList:
            tag.auto_update_date_last_checked = datetime.datetime.now()
        db.session.commit()
        print("Finished!")

        os.kill(os.getpid(), signal.SIGINT)
