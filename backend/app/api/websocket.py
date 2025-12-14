from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_jwt_extended import decode_token
from app import socketio
import logging

logger = logging.getLogger(__name__)
connected_users = {}

@socketio.on('connect')
def handle_connect():
    """Обработка подключения WebSocket"""
    logger.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    """Обработка отключения WebSocket"""
    logger.info('Client disconnected')

@socketio.on('authenticate')
def handle_authentication(data):
    """Аутентификация через WebSocket"""
    try:
        token = data.get('token')
        if not token:
            emit('error', {'message': 'Token required'})
            return False
        
        # Декодируем токен
        decoded = decode_token(token)
        user_id = decoded['sub']
        
        # Сохраняем информацию о подключении
        connected_users[user_id] = request.sid
        
        # Присоединяем к комнате пользователя
        join_room(f'user_{user_id}')
        
        emit('authenticated', {'user_id': user_id})
        logger.info(f"User {user_id} authenticated via WebSocket")
        
    except Exception as e:
        logger.error(f"WebSocket auth error: {e}")
        emit('error', {'message': 'Authentication failed'})
        return False

@socketio.on('subscribe_signals')
def handle_subscribe_signals(data):
    """Подписка на получение сигналов"""
    try:
        symbols = data.get('symbols', [])
        user_id = data.get('user_id')
        
        if user_id and user_id in connected_users:
            for symbol in symbols:
                join_room(f'symbol_{symbol}')
            
            emit('subscribed', {
                'symbols': symbols,
                'message': f'Subscribed to {len(symbols)} symbols'
            })
            
    except Exception as e:
        logger.error(f"Subscribe error: {e}")
        emit('error', {'message': str(e)})

@socketio.on('unsubscribe_signals')
def handle_unsubscribe_signals(data):
    """Отписка от получения сигналов"""
    try:
        symbols = data.get('symbols', [])
        
        for symbol in symbols:
            leave_room(f'symbol_{symbol}')
        
        emit('unsubscribed', {
            'symbols': symbols,
            'message': f'Unsubscribed from {len(symbols)} symbols'
        })
        
    except Exception as e:
        logger.error(f"Unsubscribe error: {e}")
        emit('error', {'message': str(e)})

@socketio.on('get_market_data')
def handle_get_market_data(data):
    """Получение рыночных данных"""
    try:
        symbol = data.get('symbol')
        timeframe = data.get('timeframe', 'M5')
        limit = data.get('limit', 100)
        
        # Здесь будет логика получения данных из MT5
        # Пока возвращаем заглушку
        emit('market_data', {
            'symbol': symbol,
            'timeframe': timeframe,
            'data': [],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Market data error: {e}")
        emit('error', {'message': str(e)})