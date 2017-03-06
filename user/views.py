from flask import Blueprint, render_template, request, redirect, session, url_for, abort
import bcrypt
import uuid #unique id using time for setting
import os
from werkzeug import secure_filename

from user.forms import RegisterForm, LoginForm, EditForm, ForgotPasswordForm, PasswordResetForm

from user.models import User
from utilities.common import email
from settings import UPLOAD_FOLDER
from utilities.imaging import thumbnail_process
from relationship.models import Relationship
from user.decorators import login_required

user_app = Blueprint('user_app', __name__) #name of app

#use name of application for decorator
# @user_app.route('/')
# def home():
#     return render_template('/user/home.html')

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
                    #return "User Logged in"
                    return "user logged in"
                return "user logged in"
            else:
                user = None
        if not user:
            error = 'username or password was incorrect'
    return render_template('user/login.html', form=form, error=error)
    
@user_app.route('/logout')
def logout():
    session.pop('username')
    return redirect(url_for('user_app.login'))
    
@user_app.route('/<username>')
def profile(username):
    logged_user = None
    edit_profile = False
    rel = None
    user = User.objects.filter(username=username).first()
    
    if user:
        if session.get('username'):
            # compare relationship between user being looked at and user that is logged in 
            logged_user = User.objects.filter(username=session.get('username')).first()
            rel = Relationship.get_relationship(logged_user, user)
            
        if user.username == session.get('username'): #if user is looking at his own profile page
            edit_profile = True
        #get friends
        friends = Relationship.objects.filter(
            from_user=user,
            rel_type=Relationship.FRIENDS,
            status=Relationship.APPROVED)
        friends_total = friends.count()
        
        return render_template('user/profile.html', user = user, logged_user=logged_user, rel=rel, edit_profile=edit_profile, friends=friends, friends_total=friends_total)
    else:
        abort(404)
    
@user_app.route('/edit', methods=('GET','POST'))
@login_required
def edit():
    error = None
    message = None
    user = User.objects.filter(username=session.get('username')).first()
    if user:
        form = EditForm(obj=user) #pre populates form
        if form.validate_on_submit():
            #Check if image is of correct type
            image_ts = None
            if request.files.get('image'):
                filename = secure_filename(form.image.data.filename)
                file_path = os.path.join(UPLOAD_FOLDER, 'user', filename)
                form.image.data.save(file_path) #save form image under this path
                image_ts = str(thumbnail_process(file_path, 'user', str(user.id)))
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
                if image_ts: #if image was attached to form
                    user.profile_image = image_ts
                user.save()
                if not message: #if user did not edit the email
                    message = "Profile updated"
        return render_template("user/edit.html", form=form, error=error, message=message, user=user)
    else:
        abort(404)
    
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
    
@user_app.route('/password_reset/<username>/<code>', methods=('GET', 'POST'))
def password_reset(username, code):
    message = None
    require_current = None
    
    form = PasswordResetForm()
    
    user = User.objects.filter(username=username).first()
    if not user or code != user.change_configuration.get('password_reset_code'):
        abort(404)
        
    if request.method == 'POST':
        del form.current_password
        if form.validate_on_submit():
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(form.password.data, salt)
            user.password = hashed_password
            user.change_configuration = {}
            user.save()
            
            if session.get('username'):
                session.pop('username')
            return redirect(url_for('user_app.password_reset_complete'))
            
    return render_template('user/password_reset.html',
        form=form,
        message=message,
        require_current=require_current,
        username=username,
        code=code
    )
        
@user_app.route('/password_reset_complete')
def password_reset_complete():
    return render_template('user/password_change_confirmed.html')
    
@user_app.route('/change_password', methods=('GET', 'POST'))
def change_password():
    require_current = True
    error = None
    form = PasswordResetForm()
    user = User.objects.filter(username=session.get('username')).first()
    
    if not user:
        abort(404)
    if request.method == 'POST':
        if form.validate_on_submit:
            if bcrypt.hashpw(form.current_password.data, user.password) == user.password:
                salt = bcrypt.gensalt()
                user.password = bcrypt.hashpw(form.password.data, salt)
                user.save()
                
                #log user out if already logged in
                if session.get('username'):
                    session.pop('username')
                return redirect(url_for('user_app.password_reset_complete'))
            else:
                error = "Incorrect password"
    return render_template('user/password_reset.html', 
        form = form, 
        require_current = require_current, 
        error=error)
                