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
        
        #Test confirmation email
        user = User.objects.get(username=self.user_dict()['username'])
        code = user.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + user.username + '/' + code)
        assert "Thank You! Your registration is now complete" in str(rv.data)
        
        #Test again - should be 404
        rv = self.app.get('/confirm/' + user.username + '/' + code)
        assert rv.status_code == 404
        
        #Check that change configuration is empty
        user = User.objects.get(username=self.user_dict()['username'])
        assert user.change_configuration == {}
        
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
        
        #confirm the user
        user = User.objects.get(username = self.user_dict()['username'])
        code = user.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + user.username + '/' + code)
        
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
        #user['email'] = "TestEmail@demo.demo"
        
        # Edit the user
        rv = self.app.post('/edit', data=user)
        assert "Profile updated" in str(rv.data)
        edited_user = User.objects.first()
        assert edited_user.first_name == "TestFirstName"
        assert edited_user.last_name == "TestLastName"
        assert edited_user.username == "testusername"
        #assert edited_user.email == "testemail@demo.demo"
        
        #Check that new email is in change configuration
        user['email'] = 'numail@example.com'
        rv = self.app.post('/edit', data=user)
        #assert 'You will need to confirm the new email, by clicking on the link sent to your email' in str(rv.data)
        db_user = User.objects.first() #Retrieve most recently made user fromn the database
        code = db_user.change_configuration.get('confirmation_code')
        new_email = db_user.change_configuration.get('new_email')
        assert new_email == user['email']
        
        #confirm that user clicks on the email link, the new email is saved to database, change_configuration is dumped
        rv = self.app.get('/confirm/' + db_user.username + '/' + code)
        db_user = User.objects.first()
        assert db_user.email == user['email']
        assert db_user.change_configuration == {}
        
        #Create a second user
        self.app.post('/register', data=self.user_dict())
        #login with this user
        rv = self.app.post('/login', data=dict(
            username = self.user_dict()['username'],
            password = self.user_dict()['password']
            ))
        rv = self.app.get('/' + self.user_dict()['username']) #access profile page
        assert "Edit Profile" in str(rv.data)
        # try to duplicate email
        # Edit fields
        user = self.user_dict()
        user['email'] = "TestEmail@demo.demo"
        rv = self.app.post('/edit', data=user)
        #assert "This email already exists" in str(rv.data)
        
        # duplicate username
        user = self.user_dict()
        user['username'] = "TestUsername"
        rv = self.app.post('/edit', data=user)
        assert "Username already taken" in str(rv.data)
        
    def test_get_profile(self):
        #create user
        self.app.post('/register', data=self.user_dict())
        rv = self.app.get('/' + self.user_dict()['username'])
        assert self.user_dict()['username'] in str(rv.data)
        
    def test_forgot_password(self):
        #create user
        self.app.post('/register', data=self.user_dict())
        #confirm user
        #confirm the user
        user = User.objects.get(username = self.user_dict()['username'])
        code = user.change_configuration.get('confirmation_code')
        rv = self.app.get('/confirm/' + user.username + '/' + code)
        
        #Enter userforgot email
        rv = self.app.post('/forgot', data=dict(email=self.user_dict().get('email')))
        user = User.objects.first()
        password_reset_code = user.change_configuration.get('password_reset_code')
        
        assert password_reset_code is not None
        
        #Wrong username
        rv = self.app.get('/password_reset/not_here' + password_reset_code)
        assert rv.status_code == 404
        
        #Wrong password
        rv = self.app.post('/password_reset/' + self.user_dict().get('username') + '/baddPassword')
        assert rv.status_code == 404
        
        #Correct username and password
        rv = self.app.post('/password_reset/' + self.user_dict().get('username') + '/' + password_reset_code,
        data=dict(password = 'newPassword', confirm = 'newPassword'), follow_redirects = True)
        assert "Your password has been successfully updated" in str(rv.data)
        user = User.objects.first()
        assert user.change_configuration == {}
        
        #try logging in with new password
        rv = self.app.post('/login', data=dict(
            username = self.user_dict()['username'],
            password = 'newPassword'
            ))
        
        with self.app as c:
            rv = c.get('/')
            assert session.get('username') == self.user_dict()['username']
            
