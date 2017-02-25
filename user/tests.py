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
        assert User.objects.filter(username = self.user_dict()['username']).count() == 1
        #Test for invalid username characters
        user2 = self.user_dict()
        user2['username'] = "James Forney"
        user2['email'] = "muhMail@demo.demo"
        rv = self.app.post('/register', data=user2, follow_redirects = True)
        assert "Must be alphanumeric characters, _ or -, length of 4 to 25" in str(rv.data)
        
        #check if username being saved in lowercase
        user3 = self.user_dict()
        user3['username'] = "MuHUsEr"
        user3['email'] = "real@demo.demo"
        rv = self.app.post('/register', data=user3, follow_redirects = True)
        assert User.objects.filter(username = user3['username'].lower()).count() == 1
        
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
        
    def test_edit_profile(self):
        #create user
        self.app.post('/register', data=self.user_dict())
        #login with this user
        rv = self.app.post('/login', data=dict(
            username = self.user_dict()['username'],
            password = self.user_dict()['password']
            ))
        rv = self.app.get('/' + self.user_dict()['username']) #access profile page
        assert "Edit Profile" in str(rv.data)
        
        # Edit fields
        user = self.user_dict()
        user['first_name'] = "TestFirstName"
        user['last_name'] = "TestLastName"
        user['username'] = "TestUsername"
        user['email'] = "TestEmail@demo.demo"
        
        # Edit the user
        rv = self.app.post('/edit', data=user)
        assert "Profile updated" in str(rv.data)
        edited_user = User.objects.first()
        assert edited_user.first_name == "TestFirstName"
        assert edited_user.last_name == "TestLastName"
        assert edited_user.username == "testusername"
        assert edited_user.email == "testemail@demo.demo"
        
        #Create a second user
        self.app.post('/register', data=self.user_dict())
        #login with this user
        rv = self.app.post('/login', data=dict(
            username = self.user_dict()['username'],
            password = self.user_dict()['password']
            ))
        rv = self.app.get('/' + self.user_dict()['username']) #access profile page
        assert "Edit Profile" in str(rv.data)
        #try to duplicate email
        # Edit fields
        user = self.user_dict()
        user['email'] = "TestEmail@demo.demo"
        rv = self.app.post('/edit', data=user)
        assert "This email already exists" in str(rv.data)
        
        # duplicate username
        user = self.user_dict()
        user['username'] = "TestUsername"
        rv = self.app.post('/edit', data=user)
        assert "Username already taken" in str(rv.data)