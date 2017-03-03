from functools import wraps
from flask import session, request, url_for, redirect

#Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username') is None:
            return redirect(url_for('user_app.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function