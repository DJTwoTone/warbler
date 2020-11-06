# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows
from bs4 import BeautifulSoup

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

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

    def test_user_exists(self):
        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@testuser", str(resp.data))

    def setup_likes(self):
        mess1 = Message(id=1234, text="important stuff", user_id=self.testuser_id)
        mess2 = Message(id=2345, text="listen to me", user_id=self.testuser_id)
        mess3 = Message(id=3456, text="blah, blah, blah", user_id=self.u1_id)

        db.session.add_all([mess1,mess2,mess3])
        db.session.commit()

        like1 = Likes(user_id=self.testuser_id, message_id=3456)

        db.session.add(like1)
        db.session.commit()

    def test_user_with_likes(self):
        self.setup_likes()

        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@testuser", str(resp.data))
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all("li", {"class": "stat"})
            self.assertEqual(len(found), 4)

            self.assertIn("2", found[0].text)

            self.assertIn("0", found[1].text)

            self.assertIn("0", found[2].text)

            self.assertIn("1", found[3].text)

    def test_add_likes(self):
        m = Message(id=4567, text="kill your tv", user_id=self.u1_id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post("users/warble_liking/4567", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            likes = Likes.query.filter(Likes.message_id == 4567).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.testuser_id)

    def test_remove_likes(self):
        self.setup_likes()

        m = Message.query.filter(Message.text == "blah, blah, blah").one()
        
        self.assertIsNotNone(m)
        self.assertNotEqual(m.user_id, self.testuser_id)

        l = Likes.query.filter(
            Likes.user_id==self.testuser_id and Likes.message_id==m.id
        ).one()


        self.assertIsNotNone(l)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post(f"/users/warble_liking/{m.id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            likes = Likes.query.filter(Likes.message_id==m.id).all()

            self.assertEqual(len(likes), 0)

    def test_unauthorized_likes(self):
        self.setup_likes()

        m = Message.query.filter(Message.text=="important stuff").one()
        self.assertIsNotNone(m)

        like_count = Likes.query.count()

        with self.client as c:
            resp = c.post(f"/users/warble_liking/{m.id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            self.assertIn("Access unauthorized.", str(resp.data))

            self.assertEqual(like_count, Likes.query.count())

    def setup_followers(self):
        f1 = Follows(user_being_followed_id=self.u1_id, user_following_id=self.testuser_id)
        f2 = Follows(user_being_followed_id=self.u2_id, user_following_id=self.testuser_id)
        f3 = Follows(user_being_followed_id=self.testuser_id, user_following_id=self.u1_id)

        db.session.add_all([f1,f2,f3])
        db.session.commit()

    def test_user_with_follows(self):
        self.setup_followers()

        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@testuser", str(resp.data))
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all("li", {"class": "stat"})
            self.assertEqual(len(found), 4)

            self.assertIn("0", found[0].text)
            
            self.assertIn("2", found[1].text)
            
            self.assertIn("1", found[2].text)
            
            self.assertIn("0", found[3].text)

    def test_following(self):
        self.setup_followers()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.testuser_id}/following", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@abc", str(resp.data))
            self.assertIn("@def", str(resp.data))
            self.assertNotIn("@ghi", str(resp.data))
            self.assertNotIn("@jkl", str(resp.data))

    def test_followers(self):
        self.setup_followers()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.testuser_id}/followers")

            self.assertIn("@abc", str(resp.data))
            self.assertNotIn("@def", str(resp.data))
            self.assertNotIn("@ghi", str(resp.data))
            self.assertNotIn("@jkl", str(resp.data))

    def test_unauthorized_following_page_access(self):
        self.setup_followers()

        with self.client as c:

            resp = c.get(f"/users/{self.testuser_id}/following", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("@abc", str(resp.data))
            self.assertIn("Access unauthorized", str(resp.data))


    def test_unauthorized_followers_page_access(self):
        self.setup_followers()

        with self.client as c:

            resp = c.get(f"/users/{self.testuser_id}/followers", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("@abc", str(resp.data))
            self.assertIn("Access unauthorized.", str(resp.data))