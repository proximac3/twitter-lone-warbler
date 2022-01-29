import os
from unittest import TestCase
from models import User, Message, Follows, db
from flask import session

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

class UsersTestCase(TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG_TB_HOST'] = ['dont-show-debug-toolbar']
        app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

        #clear database tables
        User.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        #create Test users
        self.testUser = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser33",
                                    image_url=None)
        db.session.commit()

        self.testUser3 = User.signup(username="testuser3",
                                    email="test3@test.com",
                                    password="testuser222",
                                    image_url=None)
        db.session.commit()

        #set up following demo
        follow = Follows(user_being_followed_id=self.testUser3.id, user_following_id=self.testUser.id)
        db.session.add(follow)
        db.session.commit()


    def test_home_page(self):
        """Test home/signup page"""
        with app.test_client() as client:

            response = client.get('/')
            html = response.get_data(as_text=True)
            
            #test Response Code 
            self.assertEqual(response.status_code, 200)
            #test html text
            self.assertIn(' <p>Sign up now to get your own personalized timeline!</p>', html)


    def test_user_login_get(self):
        """Test /login view function (GET)"""

        with app.test_client() as client:

            response = client.get('/login')
            html = response.get_data(as_text=True)

            #test response code
            self.assertEqual(response.status_code, 200)
            #test html text
            self.assertIn('<h2 class="join-message">Welcome back.</h2>', html)


    def test_user_login_post(self):
        """Test /login(authenticate) view function (POST)"""

        with self.client as c:
            response = c.post('/login', follow_redirects = True, data={'username': 'testuser2', 'password': 'testuser33'})

            html = response.get_data(as_text=True)

            #test response code
            self.assertEqual(response.status_code, 200)

            # Test html content
            self.assertIn('<p class="small">Messages</p>', html)
            self.assertIn('<p class="small">Following</p>', html)
            self.assertIn('<p class="small">Followers</p>', html)
            self.assertIn('<li><a href="/logout">Log out</a></li>', html)

            # test sessions data
            self.assertEqual(session[CURR_USER_KEY], self.testUser.id)
    


    def test_signup(self):
        """test /signup view function"""

        with app.test_client() as client:

            response = client.post('/signup', follow_redirects = True, data={'username': 'test3', 'password': 'Test0000!', 'email': 'test3@gmail.com', 'image_url': ' https://randomuser.me/api/portraits/men/56.jpg '})

            html = response.get_data(as_text=True)

            #Test status code 
            self.assertEqual(response.status_code, 200)

            #test html content
            self.assertIn('<p class="small">Followers</p>', html)
            self.assertIn('<li><a href="/logout">Log out</a></li>', html)

    def test_user(self):
        """Test /users/<int:user_id> view function"""

        with app.test_client() as client:
            #put user in session to persist during session
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testUser.id
        
            response = client.get(f'/users/{self.testUser.id}')
            html = response.get_data(as_text=True)

            #test Status code 
            self.assertEqual(response.status_code, 200)
            #test html content
            self.assertIn('<p class="small">Likes</p>', html)
            self.assertIn('<button class="btn btn-outline-danger ml-2">Delete Profile</button>', html)
    


    def test_user_following(self):
        """Test /users/<int:user_id>/following"""

        with app.test_client() as client:
            #put user in session to persist during session
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testUser.id

            response = client.get(f'/users/{self.testUser.id}/following')
            html = response.get_data(as_text=True)

            #test status code
            self.assertEqual(response.status_code, 200)
            #test html content
            self.assertIn('<button class="btn btn-primary btn-sm">Unfollow</button>', html)
    

    def test_user_following_logedout(self):
        """Test /users/<int:user_id>/following. If logged out can user view users following"""

        with app.test_client() as client:
            
            response = client.get(f'/users/{self.testUser.id}/following')
            html = response.get_data(as_text=True)

            #test status code
            self.assertEqual(response.status_code, 302)
            #test html content
            self.assertIn('</h1>\n<p>You should be redirected automatically to target URL: <a href="/">/</a>.', html)


    #come back and finish this test
    def test_user_follow(self):
        """Test /users/stop-following/<int:follow_id> view function"""

        with app.test_client() as client:
            #put user in session to persist during session
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testUser.id

            # response = client.post(f'/users/stop-following/{self.testUser3.id}', 
            # follow_redirects = True)
            
            # self.assertEqual(response.status_code, 200)

    def test_update_user_profile_form(self):
        """Test update form: /users/<int:user_id>/profile (GET)"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testUser.id

            response = client.get(f'/users/{self.testUser.id}/profile')
            html = response.get_data(as_text=True)

            #test response code
            self.assertEqual(response.status_code, 200)
            self.assertIn('<p>To confirm changes, enter your password:</p>', html)

    def test_update_profile(self):
        """Test update user view /users/<int:user_id>/profile (POST)"""

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testUser.id

            response = client.post(f'/users/{self.testUser.id}/profile', follow_redirects = True, 
            data={
                'username': 'updated user', 
                'image_url': f'{self.testUser.image_url}', 
                'header_image_url': f'{self.testUser.header_image_url}', 
                'bio': f'{self.testUser.bio}',
                'location': f'{self.testUser.location}',
                'password': 'testuser33'
            })

            html = response.get_data(as_text=True)

            #test
            self.assertEqual(response.status_code, 200)
            self.assertIn(f'<h4 id="sidebar-username">@updated user</h4>', html)

    def test_delete_user(self):
        """Test /users/delete (POST)"""
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testUser.id
            
        response = client.post('/users/delete', follow_redirects=True)
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('<button class="btn btn-primary btn-lg btn-block">Sign me up!</button>', html)
                
            
            





            
           





























