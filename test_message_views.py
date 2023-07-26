"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import Message, User, connect_db, db

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ["DATABASE_URL"] = "postgresql:///warbler-test"


# Now we can import app

from app import CURR_USER_KEY, app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config["WTF_CSRF_ENABLED"] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(
            username="testuser",
            email="test@test.com",
            password="testuser",
            image_url=None,
        )
        self.testuser_id = 9999
        self.testuser.id = self.testuser_id

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_add_no_session(self):
        """Trying to add without logging in"""
        with self.client as c:
            resp = c.post(
                "/messages/new", data={"text": "Hello"}, follow_redirects=True
            )

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_add_invalid_user(self):
        """User does not exist"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1204980

            resp = c.post(
                "/messages/new", data={"text": "Hello"}, follow_redirects=True
            )

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_show_message(self):
        """Test showing a message"""

        m = Message(id=9000, text="heydood", user_id=self.testuser.id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            m = Message.query.get(9000)
            resp = c.get(f"/messages/{m.id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn(m.text, str(resp.data))

    def test_delete_message(self):
        """Deleting a message"""

        m = Message(id=9000, text="heydood", user_id=self.testuser.id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            m = Message.query.get(9000)
            resp = c.post(f"messages/{m.id}/delete", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            get = Message.query.get(9000)
            self.assertIsNone(get)

    # def test_delete_without_authorization(self):
    #     """User tries to delete other user comment"""
    #     u = User.signup(
    #         username="blah",
    #         email="blah@test.com",
    #         password="blahblah",
    #         image_url=None,
    #     )
    #     u.id = 7777

    #     m = Message(id=1234, text="This is my comment", user_id=self.testuser_id)

    #     db.session.add_all([u,m])
    #     db.session.commit()

    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = 7777
            

    #         resp = c.post(f"/messages/1234/delete", follow_redirects=True)

    #         self.assertEqual(resp.status_code, 200)
    #         self.assertIn("Access unauthorized", str(resp.data))

    #         get = Message.query.get(m.id)

    #         self.assertIsNotNone(get)