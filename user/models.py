from mongoengine import signals #for pre_save
from application import db
import os

from utilities.common import utc_now_ts as now
from flask import url_for
from settings import STATIC_IMAGE_URL


class User(db.Document): #create object for Mongo
    username=db.StringField(db_field="u", required = True, unique = True) #dbfield name in Mongo: single letter to save space
    password=db.StringField(db_field="p", required = True)
    email=db.EmailField(db_field="e", required = True, unique = True)
    first_name=db.StringField(db_field="fn", max_length=50)
    last_name=db.StringField(db_field="ln", max_length=50)
    created=db.IntField(db_field="c", default=now())
    bio=db.StringField(db_field="b", max_length=200)
    email_confirmed=db.BooleanField(db_field="ec", default=False)
    change_configuration=db.DictField(db_field="cc")
    profile_image = db.StringField(db_field="i", default=None)
    
    @classmethod  #for pre_save
    def pre_save(cls, sender, document, **kwargs): #always called before database save
        document.username = document.username.lower()
        document.email = document.email.lower()
        
    def profile_imgsrc(self, size):
        return os.path.join(STATIC_IMAGE_URL, 'user', '%s.%s.%s.png' % (self.id, self.profile_image, size))
    
    meta = {
        'indexes': ['username', 'email', '-created'] #create indices to sort the data
    }
    
signals.pre_save.connect(User.pre_save, sender=User)