<template>
  <div class="dashboard">
    <!-- Заголовок -->
    <header class="dashboard-header">
      <div class="user-info">
        <div class="avatar" :style="{ backgroundColor: userColor }">
          {{ userInitials }}
        </div>
        <div class="user-details">
          <h2>{{ user.username || 'Трейдер' }}</h2>
          <p class="balance">Баланс: <span>{{ formatCurrency(balance) }}</span></p>
        </div>
      </div>
      <div class="status-indicator" :class="botStatusClass">
        {{ botStatusText }}
      </div>
    </header>

    <!-- Быстрая статистика -->
    <div class="quick-stats">
      <div class="stat-card" @click="goToSignals">
        <div class="stat-icon">���</div>
        <div class="stat-content">
          <h3>Активные сигналы</h3>
          <p class="stat-value">{{ activeSignals }}</p>
        </div>
      </div>
      
      <div class="stat-card" @click="goToStatistics">
        <div class="stat-icon">���</div>
        <div class="stat-content">
          <h3>Прибыль сегодня</h3>
          <p class="stat-value" :class="dailyProfit >= 0 ? 'positive' : 'negative'">
            {{ formatCurrency(dailyProfit) }}
          </p>
        </div>
      </div>
    </div>

    <!-- График -->
    <div class="chart-section">
      <div class="section-header">
        <h3>Активный график</h3>
        <select v-model="selectedSymbol" @change="updateChart">
          <option v-for="symbol in popularSymbols" :key="symbol" :value="symbol">
            {{ symbol }}
          </option>
        </select>
      </div>
      <div class="chart-container">
        <canvas ref="chartCanvas"></canvas>
      </div>
      <div class="chart-controls">
        <button @click="changeTimeframe('M1')" :class="{ active: timeframe === 'M1' }">1M</button>
        <button @click="changeTimeframe('M5')" :class="{ active: timeframe === 'M5' }">5M</button>
        <button @click="changeTimeframe('M15')" :class="{ active: timeframe === 'M15' }">15M</button>
        <button @click="changeTimeframe('H1')" :class="{ active: timeframe === 'H1' }">1H</button>
      </div>
    </div>

    <!-- Быстрые действия -->
    <div class="quick-actions">
      <button class="action-btn" @click="analyzeMarket" :disabled="analyzing">
        <span v-if="analyzing">⏳</span>
        <span v-else>���</span>
        Анализировать рынок
      </button>
      
      <button class="action-btn" @click="toggleBot" :class="{ 'bot-active': botRunning }">
        <span v-if="botRunning">⏸️</span>
        <span v-else>▶️</span>
        {{ botRunning ? 'Остановить бота' : 'Запустить бота' }}
      </button>
    </div>

    <!-- Последние сигналы -->
    <div class="recent-signals">
      <h3>Последние сигналы</h3>
      <div v-if="recentSignals.length === 0" class="no-signals">
        <p>Нет активных сигналов</p>
      </div>
      <div v-else>
        <div v-for="signal in recentSignals" :key="signal.id" 
             class="signal-item" :class="signal.signal_type">
          <div class="signal-info">
            <span class="symbol">{{ signal.symbol }}</span>
            <span class="timeframe">{{ signal.timeframe }}</span>
            <span class="signal-type" :class="signal.signal_type">
              {{ signal.signal_type === 'buy' ? '��� ПОКУПКА' : '��� ПРОДАЖА' }}
            </span>
          </div>
          <div class="signal-details">
            <span class="price">{{ formatPrice(signal.entry_price) }}</span>
            <span class="probability" :class="getProbabilityClass(signal.probability)">
              {{ signal.probability }}%
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTradingStore } from '@/stores/trading'
import Chart from 'chart.js/auto'

