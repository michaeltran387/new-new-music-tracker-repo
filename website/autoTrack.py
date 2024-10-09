import os
import signal
import subprocess
import sys

print(os.getcwd())
print(os.chdir(".."))
print(os.getcwd())

# os.system("flask run")
subprocess.Popen()

# print(os.getpid())
# os.kill(os.getpid(), signal.SIGINT)


# result = (
#     db.session.execute(db.select(UserTags).where(UserTags.auto_update == True))
#     .scalars()
#     .all()
# )
# print(result)

# go through the tags and see which auto update is set to true
# if it's true then you go to the associated artists' music in the spotify api
# and then you're like ok do you have new music
# so to identify the new music there's gonna be a permanent variable about this is the last time I checked
# and it's like ok so you're searching all the music until you hit the music for the last time you checked
# i think it makes more sense to just start from the time they said to track it
