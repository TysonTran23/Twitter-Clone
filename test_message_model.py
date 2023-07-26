import os
from unittest import TestCase

from sqlalchemy import exc

from models import Follows, Likes, Message, User, db

os.environ["DATABASE_URL"] = "postgresql:///warbler-test"
from app import app

db.create_all()


class MessageModelTestCase(TestCase):
    """Test views for messages"""

    def setUp(self):
        db.drop_all()
        db.create_all()
        self.uid = 9999

        u = User.signup("testing", "testing@test.com", "password", None)
        u.id = self.uid

        self.u = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        message = Message(text="This is a tweet", user_id=self.uid)
        db.session.add(message)
        db.session.commit()

        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(self.u.messages[0].text, "This is a tweet")

    def test_likes(self):
        m1 = Message(text="This is a tweet", user_id=self.uid)
        m2 = Message(text="This is a comment blah blah", user_id=self.uid)
        u = User.signup("testingagain", "testingmore@more.com", "password", None)

        db.session.add_all([m1, m2, u])
        db.session.commit()

        u.likes.append(m1)

        db.session.commit()

        l = Likes.query.filter(Likes.user_id == u.id).all()
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].message_id, m1.id)
