import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { io } from 'socket.io-client'

export const useTradingStore = defineStore('trading', () => {
  // State
  const user = ref(null)
  const isAuthenticated = ref(false)
  const token = ref(null)
  const signals = ref([])
  const trades = ref([])
  const botRunning = ref(false)
  const socket = ref(null)
  
  // Getters
  const activeSignalsCount = computed(() => {
    return signals.value.filter(s => s.status === 'active').length
  })
  
  const recentSignals = computed(() => {
    return signals.value.slice(0, 5)
  })
  
  const dailyProfit = computed(() => {
    const today = new Date().toISOString().split('T')[0]
    return trades.value
      .filter(t => t.closed_at && t.closed_at.startsWith(today))
      .reduce((sum, t) => sum + (t.profit_loss || 0), 0)
  })
  
  // Actions
  const initialize = async () => {
    // Проверяем наличие токена в localStorage
    const savedToken = localStorage.getItem('trading_token')
    if (savedToken) {
      token.value = savedToken
      isAuthenticated.value = true
      
      // Настраиваем axios
      axios.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`
      
      // Загружаем данные пользователя
      await loadUserData()
      
      // Подключаемся к WebSocket
      connectWebSocket()
    }
    
    // Загружаем сигналы и сделки
    await loadSignals()
    await loadTrades()
    
    // Проверяем статус бота
    await checkBotStatus()
  }
  
  const authenticate = async (telegramData) => {
    try {
      const response = await axios.post('/api/auth/telegram', telegramData)
      
      token.value = response.data.token
      user.value = response.data.user
      isAuthenticated.value = true
      
      // Сохраняем токен
      localStorage.setItem('trading_token', token.value)
      
      // Настраиваем axios
      axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
      
      // Подключаемся к WebSocket
      connectWebSocket()
      
      return true
    } catch (error) {
      console.error('Authentication error:', error)
      return false
    }
  }
  
  const logout = () => {
    user.value = null
    isAuthenticated.value = false
    token.value = null
    signals.value = []
    trades.value = []
    
    // Удаляем токен
    localStorage.removeItem('trading_token')
    
    // Отключаем WebSocket
    if (socket.value) {
      socket.value.disconnect()
      socket.value = null
    }
    
    // Удаляем заголовок авторизации
    delete axios.defaults.headers.common['Authorization']
  }
  
  const loadUserData = async () => {
    try {
      const response = await axios.get('/api/user/profile')
      user.value = response.data.user
    } catch (error) {
      console.error('Error loading user data:', error)
    }
  }
  
  const loadSignals = async () => {
    try {
      const response = await axios.get('/api/signals')
      signals.value = response.data.signals
    } catch (error) {
      console.error('Error loading signals:', error)
    }
  }
  
  const loadTrades = async () => {
    try {
      const response = await axios.get('/api/trades')
      trades.value = response.data.trades
    } catch (error) {
      console.error('Error loading trades:', error)
    }
  }
  
  const analyzeMarket = async (symbol, timeframe) => {
    try {
      const response = await axios.post('/api/market/analyze', {
        symbol,
        timeframe
      })
      return response.data
    } catch (error) {
      console.error('Error analyzing market:', error)
      throw error
    }
  }
  
  const startBot = async () => {
    try {
      const response = await axios.post('/api/bot/start')
      botRunning.value = true
      return response.data
    } catch (error) {
      console.error('Error starting bot:', error)
      throw error
    }
  }
  
  const stopBot = async () => {
    try {
      const response = await axios.post('/api/bot/stop')
      botRunning.value = false
      return response.data
    } catch (error) {
      console.error('Error stopping bot:', error)
      throw error
    }
  }
  
  const checkBotStatus = async () => {
    try {
      const response = await axios.get('/api/bot/status')
      botRunning.value = response.data.running
    } catch (error) {
      console.error('Error checking bot status:', error)
    }
  }
  
  const fetchMarketData = async (symbol, timeframe, limit = 100) => {
    try {
      // Заглушка - в реальном приложении здесь будет запрос к API
      return {
        labels: Array.from({ length: limit }, (_, i) => i),
        prices: Array.from({ length: limit }, () => 
          Math.random() * 100 + 100
        )
      }
    } catch (error) {
      console.error('Error fetching market data:', error)
      throw error
    }
  }
  
  const connectWebSocket = () => {
    if (!token.value || socket.value) return
    
    socket.value = io({
      auth: {
        token: token.value
      },
      transports: ['websocket']
    })
    
    socket.value.on('connect', () => {
      console.log('WebSocket connected')
    })
    
    socket.value.on('disconnect', () => {
      console.log('WebSocket disconnected')
    })
    
    socket.value.on('new_signal', (data) => {
      console.log('New signal received:', data)
      
      // Добавляем сигнал в начало списка
      signals.value.unshift(data.signal)
      
      // Ограничиваем количество сигналов
      if (signals.value.length > 50) {
        signals.value = signals.value.slice(0, 50)
      }
    })
    
    socket.value.on('trade_update', (data) => {
      console.log('Trade update received:', data)
      
      // Обновляем сделку
      const index = trades.value.findIndex(t => t.id === data.trade.id)
      if (index !== -1) {
        trades.value[index] = data.trade
      } else {
        trades.value.unshift(data.trade)
      }
    })
    
    socket.value.on('error', (error) => {
      console.error('WebSocket error:', error)
    })
  }
  
  return {
    // State
    user,
    isAuthenticated,
    signals,
    trades,
    botRunning,
    
    // Getters
    activeSignalsCount,
    recentSignals,
    dailyProfit,
    
    // Actions
    initialize,
    authenticate,
    logout,
    loadSignals,
    loadTrades,
    analyzeMarket,
    startBot,
    stopBot,
    checkBotStatus,
    fetchMarketData
  }
})
