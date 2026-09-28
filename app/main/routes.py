from flask import render_template, redirect, request, session, url_for
from flask_login import login_required
from flask_babel import _
from app.main import bp
from app.middleware.auth import roles_required

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('main/index.html', title=_('Home'))

@bp.route('/set-language/<lang>')
def set_language(lang):
    if lang in ['en', 'ta']:
        session['lang'] = lang
        from flask_login import current_user
        if current_user.is_authenticated:
            current_user.language = lang
            from app.extensions import db
            db.session.commit()
    return redirect(request.referrer or url_for('main.index'))

@bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    from flask_login import current_user
    from app.extensions import db
    from app.services.supabase_storage import SupabaseStorageClient
    
    theme_color = request.form.get('theme_color')
    if theme_color in ['light', 'dark']:
        current_user.theme_color = theme_color
        
    if 'profile_photo' in request.files:
        file = request.files['profile_photo']
        if file.filename != '':
            # save file temporarily
            import tempfile
            import os
            fd, path = tempfile.mkstemp()
            try:
                with os.fdopen(fd, 'wb') as f:
                    f.write(file.read())
                
                storage = SupabaseStorageClient()
                url = storage.upload_profile_photo(path, file.filename)
                if url:
                    current_user.profile_photo_url = url
            finally:
                os.remove(path)
                
    db.session.commit()
    from flask import flash
    flash(_('Profile preferences updated.'), 'success')
    return redirect(request.referrer or url_for('main.index'))
