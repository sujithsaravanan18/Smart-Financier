from app.models import User, Role
from app.extensions import db

def test_new_user(app):
    with app.app_context():
        user = User(username='testuser', email='test@test.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        assert user.username == 'testuser'
        assert user.email == 'test@test.com'
        assert user.password_hash is not None
        assert user.check_password('password123') is True
        assert user.check_password('wrongpassword') is False
        assert user.is_active is True

def test_uuid_generation(app):
    with app.app_context():
        user1 = User(username='user1', email='u1@test.com')
        user2 = User(username='user2', email='u2@test.com')
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        
        assert user1.id is not None
        assert user2.id is not None
        assert user1.id != user2.id
        assert len(user1.id) == 36 # UUID length
