
#Application Factory Method
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('settings.py') #get application settings from file settings.py
    
    from user.views import user_app
    
    #register blueprints
    app.register_blueprint(user_app)
    
    return app