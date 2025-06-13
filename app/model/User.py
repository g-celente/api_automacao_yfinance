from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional
from datetime import datetime

class User(db.Model):
    """
    Modelo de usuário que representa um usuário no sistema.

    Attributes:
        id (int): ID único do usuário
        name (str): Nome completo do usuário
        email (str): Email único do usuário
        password_hash (str): Hash da senha do usuário
        role (str): Papel do usuário ('admin' ou 'client')
        portfolios (relationship): Relacionamento com as carteiras do usuário
        created_at (datetime): Data de criação do usuário
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='client')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    portfolios = db.relationship('Portfolio', backref='owner', lazy=True, cascade='all, delete-orphan')

    def __init__(self, name: str, email: str, password: str, role: str = 'client'):
        """
        Inicializa um novo usuário.

        Args:
            name (str): Nome do usuário
            email (str): Email do usuário
            password (str): Senha em texto plano
            role (str, optional): Papel do usuário. Defaults to 'client'.
        """
        self.name = name
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.role = role

    def check_password(self, password: str) -> bool:
        """
        Verifica se a senha fornecida corresponde ao hash armazenado.

        Args:
            password (str): Senha em texto plano para verificar

        Returns:
            bool: True se a senha está correta, False caso contrário
        """
        return check_password_hash(self.password_hash, password)

    @classmethod
    def find_by_email(cls, email: str) -> Optional['User']:
        """
        Busca um usuário pelo email.

        Args:
            email (str): Email do usuário

        Returns:
            Optional[User]: Usuário encontrado ou None
        """
        return cls.query.filter_by(email=email).first()

    @classmethod
    def add_user_adm(cls, name: str, email: str, password: str, role: str) -> 'User':
        """
        Cria e salva um novo usuário administrativo.

        Args:
            name (str): Nome do usuário
            email (str): Email do usuário
            password (str): Senha em texto plano
            role (str): Papel do usuário

        Returns:
            User: Novo usuário criado
        """
        new_user = cls(name, email, password, role)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def to_dict(self) -> dict:
        """
        Converte o usuário em um dicionário para serialização.

        Returns:
            dict: Representação do usuário em dicionário
        """
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
