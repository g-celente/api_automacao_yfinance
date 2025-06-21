from app import db
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.model.Cliente import Cliente

class Carteira(db.Model):
    """
    Modelo de carteira que pertence a um cliente.

    Attributes:
        id (int): ID único da carteira
        cliente_id (int): ID do cliente proprietário
        nome (str): Nome da carteira
        descricao (str): Descrição da carteira (opcional)
        created_at (datetime): Data de criação da carteira
        updated_at (datetime): Data da última atualização
        ativos (relationship): Relacionamento com os ativos da carteira
    """
    __tablename__ = 'carteiras'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id', ondelete='CASCADE'), nullable=False, index=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    ativos = db.relationship('Asset', backref='carteira', lazy=True, cascade='all, delete-orphan')

    def __init__(self, cliente_id: int, nome: str, descricao: str = None):
        """
        Inicializa uma nova carteira.

        Args:
            cliente_id (int): ID do cliente proprietário
            nome (str): Nome da carteira
            descricao (str, optional): Descrição da carteira
        """
        self.cliente_id = cliente_id
        self.nome = nome
        self.descricao = descricao

    @classmethod
    def get_carteiras_by_cliente(cls, cliente_id: int) -> List['Carteira']:
        """
        Busca todas as carteiras de um cliente.

        Args:
            cliente_id (int): ID do cliente

        Returns:
            List[Carteira]: Lista de carteiras do cliente
        """
        return cls.query.filter_by(cliente_id=cliente_id).order_by(cls.created_at.desc()).all()

    @classmethod
    def find_by_nome_and_cliente(cls, nome: str, cliente_id: int) -> Optional['Carteira']:
        """
        Busca uma carteira pelo nome e cliente.

        Args:
            nome (str): Nome da carteira
            cliente_id (int): ID do cliente

        Returns:
            Optional[Carteira]: Carteira encontrada ou None
        """
        return cls.query.filter_by(nome=nome, cliente_id=cliente_id).first()
    
    @classmethod
    def find_by_id(cls, carteira_id: int) -> Optional['Carteira']:
        """
        Busca uma carteira pelo ID.

        Args:
            carteira_id (int): ID da carteira

        Returns:
            Optional[Carteira]: Carteira encontrada ou None
        """
        return cls.query.filter_by(id=carteira_id).first()
    
    @classmethod
    def find_all(cls) -> List['Carteira']:
        """
        Busca todas as carteiras no banco de dados.

        Returns:
            List[Carteira]: Lista de todas as carteiras
        """
        return cls.query.all()

    @classmethod
    def get_carteiras_by_admin(cls, user_adm_id: int) -> List['Carteira']:
        """
        Busca todas as carteiras dos clientes de um usuário administrador.

        Args:
            user_adm_id (int): ID do usuário administrador

        Returns:
            List[Carteira]: Lista de carteiras dos clientes do admin
        """
        return cls.query.join(Cliente).filter(Cliente.user_adm_id == user_adm_id).all()

    @classmethod
    def update_carteira_by_admin(cls, carteira_id: int, user_adm_id: int, data: dict) -> Optional['Carteira']:
        """
        Atualiza uma carteira apenas se ela pertencer a um cliente do admin autenticado.

        Args:
            carteira_id (int): ID da carteira
            user_adm_id (int): ID do usuário administrador
            data (dict): Dados para atualização

        Returns:
            Optional[Carteira]: Carteira atualizada ou None se não encontrada/autorizada
        """
        carteira = cls.query.join(Cliente).filter(
            cls.id == carteira_id,
            Cliente.user_adm_id == user_adm_id
        ).first()
        
        if not carteira:
            return None
        
        # Atualiza os campos permitidos
        if 'nome' in data:
            carteira.nome = data['nome']
        if 'descricao' in data:
            carteira.descricao = data['descricao']
        
        carteira.updated_at = datetime.utcnow()
        
        db.session.commit()
        return carteira

    @classmethod
    def delete(cls, carteira: 'Carteira') -> None:
        """
        Deleta uma carteira do banco de dados.

        Args:
            carteira (Carteira): Carteira a ser deletada
        """
        db.session.delete(carteira)
        db.session.commit()
    
    @classmethod
    def save(cls, carteira: 'Carteira') -> 'Carteira':
        """
        Salva a carteira no banco de dados.
        """
        db.session.add(carteira)
        db.session.commit()

    def get_valor_total(self) -> Decimal:
        """
        Calcula o valor total da carteira baseado nos ativos.

        Returns:
            Decimal: Valor total da carteira
        """
        total = Decimal('0.00')
        for ativo in self.ativos:
            if ativo.quantidade and ativo.valor_unitario:
                total += Decimal(str(ativo.quantidade)) * Decimal(str(ativo.valor_unitario))
        return total

    def get_quantidade_ativos(self) -> int:
        """
        Retorna a quantidade de ativos únicos na carteira.

        Returns:
            int: Número de ativos na carteira
        """
        return len(self.ativos)

    def get_ativos_por_tipo(self) -> dict:
        """
        Agrupa os ativos por tipo.

        Returns:
            dict: Dicionário com tipos como chave e lista de ativos como valor
        """
        tipos = {}
        for ativo in self.ativos:
            tipo = ativo.tipo or 'Outros'
            if tipo not in tipos:
                tipos[tipo] = []
            tipos[tipo].append(ativo)
        return tipos

    def to_dict(self, include_ativos: bool = False) -> dict:
        """
        Converte a carteira em um dicionário para serialização.

        Args:
            include_ativos (bool): Se deve incluir os ativos na serialização

        Returns:
            dict: Representação da carteira em dicionário
        """
        result = {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'nome': self.nome,
            'descricao': self.descricao,
            'valor_total': float(self.get_valor_total()),
            'quantidade_ativos': self.get_quantidade_ativos(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_ativos:
            result['ativos'] = [ativo.to_dict() for ativo in self.ativos]
            result['ativos_por_tipo'] = {
                tipo: len(ativos) for tipo, ativos in self.get_ativos_por_tipo().items()
            }
        
        return result

    def __repr__(self):
        return f'<Carteira {self.nome} (Cliente ID: {self.cliente_id})>'
