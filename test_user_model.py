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
        db.drop_all()
        db.create_all()

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u1 = User.signup("testuser1", "test1@test.com", "password", None)
        uid1 = 1111
        u1.id = uid1

        u2 = User.signup("testuser2", "test2@test.com", "password", None)
        uid2 = 2222
        u2.id = uid2

        db.session.commit()

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        """Clean up fouled transactions."""

        # db.session.rollback()
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        # User should have no messages & no followers
        self.assertEqual(len(self.u1.messages), 0)
        self.assertEqual(len(self.u1.followers), 0)

    def test_repr(self):
        """Does __repr__ respond properly?"""


        self.assertEqual(repr(self.u1), "<User #1111: testuser1, test1@test.com>")
        self.assertEqual(repr(self.u2), "<User #2222: testuser2, test2@test.com>")

