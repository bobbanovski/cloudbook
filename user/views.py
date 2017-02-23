from flask import Blueprint

user_app = Blueprint('user_app', __name__) #name of app

#use name of application for decorator
@user_app.route('/login')
def login():
    return "User Login"