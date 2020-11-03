import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes 

os.environ['DATABASE_URL'] = 'postgresql:///warbler-test'

from app import app

db.create_all()

class UserModelTestCase(TestCase):

    def setUp(self):
        db.drop_all()
        db.create_all()

        self.uid = 123456
        u = User.signup("testuser", "test@test.com", "password", None)
        u.id = self.uid
        db.session.commit()

        self.u = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message(self):

        m = Message(
            text="a test message",
            user_id=self.uid
        )

        db.session.add(m)
        db.session.commit()

        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(self.u.messages[0].text, "a test message")

    def test_message_likes(self):
        m1 = Message(
            text='to be liked',
            user_id=self.uid
        )
        
        u = User.signup("anothertestuser", "atu@test.com", 'password', None)
        uid = 9876543
        u.id = uid
        db.session.add_all([m1, u])
        db.session.commit()

        u.likes.append(m1)

        db.session.commit()

        testlike = Likes.query.filter(Likes.user_id == uid).all()
        self.assertEqual(len(testlike), 1)
        self.assertEqual(testlike[0].message_id, m1.id)
