from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='client')  # 'admin' ou 'client'
    portfolios = db.relationship('Portfolio', backref='owner', lazy=True)

    def __init__(self, name, email, password, role='admin'):
        self.name = name
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.role = role

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)    

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def add_user_adm(cls, name, email, password, role):
        new_user = cls(name, email, password, role)
        db.session.add(new_user)
        db.session.commit()
        return new_user
