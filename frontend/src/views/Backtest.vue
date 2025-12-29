<template>
  <div class="backtest-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">回测分析 Backtest & Performance</h1>
        <p class="page-desc">策略回测与绩效评估 - 回测统计、权益曲线、交易明细</p>
      </div>
      <button class="btn btn-primary" @click="runBacktest" :disabled="loading">
        {{ loading ? '运行中...' : '🔄 运行回测' }}
      </button>
    </div>

    <!-- 回测参数配置面板 -->
    <div class="card config-panel">
      <div class="card-header">
        <h3>⚙️ 回测参数配置</h3>
      </div>
      <div class="config-grid">
        <div class="config-item">
          <label>开始时间</label>
          <input 
            type="date" 
            v-model="params.startDate" 
            class="input"
            @change="onParamsChange"
          />
        </div>
        <div class="config-item">
          <label>结束时间</label>
          <input 
            type="date" 
            v-model="params.endDate" 
            class="input"
            @change="onParamsChange"
          />
        </div>
        <div class="config-item">
          <label>初始资金 (USDT)</label>
          <input 
            type="number" 
            v-model.number="params.initialCapital" 
            step="1000"
            min="1000"
            class="input"
            @change="onParamsChange"
          />
        </div>
        <div class="config-item">
          <label>交易规模 (USDT)</label>
          <input 
            type="number" 
            v-model.number="params.tradeSize" 
            step="1000"
            min="1000"
            class="input"
            @change="onParamsChange"
          />
        </div>
        <div class="config-item">
          <label>Z-Score阈值</label>
          <input 
            type="number" 
            v-model.number="params.zThreshold" 
            step="0.1"
            min="0"
            class="input"
            @change="onParamsChange"
          />
        </div>
        <div class="config-item">
          <label>CEX手续费 (%)</label>
          <input 
            type="number" 
            v-model.number="params.fees.cex" 
            step="0.001"
            min="0"
            class="input"
            @change="onParamsChange"
          />
        </div>
        <div class="config-item">
          <label>DEX手续费 (%)</label>
          <input 
            type="number" 
            v-model.number="params.fees.dex" 
            step="0.001"
            min="0"
            class="input"
            @change="onParamsChange"
          />
        </div>
        <div class="config-item">
          <label>Gas费用 (USDT)</label>
          <input 
            type="number" 
            v-model.number="params.fees.gas" 
            step="1"
            min="0"
            class="input"
            @change="onParamsChange"
          />
        </div>
      </div>
    </div>

    <!-- 回测统计面板 -->
    <div class="stats-module" v-if="results && results.totalTrades > 0">
      <h2 class="module-title">📊 回测统计</h2>
      <div class="stats-grid">
        <stat-card label="总交易次数" :value="results.totalTrades" type="number" :decimals="0" icon="📊" />
        <stat-card label="胜率" :value="results.winRate" type="percent" icon="🎯" />
        <stat-card label="总收益" :value="results.totalProfit" type="currency" unit="USDT" icon="💰" :value-color="'#19D3A2'" />
        <stat-card label="平均收益" :value="results.avgProfit" type="currency" unit="USDT" icon="📈" />
        <stat-card label="最大回撤" :value="results.maxDrawdown" type="percent" icon="📉" />
        <stat-card label="夏普比率" :value="results.sharpeRatio" type="number" :decimals="2" icon="⚡" />
        <stat-card label="盈亏比" :value="results.profitLossRatio" type="number" :decimals="2" icon="⚖️" />
        <stat-card label="最大连续盈利" :value="results.maxConsecutiveWins" type="number" :decimals="0" icon="🔥" />
      </div>
    </div>

    <!-- 权益曲线（增强版，叠加回撤曲线） -->
    <div class="card" v-if="results && results.equity && results.equity.length > 0">
      <div class="card-header">
        <h3>📈 权益曲线与回撤分析</h3>
      </div>
      <chart-card
        title=""
        :height="450"
        :options="equityCurveOptions"
        :loading="loading"
      />
    </div>

    <!-- 交易明细表 -->
    <div class="card" v-if="results && results.signals && results.signals.length > 0" style="margin-top: 24px;">
      <div class="card-header">
        <h3>📋 交易明细</h3>
        <div class="header-actions">
          <button class="btn btn-secondary btn-sm" @click="exportTrades">
            📥 导出CSV
          </button>
        </div>
      </div>
      <data-table
        :columns="tradeColumns"
        :data="sortedTrades"
        :max-height="500"
        :clickable="false"
      >
        <template #col-direction="{ value }">
          <span class="badge" :class="value === 'CEX->DEX' || value === 'Long' ? 'badge-primary' : 'badge-success'">
            {{ value }}
          </span>
        </template>
        
        <template #col-netProfit="{ value }">
          <span class="value-display" :class="value >= 0 ? 'positive' : 'negative'">
            {{ value >= 0 ? '+' : '' }}{{ value.toFixed(2) }}
          </span>
        </template>
        
        <template #col-time="{ value }">
          {{ formatTime(value) }}
        </template>
      </data-table>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading && !hasData" class="loading-state">
      <div class="loading-spinner"></div>
      <p>正在运行回测...</p>
    </div>

    <!-- 错误状态 -->
    <div v-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>回测失败</h3>
      <p>{{ error }}</p>
      <button class="btn btn-primary" @click="runBacktest">重试</button>
    </div>
  </div>
