from flask import render_template
from flask import current_app as app
import sys

def register_error_handlers(app):
    from werkzeug.exceptions import HTTPException

    @app.errorhandler(Exception)
    def handle_exception(e):
        if app.testing:
            raise e
            
        # Pass through HTTP errors
        if isinstance(e, HTTPException):
            return render_template('shared/error.html', error=e), e.code
            
        from app.services.audit import log_error
        log_error(str(e), sys.exc_info()[1])
        return render_template('shared/error.html', error=e), 500
