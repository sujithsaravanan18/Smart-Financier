from flask import Flask, session, request
from config import Config
from app.extensions import db, migrate, login_manager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    from app.extensions import csrf, limiter, cache
    csrf.init_app(app)
    limiter.init_app(app)
    
    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 60
    cache.init_app(app)
    
    from flask_talisman import Talisman
    csp = {
        'default-src': [
            '\'self\'',
            'https://cdn.jsdelivr.net'
        ],
        'img-src': ['*', 'data:']
    }
    Talisman(app, content_security_policy=csp, force_https=not (app.testing or app.debug))

    # Initialize Babel
    from app.extensions import babel
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

    def get_locale():
        from flask_login import current_user
        if current_user.is_authenticated and current_user.language:
            return current_user.language
        return session.get('lang', 'en')

    babel.init_app(app, locale_selector=get_locale)

    # Initialize APScheduler
    from app.extensions import scheduler
    scheduler.init_app(app)
    scheduler.start()

    # Import tasks so APScheduler registers them
    with app.app_context():
        from app.notifications import tasks

    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.creditor import bp as creditor_bp
    app.register_blueprint(creditor_bp, url_prefix='/creditor')

    from app.debtor import bp as debtor_bp
    app.register_blueprint(debtor_bp, url_prefix='/debtor')

    from app.dashboard import bp as dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

    from app.loans import bp as loans_bp
    app.register_blueprint(loans_bp, url_prefix='/loans')

    from app.payments import bp as payments_bp
    app.register_blueprint(payments_bp, url_prefix='/payments')

    from app.settings import bp as settings_bp
    app.register_blueprint(settings_bp, url_prefix='/settings')

    from app.logs import bp as logs_bp
    app.register_blueprint(logs_bp, url_prefix='/logs')

    from app.middleware.errors import register_error_handlers
    register_error_handlers(app)

    return app
