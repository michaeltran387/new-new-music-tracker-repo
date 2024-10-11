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
            artistList = (
                db.session.execute(
                    db.select(AddedArtists).where(AddedArtists.tag_id == tag.id)
                )
                .scalars()
                .all()
            )
            for artist in artistList:
                access_token = (
                    db.session.execute(
                        db.select(AccessToken.access_token).where(
                            AccessToken.user_id == tag.user_id
                        )
                    )
                    .scalars()
                    .all()[0]
                )
                print(access_token)
                headers = {"Authorization": "Bearer " + access_token}
                params = {"include_groups": "album,single"}
                r = requests.get(
                    "https://api.spotify.com/v1/artists/"
                    + artist.artist_id
                    + "/albums",
                    params=params,
                    headers=headers,
                )
                for item in range(len(r.json()["items"])):
                    release_date = r.json()["items"][item]["release_date"]
                    release_date = datetime.datetime(
                        int(release_date[0:4]),
                        int(release_date[5:7]),
                        int(release_date[8:]),
                    )
                    if tag.auto_update_date_last_checked < release_date:
                        albumID = r.json()["items"][item]["id"]
                        r = requests.get(
                            "https://api.spotify.com/v1/albums/{}/tracks".format(
                                albumID
                            ),
                            headers=headers,
                        )
                        for item in range(len(r.json()["items"])):
                            uris.append(r.json()["items"][item]["uri"])

                        # add the shit

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
