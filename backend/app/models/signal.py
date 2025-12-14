from datetime import datetime
from app import db

class Signal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    timeframe = db.Column(db.String(10), nullable=False)
    signal_type = db.Column(db.String(10), nullable=False)  # buy/sell
    entry_price = db.Column(db.Float, nullable=False)
    stop_loss = db.Column(db.Float)
    take_profit = db.Column(db.Float)
    probability = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')  # pending, active, completed, cancelled
    result = db.Column(db.String(20))  # profit, loss, breakeven
    profit_loss = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime)
    
    # Technical indicators at signal time
    rsi = db.Column(db.Float)
    macd = db.Column(db.Float)
    macd_signal = db.Column(db.Float)
    sma_20 = db.Column(db.Float)
    ema_50 = db.Column(db.Float)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'signal_type': self.signal_type,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'probability': self.probability,
            'status': self.status,
            'result': self.result,
            'profit_loss': self.profit_loss,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'indicators': {
                'rsi': self.rsi,
                'macd': self.macd,
                'macd_signal': self.macd_signal,
                'sma_20': self.sma_20,
                'ema_50': self.ema_50
            }
        }