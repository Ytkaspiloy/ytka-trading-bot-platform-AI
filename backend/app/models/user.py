from datetime import datetime
from app import db
from flask_jwt_extended import create_access_token

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    signals = db.relationship('Signal', backref='user', lazy=True)
    trades = db.relationship('Trade', backref='user', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'telegram_id': self.telegram_id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def generate_token(self):
        return create_access_token(identity=str(self.id))
    
    @classmethod
    def get_or_create(cls, telegram_id, **kwargs):
        user = cls.query.filter_by(telegram_id=telegram_id).first()
        if not user:
            user = cls(telegram_id=telegram_id, **kwargs)
            db.session.add(user)
            db.session.commit()
        return user