import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows
from bs4 import BeautifulSoup

os.environ['DATABASE_URL'] = "postgresql://warbler-test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewsTestCase(TestCase):

    def setUp(self):

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="password",
                                    image_url=None)
        self.testuser_id = 12345
        self.testuser.id = self.testuser_id

        self.u1 = User.signup('abc', 'user1@test.com', 'password', None)
        self.u1_id = 23456
        self.u1.id = self.u1_id
        self.u2 = User.signup('def', 'user2@test.com', 'password', None)
        self.u2_id = 34567
        self.u2.id = self.u2_id
        self.u3 = User.signup('ghi', 'user3@test.com', 'password', None)
        self.u3_id = 45678
        self.u3.id = self.u3_id
        self.u4 = User.signup('jkl', 'user4@test.com', 'password', None)
        self.u4_id = 56789
        self.u4.id = self.u4_id

        db.session.commit()

        def tearDown(self):
            resp = super().tearDown()
            db.session.rollback()
            return resp

        def test_users(self):
            with self.client as c:
                resp = c.get("/users")

                self.assertIn("@testuser", str(resp.data))
                self.assertIn("@abc", str(resp.data))
                self.assertIn("@def", str(resp.data))
                self.assertIn("@ghi", str(resp.data))
                self.assertIn("@jkl", str(resp.data))
        
        def test_users_search(self):
            with self.client as c:
                resp = c.get("/users?q=test")

                self.assertIn("@testuser", str(resp.data))

                self.assertNotIn("@abc", str(resp.data))
                self.assertNotIn("@def", str(resp.data))
                self.assertNotIn("@ghi", str(resp.data))
                self.assertNotIn("@jkl", str(resp.data))