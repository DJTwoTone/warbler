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

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        user1 = User(
                email="test@test.com",
                username="testuser1",
                password="HASHED_PASSWORD",
                )

        user2 = User(
                email="test2@test.com",
                username="testuser2",
                password="HASHED_PASSWORD",
                )

        # user1 = User(USER_DATA)
        # user2 = User(USER_DATA_2)
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        user1 = User.query.get('testuser1')
        user2 = User.query.get('testuser2')

        # User should have no messages & no followers
        self.assertEqual(len(user1.messages), 0)
        self.assertEqual(len(user1.followers), 0)

    # def test_repr(self):
    #     """Does __repr__ respond properly?"""

    #     u = User(
    #         email="test@test.com",
    #         username="testuser",
    #         password="HASHED_PASSWORD"
    #     )

    #     db.session.add(u)
    #     db.session.commit()

    #     self.assertEqual(repr(u), "<User #1: testuser, test@test.com>")

