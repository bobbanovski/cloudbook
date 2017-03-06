
#Application Factory Method
from flask import Flask
from flask.ext.mongoengine import MongoEngine

db = MongoEngine() # Create instance of Mongo Engine

def create_app(**config_overrides): #** allows unit tester to override
    app = Flask(__name__)
    
    app.config.from_pyfile('settings.py') #get application settings from file settings.py
    #Need to override this for unit testing
    app.config.update(config_overrides)
    
    db.init_app(app)
    
    from user.views import user_app
    from relationship.views import relationship_app
    from home.views import home_app
    
    #register blueprints
    app.register_blueprint(user_app)
    app.register_blueprint(relationship_app)
    app.register_blueprint(home_app)
    return app