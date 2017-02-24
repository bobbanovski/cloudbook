from application import create_app as create_app_base
from mongoengine.connection import _get_db
import unittest
from flask import session

from user.models import User

class UserTest(unittest.TestCase):
    def create_app(self):
        self.db_name = 'cloudbook_test'
        return create_app_base(
            MONGODB_SETTINGS={'DB': self.db_name},
            TESTING = True,
            WTF_CSRF_ENABLED = False,
            SECRET_KEY = 's\xce\xabB|\x10\xae\x0c\x87\xe2\xff(2(\xa8\x1a_\x8a\x16r\xa81\xc3\n'
            )

    def setUp(self):
        self.app_factory = self.create_app()
        self.app = self.app_factory.test_client() # allows test module to handle requests
    
    def tearDown(self):
        db = _get_db()
        #db.client.drop_database(db)
        db.connection.drop_database(db)
        
    def user_dict(self):
        return dict(
            first_name = "Robert",
            last_name = "Coleman",
            username = "jimmy",
            email = "special@demo.demo",
            password = "dddd",
            confirm = "dddd"
            )
        
    def test_register_user(self):
        #basic registration
        rv = self.app.post('/register', data=self.user_dict(), follow_redirects = True)
            
        assert User.objects.filter(username="jimmy").count() == 1
        
    def test_login_user(self):
        #create user
        self.app.post('/register', data=self.user_dict())
        #login user
        rv = self.app.post('/login', data=dict(
            username=self.user_dict()['username'],
            password=self.user_dict()['password']
            ))
        #check the session is set correctly
        with self.app as c: #for assertions that require a running application
            rv = c.get('/')
            assert session.get('username') == self.user_dict()['username'] # this indent is detrimental
        
        
