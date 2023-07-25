"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import Follows, Message, User, db

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

        u1 = User.signup("test1", "email1@email.com", "password", None)
        uid1 = 1111
        u1.id = uid1

        u2 = User.signup("test2", "email2@email.com", "password", None)
        uid2 = 2222
        u2.id = uid2

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
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
    
    def test_repr_method(self):
        """Does the repr method work as expected?"""
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        expected_repr = f"<User #{u.id}: {u.username}, {u.email}>"
        self.assertEqual(repr(u), expected_repr)

    def test_detect_following(self):
        """Does is_following successfully detect when user1 is following user2?"""
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
           

    def test_detect_not_following(self):
        """Does is_following successfully detect when user1 is NOT following user2?"""

        self.assertFalse(self.u1.is_following(self.u2))
    
    def test_detect_is_followed_by(self):
        """Does is_followed_by successfully detect when user 1 is followed by user 2"""

        self.u2.following.append(self.u1)
        db.session.commit()
        self.assertTrue(self.u1.is_followed_by(self.u2))
    
    def test_detect_not_is_followed_by(self):
        """Does is_followed_by succesffuly detect when user 1 is not followed by user 2"""

        self.assertFalse(self.u1.is_followed_by(self.u2))
    
    def test_signup(self):
        """Signing up a user"""
        u = User.signup("username", "email@email.com", "password", None)
        uid = 9999
        u.id = uid
        db.session.commit()

        u = User.query.get(uid)

        self.assertIsNotNone(u)
        self.assertEqual(u.username, "username")
        self.assertEqual(u.email, "email@email.com")
        self.assertNotEqual(u.password, "password")

        #Bcrypt strings start with $2b$
        self.assertTrue(u.password.startswith("$2b$"))
    
    def test_invalid_username(self):
        """Invalid Username"""
        u = User.signup(None, "email@email.com", "password", None)
        uid = 9999
        u.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
        
    def test_invalid_email(self):
        """Invalid Username"""
        u = User.signup("username", None, "password", None)
        uid = 9999
        u.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password(self):
        """Invalid Password""" 
        with self.assertRaises(ValueError) as context:
            User.signup("username", "email@email.com", None, None)

        with self.assertRaises(ValueError) as context:
            User.signup("username", "email@email.com", None, None)
    
    def test_valid_authentication(self):
        u = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.uid1)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("notmebruv", "password"))
    
    def test_invalid_password(self):
        self.assertFalse(User.authenticate(self.u1.username, "notmypassword"))

