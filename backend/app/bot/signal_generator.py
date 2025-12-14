def generate_signal(df, indicators):
    """Генерация торгового сигнала"""
    if not indicators:
        return None
    
    # Сигналы на основе индикаторов
    buy_signals = 0
    sell_signals = 0
    
    # RSI сигналы
    if indicators['rsi']:
        if indicators['rsi'] < 30:
            buy_signals += 1
        elif indicators['rsi'] > 70:
            sell_signals += 1
    
    # MACD сигналы
    if indicators['macd'] and indicators['macd_signal']:
        if indicators['macd'] > indicators['macd_signal']:
            buy_signals += 1
        else:
            sell_signals += 1
    
    # Moving averages
    if indicators['sma_10'] and indicators['sma_20']:
        if indicators['sma_10'] > indicators['sma_20']:
            buy_signals += 1
        else:
            sell_signals += 1
    
    if indicators['ema_21'] and indicators['ema_50']:
        if indicators['ema_21'] > indicators['ema_50']:
            buy_signals += 1
        else:
            sell_signals += 1
    
    # Stochastic
    if indicators['stoch_k'] and indicators['stoch_d']:
        if indicators['stoch_k'] > indicators['stoch_d']:
            buy_signals += 1
        else:
            sell_signals += 1
    
    # Подсчет общего сигнала
    total_signals = buy_signals + sell_signals
    if total_signals == 0:
        return None
    
    buy_ratio = buy_signals / total_signals
    sell_ratio = sell_signals / total_signals
    
    signal = None
    confidence = 0
    
    if buy_ratio > 0.6:
        signal = 'buy'
        confidence = buy_ratio
    elif sell_ratio > 0.6:
        signal = 'sell'
        confidence = sell_ratio
    
    if signal:
        current_price = float(df['close'].iloc[-1])
        
        # Расчет стоп-лосса и тейк-профита
        if indicators['atr']:
            atr = indicators['atr']
            if signal == 'buy':
                stop_loss = current_price - (atr * 1.5)
                take_profit = current_price + (atr * 3)
            else:
                stop_loss = current_price + (atr * 1.5)
                take_profit = current_price - (atr * 3)
        else:
            # Значения по умолчанию
            risk_reward = 0.02  # 2%
            if signal == 'buy':
                stop_loss = current_price * (1 - risk_reward)
                take_profit = current_price * (1 + risk_reward * 2)
            else:
                stop_loss = current_price * (1 + risk_reward)
                take_profit = current_price * (1 - risk_reward * 2)
        
        return {
            'signal': signal,
            'confidence': round(confidence, 2),
            'price': current_price,
            'stop_loss': round(stop_loss, 5),
            'take_profit': round(take_profit, 5),
            'indicators': indicators
        }
    
    return None