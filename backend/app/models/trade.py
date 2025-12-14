from datetime import datetime
from app import db

class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    signal_id = db.Column(db.Integer, db.ForeignKey('signal.id'))
    symbol = db.Column(db.String(20), nullable=False)
    trade_type = db.Column(db.String(10), nullable=False)  # buy/sell
    entry_price = db.Column(db.Float, nullable=False)
    exit_price = db.Column(db.Float)
    amount = db.Column(db.Float, nullable=False)
    profit_loss = db.Column(db.Float)
    profit_loss_pips = db.Column(db.Float)
    status = db.Column(db.String(20), default='open')  # open, closed, cancelled
    opened_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime)
    
    # MT5 specific
    mt5_ticket = db.Column(db.Integer)
    mt5_order_type = db.Column(db.String(20))
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'trade_type': self.trade_type,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'amount': self.amount,
            'profit_loss': self.profit_loss,
            'profit_loss_pips': self.profit_loss_pips,
            'status': self.status,
            'opened_at': self.opened_at.isoformat() if self.opened_at else None,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'duration': (self.closed_at - self.opened_at).total_seconds() if self.closed_at and self.opened_at else None
        }