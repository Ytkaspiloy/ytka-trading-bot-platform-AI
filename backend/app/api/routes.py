from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.signal import Signal
from app.models.trade import Trade
from app.bot.mt5_bot import TradingBot
import logging

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__)
bot = TradingBot()

@api_bp.route('/auth/telegram', methods=['POST'])
def auth_telegram():
    """Аутентификация через Telegram"""
    try:
        data = request.get_json()
        
        if not data or 'telegram_id' not in data:
            return jsonify({'error': 'Telegram ID required'}), 400
        
        # Получаем или создаем пользователя
        user = User.get_or_create(
            telegram_id=data['telegram_id'],
            username=data.get('username'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        
        # Обновляем последний логин
        from datetime import datetime
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Генерируем токен
        token = user.generate_token()
        
        return jsonify({
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Auth error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/signals', methods=['GET'])
@jwt_required()
def get_signals():
    """Получение списка сигналов"""
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        signals = Signal.query.filter_by(user_id=user_id)\
            .order_by(Signal.created_at.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
        
        return jsonify({
            'signals': [signal.to_dict() for signal in signals],
            'total': Signal.query.filter_by(user_id=user_id).count()
        }), 200
        
    except Exception as e:
        logger.error(f"Get signals error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/signals/<int:signal_id>', methods=['GET'])
@jwt_required()
def get_signal(signal_id):
    """Получение конкретного сигнала"""
    try:
        user_id = get_jwt_identity()
        signal = Signal.query.filter_by(id=signal_id, user_id=user_id).first()
        
        if not signal:
            return jsonify({'error': 'Signal not found'}), 404
        
        return jsonify(signal.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Get signal error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/trades', methods=['GET'])
@jwt_required()
def get_trades():
    """Получение списка сделок"""
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        trades = Trade.query.filter_by(user_id=user_id)\
            .order_by(Trade.opened_at.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
        
        return jsonify({
            'trades': [trade.to_dict() for trade in trades],
            'total': Trade.query.filter_by(user_id=user_id).count()
        }), 200
        
    except Exception as e:
        logger.error(f"Get trades error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/market/analyze', methods=['POST'])
@jwt_required()
def analyze_market():
    """Анализ рынка"""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        timeframe = data.get('timeframe', 'M5')
        
        if not symbol:
            return jsonify({'error': 'Symbol required'}), 400
        
        # Анализируем символ
        from app.bot.mt5_bot import TradingBot
        analysis = bot._analyze_symbol(symbol, timeframe)
        
        return jsonify({
            'symbol': symbol,
            'timeframe': timeframe,
            'analysis': analysis
        }), 200
        
    except Exception as e:
        logger.error(f"Analyze market error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/bot/start', methods=['POST'])
@jwt_required()
def start_bot():
    """Запуск торгового бота"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        bot.start()
        
        return jsonify({
            'status': 'bot_started',
            'message': 'Trading bot started successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Start bot error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/bot/stop', methods=['POST'])
@jwt_required()
def stop_bot():
    """Остановка торгового бота"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        bot.stop()
        
        return jsonify({
            'status': 'bot_stopped',
            'message': 'Trading bot stopped successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Stop bot error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/bot/status', methods=['GET'])
@jwt_required()
def bot_status():
    """Статус торгового бота"""
    try:
        return jsonify({
            'running': bot.running,
            'mt5_initialized': bot.mt5_initialized,
            'workers': len(bot.workers)
        }), 200
        
    except Exception as e:
        logger.error(f"Bot status error: {e}")
        return jsonify({'error': str(e)}), 500