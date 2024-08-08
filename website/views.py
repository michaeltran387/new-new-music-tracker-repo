from flask import Blueprint, render_template
from flask_login import login_remembered, current_user
from .models import *
import requests

# from .models import *

views = Blueprint("views", __name__)


@views.route("/")
def home():

    return render_template("index.html")
