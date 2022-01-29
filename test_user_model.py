"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        #create demo user 1 
        self.testUser1 = User(email="testuser1@gmail.com", username="testuser1", password='testUser1!')
        db.session.add(self.testUser1)
        db.session.commit()

        #create demo user 2
        self.testUser2 = User(email="testuser2@gmail.com", username="testuser2222", password='testUser2!')
        db.session.add(self.testUser2)
        db.session.commit()

        #set up following for testing.
        self.follow1 = Follows(user_being_followed_id=self.testUser2.id, user_following_id=self.testUser1.id)
        db.session.add(self.follow1)
        db.session.commit()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_is_Following(self):
        """Test is following instance method"""
        result = self.testUser1.is_following(self.testUser2)

        #test output
        self.assertTrue(result)

    def test_is_following_not(self):
        """Test is following when one user is not followed by other user"""
        result = self.testUser2.is_following(self.testUser1)

        #test
        self.assertFalse(result)

    def test_is_followed_by(self):
        """test if user is followed by other user"""

        result = self.testUser2.is_followed_by(self.testUser1)

        #test
        self.assertTrue(result)

    def test_is_followed_by_not(self):
        """test if user is not followed by other user"""

        result = self.testUser1.is_followed_by(self.testUser2)

        #test
        self.assertFalse(result)

    def test_user_crate(self):
        """Test creating a new user. @Classmethod"""

        result = User.signup(username='testUser666', email='testUser666@gmial.com', password='fakeuserpassword!', image_url='/static/images/default-pic.png')
        db.session.commit()

        #test
        self.assertEqual(User.query.get(result.id).id, result.id)

    def test_user_authenticate(self):
        """Authenticate a user when given correct credentials"""

        #create user
        result = User.signup(username='testUser666', email='testUser666@gmial.com', password='fakeuserpassword!', image_url='/static/images/default-pic.png')
        db.session.commit()

        #authenticate user
        auth = User.authenticate('testUser666', 'fakeuserpassword!')

        #test 
        self.assertIsNot(auth, False)

    def test_user_authenticate_incorrect(self):
        """Authenticate a user when given incorrect credentials"""

        #create user
        result = User.signup(username='testUser666', email='testUser666@gmial.com', password='fakeuserpassword!', image_url='/static/images/default-pic.png')
        db.session.commit()

        #authenticate user
        auth = User.authenticate('testUser666', 'fakeuserpassword!23323')

        #test 
        self.assertIs(auth, False)
        