</template>

<script>
import ChartCard from '@/components/ChartCard.vue'
import StatCard from '@/components/StatCard.vue'
import DataTable from '@/components/DataTable.vue'
import apiClient from '@/utils/api'

export default {
  name: 'Backtest',
  components: { 
    ChartCard, 
    StatCard,
    DataTable
  },

  data() {
    return {
      loading: false,
      error: null,
      hasData: false,
      
      results: {
        totalTrades: 0,
        winningTrades: 0,
        winRate: 0,
        totalProfit: 0,
        avgProfit: 0,
        maxDrawdown: 0,
        sharpeRatio: 0,
        profitLossRatio: 0,
        maxConsecutiveWins: 0,
        equity: [],
        signals: []
      },

      params: {
        startDate: '2025-09-01',
        endDate: '2025-09-30',
        initialCapital: 100000,
        tradeSize: 10000,
        zThreshold: 2.0,
        fees: {
          cex: 0.001,
          dex: 0.003,
          gas: 15
        }
      },

      tradeColumns: [
        { key: 'time', label: '时间', type: 'time', width: '160px' },
        { key: 'direction', label: '方向', width: '120px' },
        { key: 'spread', label: '价差', type: 'number', decimals: 2, sortable: true },
        { key: 'netProfit', label: '净利润', type: 'number', decimals: 2, sortable: true },
        { key: 'confidence', label: '置信度', type: 'number', decimals: 2, sortable: true },
        { key: 'zScore', label: 'Z-Score', type: 'number', decimals: 2, sortable: true }
      ],

      sortBy: 'time',
      sortOrder: 'desc'
    }
  },

  computed: {
    sortedTrades() {
      if (!this.results.signals || this.results.signals.length === 0) return []
      
      const sorted = [...this.results.signals]
      
      sorted.sort((a, b) => {
        let aVal, bVal
        
        switch (this.sortBy) {
          case 'netProfit':
            aVal = a.netProfit || 0
            bVal = b.netProfit || 0
            break
          case 'confidence':
            aVal = a.confidence || 0
            bVal = b.confidence || 0
            break
          case 'zScore':
            aVal = a.zScore || 0
            bVal = b.zScore || 0
            break
          case 'time':
          default:
            aVal = a.time || 0
            bVal = b.time || 0
        }
        
        if (this.sortOrder === 'asc') {
          return aVal > bVal ? 1 : -1
        } else {
          return aVal < bVal ? 1 : -1
        }
      })
      
      return sorted
    },

    equityCurveOptions() {
      if (!this.results.equity || this.results.equity.length === 0) return {}

      const equityData = this.results.equity.map(e => [e.time * 1000, e.equity])
      
      // 计算回撤曲线
      const drawdownData = []
      let peak = this.results.equity[0]?.equity || 0
      this.results.equity.forEach(e => {
        if (e.equity > peak) peak = e.equity
        const drawdown = ((peak - e.equity) / peak) * 100
        drawdownData.push([e.time * 1000, -drawdown])
      })

      return {
        tooltip: { 
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e5e7eb',
          textStyle: { color: '#111827' },
          formatter: (params) => {
            if (!params || !params.length) return ''
            let result = ''
            params.forEach(param => {
              if (param.seriesName === '权益曲线') {
                const date = new Date(param.data[0])
                const value = typeof param.data[1] === 'number' ? param.data[1] : (Array.isArray(param.value) ? param.value[1] : param.value)
                result += `${date.toLocaleString('zh-CN')}<br/>权益: ${Number(value).toFixed(2)} USDT<br/>`
              } else if (param.seriesName === '回撤曲线') {
                const date = new Date(param.data[0])
                const value = typeof param.data[1] === 'number' ? Math.abs(param.data[1]) : (Array.isArray(param.value) ? Math.abs(param.value[1]) : Math.abs(param.value))
                result += `回撤: ${Number(value).toFixed(2)}%`
              }
            })
            return result
          }
        },
        legend: {
          data: ['权益曲线', '回撤曲线'],
          top: 10,
          textStyle: { color: '#6b7280' }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'time',
          axisLabel: { 
            color: '#6b7280',
            formatter: (value) => {
              const date = new Date(value)
              return `${date.getMonth()+1}/${date.getDate()}`
            }
          }
        },
        yAxis: [
          {
            type: 'value',
            name: '权益 (USDT)',
            nameTextStyle: { color: '#6b7280' },
            axisLabel: { color: '#6b7280' },
            splitLine: { lineStyle: { color: '#f3f4f6' } }
          },
          {
            type: 'value',
            name: '回撤 (%)',
            nameTextStyle: { color: '#6b7280' },
            axisLabel: { 
              color: '#6b7280',
              formatter: (value) => value.toFixed(1) + '%'
            },
            splitLine: { show: false }
          }
        ],
        series: [
          {
            name: '权益曲线',
            type: 'line',
            data: equityData,
            smooth: true,
            symbol: 'none',
            lineStyle: { color: '#19D3A2', width: 3 },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(25, 211, 162, 0.3)' },
                  { offset: 1, color: 'rgba(25, 211, 162, 0.05)' }
                ]
              }
            }
          },
          {
            name: '回撤曲线',
            type: 'line',
            yAxisIndex: 1,
            data: drawdownData,
            smooth: true,
            symbol: 'none',
            lineStyle: { color: '#ef4444', width: 2 },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(239, 68, 68, 0.2)' },
                  { offset: 1, color: 'rgba(239, 68, 68, 0.05)' }
                ]
              }
            }
          }
        ]
      }
    },

  },

  mounted() {
    this.runBacktest()
  },

  methods: {
    // 将日期转换为时间戳（秒）
    dateToTimestamp(dateStr) {
      return Math.floor(new Date(dateStr).getTime() / 1000)
    },

    // 运行回测
    async runBacktest() {
      this.loading = true
      this.error = null
      this.hasData = false

      try {
        const start = this.dateToTimestamp(this.params.startDate)
        const end = this.dateToTimestamp(this.params.endDate) + 86400 - 1

        // 调用后端API获取回测结果
        const backtestStats = await apiClient.getBacktestStats(
          start, 
          end, 
          this.params.zThreshold, 
          this.params.tradeSize
        )

        // 获取信号列表用于交易明细
        const signals = await apiClient.getSignals(
          start, 
          end, 
          this.params.zThreshold, 
          this.params.tradeSize
        )

        // 处理回测结果
        this.results = {
          ...backtestStats,
          signals: signals || []
        }

        // 计算额外指标
        this.calculateAdditionalMetrics()

        this.hasData = true
      } catch (error) {
        console.error('回测失败:', error)
        this.error = error.message || '回测失败，请检查后端服务是否正常运行'
        this.results = {
          totalTrades: 0,
          winningTrades: 0,
          winRate: 0,
          totalProfit: 0,
          avgProfit: 0,
          maxDrawdown: 0,
          sharpeRatio: 0,
          profitLossRatio: 0,
          maxConsecutiveWins: 0,
          equity: [],
          signals: []
        }
      } finally {
        this.loading = false
      }
    },

    // 计算额外指标
    calculateAdditionalMetrics() {
      if (!this.results.signals || this.results.signals.length === 0) return

      const profits = this.results.signals.map(s => s.netProfit || 0)
      const winningTrades = profits.filter(p => p > 0)
      const losingTrades = profits.filter(p => p < 0)

      // 盈亏比
      const avgWin = winningTrades.length > 0 
        ? winningTrades.reduce((a, b) => a + b, 0) / winningTrades.length 
        : 0
      const avgLoss = losingTrades.length > 0 
        ? Math.abs(losingTrades.reduce((a, b) => a + b, 0) / losingTrades.length)
        : 0
      this.results.profitLossRatio = avgLoss > 0 ? avgWin / avgLoss : 0

      // 最大连续盈利
      let maxConsecutiveWins = 0
      let currentWins = 0

      profits.forEach(p => {
        if (p > 0) {
          currentWins++
          maxConsecutiveWins = Math.max(maxConsecutiveWins, currentWins)
        } else {
          currentWins = 0
        }
      })

      this.results.maxConsecutiveWins = maxConsecutiveWins
    },

    // 参数变化时重新运行回测
    onParamsChange() {
      this.runBacktest()
    },

    // 格式化时间
    formatTime(timestamp) {
      if (!timestamp) return '-'
      const timeMs = (timestamp || 0) * 1000
      return new Date(timeMs).toLocaleString('zh-CN')
    },

    // 导出交易明细
    exportTrades() {
      if (!this.results.signals || this.results.signals.length === 0) return

      const header = '时间,方向,价差,净利润,置信度,Z-Score\n'
      const rows = this.results.signals.map(s => {
        const timeMs = (s.time || 0) * 1000
        return `${new Date(timeMs).toISOString()},${s.direction},${s.spread || 0},${s.netProfit || 0},${s.confidence || 0},${s.zScore || 0}`
      }).join('\n')
      
      const csv = header + rows
      const blob = new Blob([csv], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `backtest_trades_${Date.now()}.csv`
      link.click()
      URL.revokeObjectURL(url)
    }
  }
}
</script>

