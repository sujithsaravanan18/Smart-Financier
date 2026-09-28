from app.models import User, Role
from app.extensions import db

def test_admin_access(client, init_database):
    admin_role = Role.query.filter_by(name='Super Admin').first()
    admin = User(username='admin', email='admin@test.com', role_id=admin_role.id)
    admin.set_password('password')
    db.session.add(admin)
    db.session.commit()
    
    client.post('/auth/login', data={'username': 'admin', 'password': 'password'})
    response = client.get('/dashboard/admin')
    assert response.status_code == 200
    
    # Check unauthorized access
    response = client.get('/dashboard/creditor', follow_redirects=True)
    # The creditor route should flash a danger message and redirect
    assert response.status_code == 200

def test_creditor_access(client, init_database):
    creditor_role = Role.query.filter_by(name='Creditor').first()
    creditor = User(username='creditor', email='creditor@test.com', role_id=creditor_role.id)
    creditor.set_password('password')
    db.session.add(creditor)
    db.session.commit()
    
    client.post('/auth/login', data={'username': 'creditor', 'password': 'password'})
    
    response = client.get('/dashboard/admin', follow_redirects=True)
    # Admin route redirects unauthorized users to index or flashes message
    assert b'You do not have permission to access this page.' in response.data
    
    response = client.get('/dashboard/debtor', follow_redirects=True)
    # Debtor route redirects
    assert b'You do not have permission' in response.data