export default {
  name: 'Dashboard',
  
  setup() {
    const router = useRouter()
    const store = useTradingStore()
    
    const chartCanvas = ref(null)
    const chartInstance = ref(null)
    const selectedSymbol = ref('EURUSD')
    const timeframe = ref('M5')
    const analyzing = ref(false)
    
    // Пользовательские данные
    const user = computed(() => store.user)
    const userInitials = computed(() => {
      if (!user.value.first_name && !user.value.last_name) return 'U'
      return ((user.value.first_name?.[0] || '') + (user.value.last_name?.[0] || '')).toUpperCase()
    })
    const userColor = computed(() => {
      const colors = ['#667eea', '#764ba2', '#f56565', '#48bb78', '#ed8936']
      const index = (user.value.id || 0) % colors.length
      return colors[index]
    })
    
    // Статистика
    const balance = computed(() => store.balance || 1000)
    const activeSignals = computed(() => store.activeSignalsCount || 0)
    const dailyProfit = computed(() => store.dailyProfit || 0)
    const botRunning = computed(() => store.botRunning)
    const recentSignals = computed(() => store.recentSignals || [])
    
    // Статус бота
    const botStatusClass = computed(() => ({
      'status-online': botRunning.value,
      'status-offline': !botRunning.value
    }))
    
    const botStatusText = computed(() => 
      botRunning.value ? 'Бот активен' : 'Бот остановлен'
    )
    
    // Популярные символы
    const popularSymbols = [
      'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD',
      'AUDUSD', 'NZDUSD', 'XAUUSD', 'BTCUSD'
    ]
    
    // Методы
    const formatCurrency = (value) => {
      return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
      }).format(value)
    }
    
    const formatPrice = (price) => {
      return price.toFixed(5)
    }
    
    const getProbabilityClass = (probability) => {
      if (probability >= 80) return 'high'
      if (probability >= 60) return 'medium'
      return 'low'
    }
    
    const goToSignals = () => {
      router.push('/signals')
    }
    
    const goToStatistics = () => {
      router.push('/statistics')
    }
    
    const updateChart = async () => {
      if (!chartCanvas.value) return
      
      try {
        const data = await store.fetchMarketData(selectedSymbol.value, timeframe.value)
        
        if (chartInstance.value) {
          chartInstance.value.destroy()
        }
        
        const ctx = chartCanvas.value.getContext('2d')
        chartInstance.value = new Chart(ctx, {
          type: 'line',
          data: {
            labels: data.labels,
            datasets: [{
              label: selectedSymbol.value,
              data: data.prices,
              borderColor: '#667eea',
              backgroundColor: 'rgba(102, 126, 234, 0.1)',
              borderWidth: 2,
              fill: true,
              tension: 0.4
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: false
              }
            },
            scales: {
              x: {
                display: false
              },
              y: {
                beginAtZero: false,
                grid: {
                  color: 'rgba(0, 0, 0, 0.1)'
                }
              }
            }
          }
        })
      } catch (error) {
        console.error('Error updating chart:', error)
      }
    }
    
    const changeTimeframe = (tf) => {
      timeframe.value = tf
      updateChart()
    }
    
    const analyzeMarket = async () => {
      analyzing.value = true
      try {
        await store.analyzeMarket(selectedSymbol.value, timeframe.value)
      } finally {
        analyzing.value = false
      }
    }
    
    const toggleBot = async () => {
      if (botRunning.value) {
        await store.stopBot()
      } else {
        await store.startBot()
      }
    }
    
    // Жизненный цикл
    onMounted(async () => {
      await store.initialize()
      await updateChart()
    })
    
    onUnmounted(() => {
      if (chartInstance.value) {
        chartInstance.value.destroy()
      }
    })
    
    return {
      // Refs
      chartCanvas,
      selectedSymbol,
      timeframe,
      analyzing,
      
      // Computed
      user,
      userInitials,
      userColor,
      balance,
      activeSignals,
      dailyProfit,
      botRunning,
      recentSignals,
      botStatusClass,
      botStatusText,
      popularSymbols,
      
      // Methods
      formatCurrency,
      formatPrice,
      getProbabilityClass,
      goToSignals,
      goToStatistics,
      updateChart,
      changeTimeframe,
      analyzeMarket,
      toggleBot
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
  max-width: 100%;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 24px;
}

.user-details h2 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.balance {
  margin: 5px 0 0;
  font-size: 14px;
  color: #666;
}

.balance span {
  font-weight: bold;
  color: #48bb78;
}

.status-indicator {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.status-online {
  background: #48bb78;
  color: white;
}

.status-offline {
  background: #e2e8f0;
  color: #718096;
}

.quick-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  font-size: 30px;
}

.stat-content h3 {
  margin: 0 0 5px;
  font-size: 14px;
  color: #718096;
}

.stat-value {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
  color: #2d3748;
}

.stat-value.positive {
  color: #48bb78;
}

.stat-value.negative {
  color: #f56565;
}

.chart-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.section-header select {
  padding: 8px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  background: white;
  color: #333;
  font-weight: 600;
  outline: none;
  cursor: pointer;
}

.chart-container {
  height: 300px;
  position: relative;
}

.chart-controls {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
}

.chart-controls button {
  padding: 8px 20px;
  border: 2px solid #e2e8f0;
  background: white;
  border-radius: 10px;
  font-weight: 600;
  color: #718096;
  cursor: pointer;
  transition: all 0.3s;
}

.chart-controls button:hover {
  border-color: #667eea;
  color: #667eea;
}

.chart-controls button.active {
  background: #667eea;
  border-color: #667eea;
  color: white;
}

.quick-actions {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
}

.action-btn {
  flex: 1;
  padding: 16px;
  border: none;
  border-radius: 15px;
  background: white;
  color: #333;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.action-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn.bot-active {
  background: #48bb78;
  color: white;
}

.recent-signals {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.recent-signals h3 {
  margin: 0 0 20px;
  font-size: 18px;
  color: #333;
}

.no-signals {
  text-align: center;
  padding: 40px 20px;
  color: #718096;
}

.signal-item {
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 10px;
  background: #f7fafc;
  transition: transform 0.3s;
}

.signal-item:hover {
  transform: translateX(5px);
}

.signal-item.buy {
  border-left: 4px solid #48bb78;
}

.signal-item.sell {
  border-left: 4px solid #f56565;
}

.signal-info {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}

.symbol {
  font-weight: bold;
  color: #333;
}

.timeframe {
  color: #718096;
  font-size: 14px;
}

.signal-type {
  font-weight: 600;
  font-size: 14px;
}

.signal-type.buy {
  color: #48bb78;
}

.signal-type.sell {
  color: #f56565;
}

.signal-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price {
  font-weight: bold;
  color: #333;
}

.probability {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.probability.high {
  background: #48bb78;
  color: white;
}

.probability.medium {
  background: #ed8936;
  color: white;
}

.probability.low {
  background: #f56565;
  color: white;
}
</style>
