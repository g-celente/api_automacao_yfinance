from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional
from datetime import datetime

class Cliente(db.Model):
    """
    Modelo de cliente que pertence a um usuário administrador.

    Attributes:
        id (int): ID único do cliente
        user_adm_id (int): ID do usuário administrador responsável
        name (str): Nome completo do cliente
        email (str): Email único do cliente
        telefone (str): Telefone do cliente (opcional)
        cpf (str): CPF único do cliente
        password_hash (str): Hash da senha do cliente
        status (str): Status do cliente (ativo, inativo, suspenso)
        created_at (datetime): Data de criação do cliente
        updated_at (datetime): Data da última atualização
        carteiras (relationship): Relacionamento com as carteiras do cliente
    """
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True)
    user_adm_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    telefone = db.Column(db.String(20), nullable=True)
    cpf = db.Column(db.String(14), unique=True, nullable=False, index=True)
    status = db.Column(db.String(20), default='ativo', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    carteiras = db.relationship('Carteira', backref='cliente', lazy=True, cascade='all, delete-orphan')

    def __init__(self, user_adm_id: int, name: str, email: str, cpf: str, password: str, 
                 telefone: str = None, status: str = 'ativo'):
        """
        Inicializa um novo cliente.

        Args:
            user_adm_id (int): ID do usuário administrador
            name (str): Nome do cliente
            email (str): Email do cliente
            cpf (str): CPF do cliente
            password (str): Senha em texto plano
            telefone (str, optional): Telefone do cliente
            status (str, optional): Status do cliente. Defaults to 'ativo'.
        """
        self.user_adm_id = user_adm_id
        self.name = name
        self.email = email
        self.cpf = cpf
        self.telefone = telefone
        self.status = status


    @classmethod
    def find_by_email(cls, email: str) -> Optional['Cliente']:
        """
        Busca um cliente pelo email.

        Args:
            email (str): Email do cliente

        Returns:
            Optional[Cliente]: Cliente encontrado ou None
        """
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_cpf(cls, cpf: str) -> Optional['Cliente']:
        """
        Busca um cliente pelo CPF.

        Args:
            cpf (str): CPF do cliente

        Returns:
            Optional[Cliente]: Cliente encontrado ou None
        """
        return cls.query.filter_by(cpf=cpf).first()

    @classmethod
    def get_clientes_by_admin(cls, user_adm_id: int) -> list:
        """
        Busca todos os clientes de um administrador.

        Args:
            user_adm_id (int): ID do usuário administrador

        Returns:
            list: Lista de clientes
        """
        return cls.query.filter_by(user_adm_id=user_adm_id, status='ativo').all()

    def is_active(self) -> bool:
        """
        Verifica se o cliente está ativo.

        Returns:
            bool: True se o cliente está ativo
        """
        return self.status == 'ativo'

    def deactivate(self):
        """
        Desativa o cliente.
        """
        self.status = 'inativo'
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def activate(self):
        """
        Ativa o cliente.
        """
        self.status = 'ativo'
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def to_dict(self) -> dict:
        """
        Converte o cliente em um dicionário para serialização.

        Returns:
            dict: Representação do cliente em dicionário
        """
        return {
            'id': self.id,
            'user_adm_id': self.user_adm_id,
            'name': self.name,
            'email': self.email,
            'telefone': self.telefone,
            'cpf': self.cpf,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Cliente {self.name} ({self.email})>'
