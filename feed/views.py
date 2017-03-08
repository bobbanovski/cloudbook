from flask import Blueprint, request, session, redirect
from user.decorators import login_required
from user.models import User

from feed.models import Message, Feed
# from feed.process import process_message


feed_app = Blueprint('feed_app', __name__)

@feed_app.route('/message/add', methods=('GET', 'POST'))
@login_required
def add_message():
    return "add message"