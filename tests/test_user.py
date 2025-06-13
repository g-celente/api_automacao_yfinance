import pytest
from app import create_app, db
from app.model.User import User

@pytest.fixture
def app():
    """Fixture para criar app de teste."""
    app = create_app('testing')
    return app

@pytest.fixture
def client(app):
    """Fixture para criar cliente de teste."""
    return app.test_client()

@pytest.fixture
def db_session(app):
    """Fixture para sessão de banco de dados de teste."""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

def test_user_creation(db_session):
    """Testa a criação de usuário."""
    user = User(
        name='Test User',
        email='test@example.com',
        password='password123'
    )
    db_session.session.add(user)
    db_session.session.commit()

    saved_user = User.query.filter_by(email='test@example.com').first()
    assert saved_user is not None
    assert saved_user.name == 'Test User'
    assert saved_user.check_password('password123')

def test_user_registration(client):
    """Testa o endpoint de registro."""
    response = client.post('/api/register', json={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] == True

def test_user_login(client, db_session):
    """Testa o endpoint de login."""
    # Cria usuário para teste
    user = User(
        name='Test User',
        email='test@example.com',
        password='password123'
    )
    db_session.session.add(user)
    db_session.session.commit()

    # Tenta login
    response = client.post('/api/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'token' in data
