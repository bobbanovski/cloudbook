from flask import Blueprint, render_template
from user.forms import RegisterForm

user_app = Blueprint('user_app', __name__) #name of app

#use name of application for decorator
@user_app.route('/login')
def login():
    return "User Login"
    
@user_app.route('/register', methods=('GET','POST'))
def register():
    form = RegisterForm()
    return render_template('user/register.html', form=form)