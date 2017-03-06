from flask import Blueprint, abort, session, url_for, redirect, render_template

from user.models import User
from user.decorators import login_required
from relationship.models import Relationship

relationship_app = Blueprint('relationship_app', __name__)

@relationship_app.route('/add_friend/<to_username>')
@login_required
def add_friend(to_username):
    logged_user = User.objects.filter(username = session.get('username')).first()
    to_user = User.objects.filter(username = to_username).first() 
    if to_user:
        to_username = to_user.username
        rel = Relationship.get_relationship(logged_user, to_user)
        if rel == "FRIENDS_PENDING":
            return rel
        elif rel == "BLOCKED" :
            return rel
        elif rel == "FRIENDS_APPROVED":
            return rel
        elif rel == "REVERSE_FRIENDS_PENDING": #Friend has approved
            Relationship(
                from_user = logged_user,
                to_user = to_user,
                rel_type = Relationship.FRIENDS,
                status = Relationship.APPROVED
                ).save()
            reverse_rel = Relationship.objects.get(
                from_user = to_user,
                to_user = logged_user
                )
            reverse_rel.status = Relationship.APPROVED
            reverse_rel.save()
            #return "FRIENDS_APPROVED"
        elif rel == None and rel != "REVERSE_BLOCKED": #notFriend, notBlocked
            Relationship(
                from_user = logged_user,
                to_user = to_user,
                rel_type = Relationship.FRIENDS,
                status = Relationship.PENDING
                ).save()
            return "FRIENDSHIP_REQUESTED"
        return redirect(url_for('user_app.profile', username=to_username))
    else:
        abort(404)
            
@relationship_app.route('/UnFriend/<to_username>')
@login_required
def UnFriend(to_username):
    logged_user = User.objects.filter(username = session.get('username')).first()
    to_user = User.objects.filter(username = to_username).first() 
    if to_user:
        rel = Relationship.get_relationship(logged_user, to_user)
        if rel == "FRIENDS_PENDING" or rel == "FRIENDS_APPROVED" or rel == "REVERSE_FRIENDS_PENDING":
            rel = Relationship.objects.filter(
                from_user = logged_user,
                to_user = to_user).delete()
            reverse_rel = Relationship.objects.filter(
                from_user = to_user,
                to_user = logged_user).delete()
            return redirect(url_for('user_app.profile', username = to_username))
    else:
        abort(404)
        
@relationship_app.route('/Block/<to_username>')
@login_required
def Block(to_username):
    logged_user = User.objects.filter(username = session.get('username')).first()
    to_user = User.objects.filter(username = to_username).first() 
    if to_user:
        rel = Relationship.get_relationship(logged_user, to_user)
        if rel == "FRIENDS_PENDING" or rel == "FRIENDS_APPROVED" or rel == "REVERSE_FRIENDS_PENDING":
            rel = Relationship.objects.filter(
                from_user = logged_user,
                to_user = to_user
                ).delete()
            reverse_rel = Relationship.objects.filter(
                from_user = to_user,
                to_user = logged_user).delete()
        Relationship(
            from_user = logged_user,
            to_user = to_user,
            rel_type = Relationship.BLOCKED,
            status = Relationship.APPROVED
            ).save()
        return redirect(url_for('user_app.profile', username = to_username))
    else:
        abort(404)
        
@relationship_app.route('/Unblock/<to_username>')
@login_required
def Unblock(to_username):
    logged_user = User.objects.filter(username = session.get('username')).first()
    to_user = User.objects.filter(username = to_username).first() 
    if to_user:
        rel = Relationship.get_relationship(logged_user, to_user)
        
        if rel == "BLOCKED":
            rel = Relationship.objects.filter(
                from_user = logged_user,
                to_user = to_user
                ).delete()
        return redirect(url_for('user_app.profile', username = to_username))
    else:
        abort(404)