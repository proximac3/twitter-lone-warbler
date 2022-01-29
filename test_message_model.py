"""Test Message Model"""

import os
from unittest import TestCase
from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
from app import app

db.create_all()

class MessageTestCase(TestCase):
    """Test Message model"""

    def setUp(self):
        """Create test client and messages"""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        #testuser1
        self.client1 = User.signup(username='client1', email='testUser666@gmial.com', password='fakeuserpassword!', image_url='/static/images/default-pic.png')
        db.session.commit()

        self.client2 = User.signup(username='client2', email='testUser666@gmial22.com', password='fakeuserpassword!22', image_url='/static/images/default-pic.png')
        db.session.commit()





