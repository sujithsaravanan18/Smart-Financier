import pytest
from app import create_app
from app.extensions import db
from config import Config
from app.models import Role, User

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    WTF_CSRF_ENABLED = False
    WTF_CSRF_CHECK_DEFAULT = False
    RATELIMIT_ENABLED = False

@pytest.fixture(scope='session')
def app():
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        
        # Create Roles
        admin_role = Role(name='Super Admin')
        creditor_role = Role(name='Creditor')
        debtor_role = Role(name='Debtor')
        db.session.add_all([admin_role, creditor_role, debtor_role])
        db.session.commit()
        
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def init_database(app):
    with app.app_context():
        # Clear out users between tests if needed, but in memory sqlite is fast
        db.session.query(User).delete()
        db.session.commit()
        yield db
