from app.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.base import TimestampMixin, SoftDeleteMixin, generate_uuid

class Role(db.Model, TimestampMixin):
    __tablename__ = 'roles'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(255))

    users = db.relationship('User', backref='role', lazy=True)

class User(UserMixin, db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    role_id = db.Column(db.String(36), db.ForeignKey('roles.id'), nullable=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_active = db.Column(db.Boolean, default=True)
    
    # Profile preferences
    profile_photo_url = db.Column(db.String(255))
    theme_color = db.Column(db.String(20), default='light')
    language = db.Column(db.String(10), default='en')

    creditor_profile = db.relationship('Creditor', backref='user', uselist=False)
    # If debtor logs in, they have a profile
    debtor_profile = db.relationship('Debtor', backref='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self):
        from flask import current_app
        from itsdangerous import URLSafeTimedSerializer
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'reset_password': self.id})

    @staticmethod
    def verify_reset_password_token(token, expires_in=3600):
        from flask import current_app
        from itsdangerous import URLSafeTimedSerializer
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token, max_age=expires_in)
            user_id = data.get('reset_password')
            if not user_id:
                return None
            return User.query.get(user_id)
        except:
            return None

class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True) # Null for global
    setting_key = db.Column(db.String(64), nullable=False)
    setting_value = db.Column(db.Text)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
