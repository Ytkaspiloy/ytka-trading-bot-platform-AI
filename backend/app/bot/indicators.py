import talib
import numpy as np
import pandas as pd

def calculate_indicators(df):
    """Расчет технических индикаторов"""
    try:
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        
        # RSI
        rsi = talib.RSI(close, timeperiod=14)
        
        # MACD
        macd, macd_signal, macd_hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        
        # Moving averages
        sma_10 = talib.SMA(close, timeperiod=10)
        sma_20 = talib.SMA(close, timeperiod=20)
        sma_50 = talib.SMA(close, timeperiod=50)
        ema_21 = talib.EMA(close, timeperiod=21)
        ema_50 = talib.EMA(close, timeperiod=50)
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)
        
        # Stochastic
        stoch_k, stoch_d = talib.STOCH(high, low, close, 
                                      fastk_period=14, 
                                      slowk_period=3, 
                                      slowd_period=3)
        
        # ATR
        atr = talib.ATR(high, low, close, timeperiod=14)
        
        return {
            'rsi': float(rsi[-1]) if len(rsi) > 0 else None,
            'macd': float(macd[-1]) if len(macd) > 0 else None,
            'macd_signal': float(macd_signal[-1]) if len(macd_signal) > 0 else None,
            'macd_hist': float(macd_hist[-1]) if len(macd_hist) > 0 else None,
            'sma_10': float(sma_10[-1]) if len(sma_10) > 0 else None,
            'sma_20': float(sma_20[-1]) if len(sma_20) > 0 else None,
            'sma_50': float(sma_50[-1]) if len(sma_50) > 0 else None,
            'ema_21': float(ema_21[-1]) if len(ema_21) > 0 else None,
            'ema_50': float(ema_50[-1]) if len(ema_50) > 0 else None,
            'bb_upper': float(bb_upper[-1]) if len(bb_upper) > 0 else None,
            'bb_middle': float(bb_middle[-1]) if len(bb_middle) > 0 else None,
            'bb_lower': float(bb_lower[-1]) if len(bb_lower) > 0 else None,
            'stoch_k': float(stoch_k[-1]) if len(stoch_k) > 0 else None,
            'stoch_d': float(stoch_d[-1]) if len(stoch_d) > 0 else None,
            'atr': float(atr[-1]) if len(atr) > 0 else None
        }
        
    except Exception as e:
        print(f"Error calculating indicators: {e}")
        return {}