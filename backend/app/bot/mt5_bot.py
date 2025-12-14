import os
import numpy as np
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import talib
import time
import threading
import queue
import logging
from flask import current_app

logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self, app=None):
        self.app = app
        self.mt5_initialized = False
        self.running = False
        self.signal_queue = queue.Queue()
        self.workers = []
        
        # Настройки из конфига
        self.mt5_login = None
        self.mt5_password = None
        self.mt5_server = None
        
        # Списки инструментов (скопированы из вашего кода)
        self.otc_instruments = [...]  # Ваш список инструментов
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        with app.app_context():
            from app import socketio
            self.socketio = socketio
            
            # Загружаем настройки
            self.mt5_login = app.config.get('MT5_LOGIN')
            self.mt5_password = app.config.get('MT5_PASSWORD')
            self.mt5_server = app.config.get('MT5_SERVER')
    
    def initialize_mt5(self):
        """Инициализация подключения к MT5"""
        max_retries = 3
        reconnect_delay = 5
        
        for attempt in range(max_retries):
            try:
                if not mt5.initialize():
                    logger.error(f"MT5 init error (attempt {attempt + 1}): {mt5.last_error()}")
                    time.sleep(reconnect_delay)
                    continue
                
                authorized = mt5.login(
                    self.mt5_login,
                    self.mt5_password,
                    self.mt5_server
                )
                
                if not authorized:
                    logger.error(f"Auth error (attempt {attempt + 1}): {mt5.last_error()}")
                    mt5.shutdown()
                    time.sleep(reconnect_delay)
                    continue
                
                # Добавляем инструменты
                success_count = 0
                for pair in self.otc_instruments:
                    if mt5.symbol_select(pair, True):
                        success_count += 1
                
                logger.info(f"Connected to MT5. Added {success_count}/{len(self.otc_instruments)} instruments")
                self.mt5_initialized = True
                return True
                
            except Exception as e:
                logger.error(f"Connection error (attempt {attempt + 1}): {str(e)}")
                time.sleep(reconnect_delay)
        
        return False
    
    def get_market_data(self, symbol, timeframe, count=200):
        """Получение рыночных данных"""
        if not self.mt5_initialized and not self.initialize_mt5():
            logger.error("MT5 not initialized")
            return None
        
        try:
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
            if rates is None:
                logger.error(f"No data for {symbol}: {mt5.last_error()}")
                return None
            
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting data for {symbol}: {e}")
            return None
    
    def start(self):
        """Запуск бота"""
        if self.running:
            logger.warning("Bot already running")
            return
        
        if not self.initialize_mt5():
            logger.error("Failed to initialize MT5")
            return
        
        self.running = True
        
        # Запускаем рабочие потоки
        for i in range(3):  # 3 рабочих потока
            worker = threading.Thread(target=self._worker_loop, daemon=True)
            worker.start()
            self.workers.append(worker)
        
        logger.info("Trading bot started")
    
    def stop(self):
        """Остановка бота"""
        self.running = False
        
        # Ждем завершения рабочих потоков
        for worker in self.workers:
            if worker.is_alive():
                worker.join(timeout=5)
        
        mt5.shutdown()
        self.mt5_initialized = False
        logger.info("Trading bot stopped")
    
    def _worker_loop(self):
        """Цикл обработки сигналов"""
        while self.running:
            try:
                # Получаем задание из очереди
                task = self.signal_queue.get(timeout=1)
                if task is None:
                    continue
                
                # Обработка задания
                self._process_task(task)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
    
    def _process_task(self, task):
        """Обработка одного задания"""
        try:
            symbol = task.get('symbol')
            timeframe = task.get('timeframe')
            action = task.get('action')
            
            if action == 'analyze':
                self._analyze_symbol(symbol, timeframe)
            elif action == 'trade':
                self._execute_trade(symbol, task.get('trade_type'), task.get('amount'))
                
        except Exception as e:
            logger.error(f"Error processing task: {e}")
    
    def _analyze_symbol(self, symbol, timeframe):
        """Анализ символа"""
        try:
            # Получаем данные
            df = self.get_market_data(symbol, timeframe)
            if df is None or len(df) < 50:
                return
            
            # Рассчитываем индикаторы
            from .indicators import calculate_indicators
            indicators = calculate_indicators(df)
            
            # Генерируем сигнал
            from .signal_generator import generate_signal
            signal = generate_signal(df, indicators)
            
            if signal and signal.get('confidence', 0) > 0.7:
                # Сохраняем сигнал в БД
                from .database import save_signal
                with self.app.app_context():
                    save_signal(symbol, timeframe, signal)
                
                # Отправляем через WebSocket
                self.socketio.emit('new_signal', {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'signal': signal,
                    'timestamp': datetime.now().isoformat()
                })
                
                logger.info(f"Signal generated for {symbol} {timeframe}: {signal}")
                
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
    
    def _execute_trade(self, symbol, trade_type, amount):
        """Выполнение торговой операции"""
        try:
            if not self.mt5_initialized:
                logger.error("MT5 not initialized")
                return False
            
            symbol_info = mt5.symbol_info(symbol)
            if symbol_info is None:
                logger.error(f"Symbol {symbol} not found")
                return False
            
            # Получаем текущую цену
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                logger.error(f"No tick data for {symbol}")
                return False
            
            # Определяем тип ордера
            order_type = mt5.ORDER_TYPE_BUY if trade_type == 'buy' else mt5.ORDER_TYPE_SELL
            price = tick.ask if trade_type == 'buy' else tick.bid
            
            # Создаем ордер
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": amount,
                "type": order_type,
                "price": price,
                "deviation": 10,
                "magic": 234000,
                "comment": "Trading bot order",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Отправляем ордер
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Order failed: {result.comment}")
                return False
            
            logger.info(f"Trade executed: {symbol} {trade_type} {amount} at {price}")
            
            # Сохраняем в БД
            from .database import save_trade
            with self.app.app_context():
                save_trade(symbol, trade_type, price, amount, result.order)
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return False