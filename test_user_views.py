import os
from unittest import TestCase

from models import Message, User, connect_db, db, Likes, Follows

os.environ["DATABASE_URL"] = "postgresql:///warbler-test"

from app import CURR_USER_KEY, app

db.create_all()

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
        self.testuser_id = 8989
        self.testuser.id = self.testuser_id

        self.u1 = User.signup("abc", "test1@test.com", "password", None)
        self.u1_id = 778
        self.u1.id = self.u1_id
        self.u2 = User.signup("efg", "test2@test.com", "password", None)
        self.u2_id = 884
        self.u2.id = self.u2_id
        self.u3 = User.signup("hij", "test3@test.com", "password", None)
        self.u4 = User.signup("testing", "test4@test.com", "password", None)

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp
    
    def get_users(self):
        with self.client as c:
            resp = c.get("/users")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@abc", str(resp.data))
            self.assertIn("@efg", str(resp.data))
            self.assertIn("@hij", str(resp.data))
            self.assertIn("@testing", str(resp.data))
    
    def test_users_search(self):
        with self.client as c:
            resp = c.get("/users?q=test")

            self.assertIn("@testing", str(resp.data))
            self.assertNotIn("@efg", str(resp.data))
    
    def show_user(self):
        with self.client as c:
            resp = c.get(f"/users/{self.u1.id}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@abc", str(resp.data))
    
    def test_add_like(self):
        m = Message(id=8000, text="kiwis are the best", user_id=self.u1.id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.post(f"users/add_like/{m.id}", follows_redirects=True)

            self.assertEqual(resp.status_code, 200)

            likes = Likes.query.filter(Likes.message_id==8000).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.testuser_id)
