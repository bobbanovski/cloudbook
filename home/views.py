from flask import Blueprint, session, render_template

from user.models import User

home_app = Blueprint('home_app', __name__)

@home_app.route('/')
def home():
    return render_template('home/home.html')