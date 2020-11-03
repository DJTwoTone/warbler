"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

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

        u = User(
            email="test@test.com",
            username="testuser",
            password="password"
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)


    def test_repr(self):
        """Does __repr__ respond properly?"""

        self.assertEqual(repr(self.u1), "<User #1111: testuser1, test1@test.com>")
        self.assertEqual(repr(self.u2), "<User #2222: testuser2, test2@test.com>")



    # Signup Tests

    def test_signup(self):
        u_test = User.signup("signuptestuser", "signuptest@test.com", "password", None)
        uid = 1234567
        u_test.id = uid
        db.session.commit()

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, "signuptestuser")
        self.assertEqual(u_test.email, "signuptest@test.com")
        self.assertNotEqual(u_test.password, "password")

        self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_username_on_signup(self):
        invalid_user = User.signup(None, "test@test.com", "password", None)
        uid = 12345678
        invalid_user.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_on_signup(self):
        invalid_email = User.signup("noemailuser", None, 'password', None)
        uid = 123456789
        invalid_email.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_on_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("testnullpassword", "test@test.com", "", None)

        with self.assertRaises(ValueError) as context:
            User.signup("testnopassword", "test@test.com", None, None)

    # Authentication Tests

    def test_authentication(self):
        u = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.uid1)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("notauser", "password"))

    def test_invalid_password(self):
        self.assertFalse(User.authenticate(self.u1.username, "wrongpassword"))


    # Following Tests

    def test_user_follows(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u1.following), 1)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(len(self.u2.following), 0)
        self.assertEqual(len(self.u2.followers), 1)

        self.assertEqual(self.u1.following[0].id, self.u2.id)
        self.assertEqual(self.u2.followers[0].id, self.u1.id)

    def test_is_following(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))

    def test_is_followed_by(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))