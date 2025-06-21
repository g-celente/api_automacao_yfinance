from app import db
from datetime import datetime
from typing import List, Optional
from sqlalchemy import and_

class Asset(db.Model):
    """
    Modelo de ativo financeiro com dados históricos.
    
    Attributes:
        id (int): ID único do registro
        carteira_id (int): ID da carteira proprietária
        ticker (str): Símbolo do ativo (ex: ITUB4.SA)
        date (datetime): Data do fechamento
        close (float): Preço de fechamento
        created_at (datetime): Data de criação do registro
    """
    __tablename__ = 'asset'
    
    id = db.Column(db.Integer, primary_key=True)
    carteira_id = db.Column(db.Integer, db.ForeignKey('carteiras.id', ondelete='CASCADE'), nullable=False, index=True)
    ticker = db.Column(db.String(20), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    close = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('carteira_id', 'ticker', 'date', name='uq_carteira_ticker_date'),
        db.CheckConstraint('close > 0', name='check_close_positive'),
    )

    def __init__(self, carteira_id: int, ticker: str, date: datetime, close: float):
        """
        Inicializa um novo registro de ativo.
        
        Args:
            carteira_id (int): ID da carteira
            ticker (str): Símbolo do ativo
            date (datetime): Data do fechamento
            close (float): Preço de fechamento
        """
        self.carteira_id = carteira_id
        self.ticker = ticker.upper()
        self.date = date.date() if hasattr(date, 'date') else date
        self.close = close

    @classmethod
    def get_assets_by_carteira(cls, carteira_id: int) -> List['Asset']:
        """
        Busca todos os ativos de uma carteira.
        
        Args:
            carteira_id (int): ID da carteira
            
        Returns:
            List[Asset]: Lista de ativos da carteira
        """
        return cls.query.filter_by(carteira_id=carteira_id).order_by(cls.date.desc()).all()

    @classmethod
    def get_unique_tickers_by_carteira(cls, carteira_id: int) -> List[str]:
        """
        Busca todos os tickers únicos de uma carteira.
        
        Args:
            carteira_id (int): ID da carteira
            
        Returns:
            List[str]: Lista de tickers únicos
        """
        result = db.session.query(cls.ticker).filter_by(carteira_id=carteira_id).distinct().all()
        return [row[0] for row in result]

    @classmethod
    def asset_exists(cls, carteira_id: int, ticker: str, date: datetime) -> bool:
        """
        Verifica se um ativo já existe para uma data específica.
        
        Args:
            carteira_id (int): ID da carteira
            ticker (str): Símbolo do ativo
            date (datetime): Data do fechamento
            
        Returns:
            bool: True se o ativo já existe
        """
        check_date = date.date() if hasattr(date, 'date') else date
        return cls.query.filter(
            and_(
                cls.carteira_id == carteira_id,
                cls.ticker == ticker.upper(),
                cls.date == check_date
            )
        ).first() is not None

    @classmethod
    def bulk_insert(cls, assets_data: List[dict]) -> int:
        """
        Inserção em lote de ativos.
        
        Args:
            assets_data (List[dict]): Lista de dados dos ativos
            
        Returns:
            int: Número de registros inseridos
        """
        try:
            # Remove duplicatas baseado em carteira_id, ticker e date
            unique_assets = []
            seen = set()
            
            for asset_data in assets_data:
                key = (asset_data['carteira_id'], asset_data['ticker'], asset_data['date'])
                if key not in seen:
                    seen.add(key)
                    unique_assets.append(asset_data)
            
            if unique_assets:
                db.session.bulk_insert_mappings(cls, unique_assets)
                db.session.commit()
                return len(unique_assets)
            return 0
            
        except Exception as e:
            db.session.rollback()
            raise e

    def to_dict(self) -> dict:
        """
        Converte o ativo para dicionário.
        
        Returns:
            dict: Dados do ativo
        """
        return {
            'id': self.id,
            'carteira_id': self.carteira_id,
            'ticker': self.ticker,
            'date': self.date.isoformat(),
            'close': self.close,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self) -> str:
        return f'<Asset {self.ticker} {self.date}: R$ {self.close}>'

    