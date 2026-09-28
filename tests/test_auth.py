from app.models import User
from app.extensions import db

def test_login_success(client, init_database):
    # Setup
    user = User(username='test_login', email='login@test.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()
    
    # Test
    response = client.post('/auth/login', data={
        'username': 'test_login',
        'password': 'password'
    }, follow_redirects=True)
    print("LOGIN RESPONSE DATA:", response.data)
    
    assert b'Logout' in response.data

def test_login_failure(client, init_database):
    response = client.post('/auth/login', data={
        'username': 'nonexistent',
        'password': 'password'
    }, follow_redirects=True)
    
    assert b'Invalid username or password' in response.data

def test_login_deactivated(client, init_database):
    user = User(username='deactivated', email='deactivated@test.com', is_active=False)
    user.set_password('password')
    db.session.add(user)
    db.session.commit()
    
    response = client.post('/auth/login', data={
        'username': 'deactivated',
        'password': 'password'
    }, follow_redirects=True)
    
    assert b'This account has been deactivated.' in response.data

def test_logout(client, init_database):
    user = User(username='test_logout', email='logout@test.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()
    
    client.post('/auth/login', data={'username': 'test_logout', 'password': 'password'})
    response = client.get('/auth/logout', follow_redirects=True)
    
    assert b'You have been logged out.' in response.data

def test_register(client, init_database):
    response = client.post('/auth/register', data={
        'username': 'new_user',
        'email': 'new@test.com',
        'password': 'password123',
        'role': 'Creditor'
    }, follow_redirects=True)
    
    assert b'Congratulations, you are now a registered user!' in response.data
    # Verify they can log in
    response = client.post('/auth/login', data={'username': 'new_user', 'password': 'password123'}, follow_redirects=True)
    assert b'Logout' in response.data

def test_forgot_and_reset_password(client, init_database):
    user = User(username='test_reset', email='reset@test.com')
    user.set_password('oldpassword')
    db.session.add(user)
    db.session.commit()
    
    # Request reset
    response = client.post('/auth/forgot_password', data={'email': 'reset@test.com'}, follow_redirects=True)
    assert b'A password reset link has been generated' in response.data
    
    # Get token manually for testing
    token = user.get_reset_password_token()
    
    # Reset password
    response = client.post(f'/auth/reset_password/{token}', data={'password': 'newpassword'}, follow_redirects=True)
    assert b'Your password has been reset.' in response.data
    
    # Test new password
    response = client.post('/auth/login', data={'username': 'test_reset', 'password': 'newpassword'}, follow_redirects=True)
    assert b'Logout' in response.data
