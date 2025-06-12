from app import db
from datetime import datetime

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(10), unique=True, nullable=False)  # ex: BOVA11
    name = db.Column(db.String(100), nullable=False)
    sector = db.Column(db.String(100))
    price = db.Column(db.Float)  # valor atual (se quiser armazenar isso)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)