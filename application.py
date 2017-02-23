
#Application Factory Method
from flask import Flask
from flask.ext.mongoengine import MongoEngine

db = MongoEngine() # Create instance of Mongo Engine

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('settings.py') #get application settings from file settings.py
    
    db.init_app(app)
    
    from user.views import user_app
    
    #register blueprints
    app.register_blueprint(user_app)
    
    return app