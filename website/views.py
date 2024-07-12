from flask import Blueprint, render_template
from flask_login import login_remembered, current_user
from .models import *

# from .models import *

views = Blueprint("views", __name__)


@views.route("/")
def home():
    # print(current_user)
    # print(current_user.username)
    return render_template("index.html")
