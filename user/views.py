from flask import Blueprint, render_template, request, redirect, session, url_for, abort
import bcrypt
import uuid #unique id using time for setting

from user.forms import RegisterForm, LoginForm, EditForm, ForgotPasswordForm

from user.models import User
from utilities.common import email

user_app = Blueprint('user_app', __name__) #name of app

#use name of application for decorator
@user_app.route('/')
def home():
    return render_template('/user/home.html')

@user_app.route('/register', methods=('GET','POST'))
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        salt = bcrypt.gensalt()
        hashed_password=bcrypt.hashpw(form.password.data, salt)
        code = str(uuid.uuid4())
        user = User(
            username = form.username.data,
            password = hashed_password,
            email = form.email.data,
            first_name = form.first_name.data,
            last_name = form.last_name.data,
            change_configuration = {
                "new_email": form.email.data.lower(),
                "confirmation_code": code
                }
            )
        #email the user
        body_html = render_template('mail/user/register.html', user=user)
        body_text = render_template('mail/user/register.txt', user=user)
        email(user.email, "Welcome to Cloudbook", body_html, body_text)
        user.save()
        return "User Registered"
    return render_template('user/register.html', form=form)
    
@user_app.route('/login', methods=('GET','POST'))
def login():
    form = LoginForm()
    error = None
    
    if request.method == 'GET' and request.args.get('next'):
        session['next'] = request.args.get('next')
        
    if form.validate_on_submit():
        user = User.objects.filter(username=form.username.data).first()
        if user:
            if bcrypt.hashpw(form.password.data, user.password) == user.password: 
                session['username'] = form.username.data
                if 'next' in session:
                    next = session.get('next')
                    session.pop('next')
                    return redirect(next)
                else:
                    return "User Logged in"
                return "User Logged in"
            else:
                user = None
        if not user:
            error = 'username or password was incorrect'
    return render_template('user/login.html', form=form, error=error)
    
@user_app.route('/logout', methods=('GET','POST'))
def logout():
    session.pop('username')
    return redirect(url_for('user_app.login'))
    
@user_app.route('/<username>')
def profile(username):
    edit_profile = False
    user = User.objects.filter(username=username).first()
    if session.get('username') and user.username == session.get('username'): #if user is looking at his own profile page
        edit_profile = True
    if user:
        return render_template('user/profile.html', user = user, edit_profile=edit_profile)
    else:
        abort(404)
    
@user_app.route('/edit', methods=('GET','POST'))
def edit():
    error = None
    message = None
    user = User.objects.filter(username=session.get('username')).first()
    if user:
        form = EditForm(obj=user) #pre populates form
        if form.validate_on_submit():
            if user.username != form.username.data.lower(): # check that user has changed own username
                if User.objects.filter(username=form.username.data.lower()).first(): # check that username not already taken
                    error = "Username already taken"
                else:
                    session['username'] = form.username.data.lower()
                    form.username.data = form.username.data.lower()
            if user.email != form.email.data.lower(): # check that user has changed own email
                if User.objects.filter(email=form.email.data.lower()).first(): # check that email not already taken
                    error = "This email already exists"
                else:
                    code = str(uuid.uuid4())
                    user.change_configuration = {
                        "new_email": form.email.data.lower(),
                        "confirmation_code": code
                        }
                    user.email_confirmed = False
                    form.email.data = user.email
                    message="You will need to confirm the new email, by clicking on the link sent to your email"
                    body_html = render_template('mail/user/change_email.html', user=user)
                    body_text = render_template('mail/user/change_email.txt', user=user)
                    email(user.change_configuration['new_email'], "Please confirm email change", body_html, body_text)
                    user.save()
                    return "User details updated, pending email confirmation"
            if not error:
                form.populate_obj(user) #populate form with user object
                user.save()
                if not message: #if user did not edit the email
                    message = "Profile updated"
        return render_template("user/edit.html", form=form, error=error, message=message)
    else:
        abort(404)
    
@user_app.route('/change_password')
def change_password():
    return "Change Password"
    
@user_app.route('/confirm/<username>/<code>', methods=('GET','POST'))
def confirm(username, code):
    user = User.objects.filter(username = username).first()
    if user and user.change_configuration and user.change_configuration.get('confirmation_code'): 
        if code == user.change_configuration.get('confirmation_code'):
            user.email = user.change_configuration.get('new_email')
            user.change_configuration = {}
            user.email_confirmed = True
            user.save()
            return render_template('user/email_confirmed.html')
    else:
        abort(404)
        
@user_app.route('/forgotPassword', methods=('GET', 'POST'))
def forgotPassword():
    error = None
    message = None
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.objects.filter(email = form.email.data.lower()).first()
        if user:
            code = str(uuid.uuid4())
            user.change_configuration={
                "password_reset_code": code
            }
            user.save()
            
            #Email to user
            body_html = render_template('mail/user/password_reset.html', user=user)
            body_text = render_template('mail/user/password_reset.txt', user=user)
            email(user.email, "Password reset request from Cloudbook", body_html, body_text)
            
        message = "Password reset request has been sent to your email address"
    return render_template('user/forgotPassword.html', form=form, error=error, message=message)