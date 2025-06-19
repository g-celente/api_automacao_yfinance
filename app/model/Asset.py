from app import db
from datetime import datetime

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), unique=True, nullable=False)  # ex: BOVA11
    date = db.Column(db.DateTime, nullable=False)
    close = db.Column(db.Float) # valor atual (se quiser armazenar isso)
    carteira_id = db.Column(db.Integer, db.ForeignKey('carteiras.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    