<style lang="scss" scoped>
.backtest-page {
  min-height: 100vh;
  background: $bg-primary;
  padding: 24px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  .page-title {
    font-size: 32px;
    font-weight: 700;
    color: $text-primary;
    margin: 0 0 8px 0;
  }

  .page-desc {
    font-size: 16px;
    color: $text-secondary;
    margin: 0;
  }
}

.config-panel {
  margin-bottom: 24px;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  padding: 20px;
}

.config-item {
  display: flex;
  flex-direction: column;
  gap: 8px;

  label {
    font-size: 13px;
    color: $text-secondary;
    font-weight: 500;
  }
}

.stats-module {
  margin-bottom: 24px;

  .module-title {
    font-size: 20px;
    font-weight: 600;
    color: $text-primary;
    margin-bottom: 16px;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.analysis-module {
  margin-top: 24px;
  margin-bottom: 24px;

  .module-title {
    font-size: 20px;
    font-weight: 600;
    color: $text-primary;
    margin-bottom: 16px;
  }
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 16px;
}

.chart-widget {
  background: $bg-card;
  border-radius: $border-radius;
  padding: 20px;
  box-shadow: $shadow-sm;

  .widget-header {
    margin-bottom: 16px;

    h4 {
      font-size: 16px;
      font-weight: 600;
      color: $text-primary;
      margin: 0;
    }
  }
}

.card {
  background: $bg-card;
  border-radius: $border-radius;
  padding: 20px;
  box-shadow: $shadow-sm;
  margin-bottom: 24px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    h3 {
      font-size: 18px;
      font-weight: 600;
      color: $text-primary;
      margin: 0;
    }
  }
}

.header-actions {
  display: flex;
  gap: 8px;
}

.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;

  &.badge-primary {
    background: rgba(59, 130, 246, 0.15);
    color: #3b82f6;
  }

  &.badge-success {
    background: rgba(16, 185, 129, 0.15);
    color: #10b981;
  }
}

.value-display {
  font-weight: 600;

  &.positive {
    color: $color-success;
  }

  &.negative {
    color: $color-danger;
  }
}

.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;

  .loading-spinner {
    width: 48px;
    height: 48px;
    border: 4px solid $border-color;
    border-top-color: $color-primary;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 16px;
  }

  .error-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }

  h3 {
    font-size: 20px;
    color: $text-primary;
    margin-bottom: 8px;
  }

  p {
    color: $text-secondary;
    margin-bottom: 16px;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
