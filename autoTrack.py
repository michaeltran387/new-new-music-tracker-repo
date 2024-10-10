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

import datetime

app = create_app()

process = subprocess.Popen("flask run")
time.sleep(5)

if process.poll() is None:
    with app.app_context():
        # result = (
        #     db.session.execute(db.select(UserTags).where(UserTags.auto_update == True))
        #     .scalars()
        #     .all()
        # )
        # print(result)
        print(current_user)
        print(current_user.id)

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
