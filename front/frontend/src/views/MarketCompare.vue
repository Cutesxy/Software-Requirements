<template>
  <div class="market-compare-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">数据分析中心</h1>
        <p class="page-desc">市场数据探索与分析 - 价差特征、价格对比、数据可视化</p>
        </div>
      <div class="header-actions">
        <button class="btn btn-primary" @click="loadData" :disabled="loading">
          {{ loading ? '加载中...' : '🔄 刷新数据' }}
        </button>
        </div>
      </div>

    <!-- 参数配置面板 -->
    <div class="card config-panel">
      <div class="card-header">
        <h3>⚙️ 分析参数配置</h3>
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
    </div>
          </div>

    <!-- 信号分析模块 -->
    <div class="signals-module" v-if="signals && signals.length > 0">
      <h2 class="module-title">🎯 套利信号分析</h2>
      <div class="signals-stats">
        <div class="signal-stat-card">
          <div class="signal-stat-label">信号总数</div>
          <div class="signal-stat-value">{{ signals.length }}</div>
              </div>
        <div class="signal-stat-card">
          <div class="signal-stat-label">平均价差</div>
          <div class="signal-stat-value">{{ formatCurrency(avgSpread) }}</div>
            </div>
        <div class="signal-stat-card">
          <div class="signal-stat-label">平均净利润</div>
          <div class="signal-stat-value success">{{ formatCurrency(avgNetProfit) }}</div>
          </div>
        <div class="signal-stat-card">
          <div class="signal-stat-label">平均置信度</div>
          <div class="signal-stat-value">{{ formatPercent(avgConfidence) }}</div>
            </div>
          </div>

      <!-- 信号分布图表 -->
      <div class="charts-grid">
          <div class="chart-widget">
            <div class="widget-header">
            <h4>📊 信号时间分布</h4>
            </div>
            <chart-card
              title=""
            :height="300"
            :options="signalsTimeDistributionOptions"
              :loading="loading"
            />
          </div>
      </div>
          </div>

    <!-- 价差分析模块 -->
    <div class="spread-module" v-if="spreadData && spreadData.length > 0">
      <h2 class="module-title">📉 价差分析</h2>
      <div class="charts-grid">
          <div class="chart-widget">
            <div class="widget-header">
            <h4>📊 价差趋势</h4>
            </div>
            <chart-card
              title=""
            :height="350"
            :options="spreadTrendOptions"
              :loading="loading"
            />
          </div>

          <div class="chart-widget">
            <div class="widget-header">
            <h4>📈 价差分布</h4>
            </div>
            <chart-card
              title=""
            :height="350"
            :options="spreadHistogramOptions"
              :loading="loading"
            />
          </div>
            </div>
          </div>

    <!-- 价格对比模块 -->
    <div class="price-module" v-if="priceData">
      <h2 class="module-title">💹 价格对比</h2>
      <div class="card">
        <chart-card
          title="CEX vs DEX 价格对比"
          :height="400"
          :options="priceCompareOptions"
          :loading="loading"
        />
              </div>
            </div>


    <!-- 加载状态 -->
    <div v-if="loading && !hasData" class="loading-state">
      <div class="loading-spinner"></div>
      <p>正在加载数据...</p>
          </div>

    <!-- 错误状态 -->
    <div v-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>数据加载失败</h3>
      <p>{{ error }}</p>
      <button class="btn btn-primary" @click="loadData">重试</button>
    </div>
  </div>
</template>

<script>
import ChartCard from '@/components/ChartCard.vue'
import apiClient from '@/utils/api'

export default {
  name: 'MarketCompare',
  components: {
    ChartCard
  },

  data() {
    return {
      loading: false,
      error: null,
      hasData: false,
      
      // API数据
      signals: null,
      spreadData: null,
      priceData: null,

      // 参数配置
      params: {
        startDate: '2025-09-01',
        endDate: '2025-09-30',
        zThreshold: 2.0,
        tradeSize: 10000
      }
    }
  },

  computed: {
    // 平均价差
    avgSpread() {
      if (!this.signals || this.signals.length === 0) return 0
      const sum = this.signals.reduce((acc, s) => acc + Math.abs(s.spread || 0), 0)
      return sum / this.signals.length
    },

    // 平均净利润
    avgNetProfit() {
      if (!this.signals || this.signals.length === 0) return 0
      const sum = this.signals.reduce((acc, s) => acc + (s.netProfit || 0), 0)
      return sum / this.signals.length
    },

    // 平均置信度
    avgConfidence() {
      if (!this.signals || this.signals.length === 0) return 0
      const sum = this.signals.reduce((acc, s) => acc + (s.confidence || 0), 0)
      return sum / this.signals.length
    },

    // 信号时间分布图表
    signalsTimeDistributionOptions() {
      if (!this.signals || this.signals.length === 0) return {}

      // 按小时统计信号数量
      const hourCounts = new Array(24).fill(0)
      this.signals.forEach(s => {
        const hour = new Date(s.time * 1000).getHours()
        hourCounts[hour]++
      })

      return {
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e5e7eb',
          textStyle: { color: '#111827' }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '10%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: Array.from({ length: 24 }, (_, i) => `${i}:00`),
          axisLabel: { color: '#6b7280', interval: 2 }
        },
        yAxis: {
          type: 'value',
          name: '信号数量',
          axisLabel: { color: '#6b7280' },
          splitLine: { lineStyle: { color: '#f3f4f6' } }
        },
        series: [{
            type: 'bar',
          data: hourCounts,
            itemStyle: { 
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: '#3b82f6' },
                  { offset: 1, color: '#60a5fa' }
                ]
              },
            borderRadius: [4, 4, 0, 0]
          }
        }]
      }
    },

    // 价差趋势图表
    spreadTrendOptions() {
      if (!this.spreadData || this.spreadData.length === 0) return {}

      const data = this.spreadData.map(d => [d.t * 1000, d.spread])

      return {
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e5e7eb',
          textStyle: { color: '#111827' }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '10%',
          containLabel: true
        },
        xAxis: {
          type: 'time',
          axisLabel: { 
            color: '#6b7280',
            formatter: (value) => {
              const date = new Date(value)
              return `${date.getMonth()+1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
            }
          }
        },
        yAxis: {
          type: 'value',
          name: '价差 (USDT)',
          nameTextStyle: { color: '#6b7280' },
          axisLabel: { color: '#6b7280' },
          splitLine: { lineStyle: { color: '#f3f4f6' } }
        },
        series: [{
          type: 'line',
          data: data,
          smooth: true,
          symbol: 'none',
          lineStyle: { color: '#f97316', width: 2 },
          areaStyle: {
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                { offset: 0, color: 'rgba(249, 115, 22, 0.3)' },
                { offset: 1, color: 'rgba(249, 115, 22, 0.05)' }
              ]
            }
          }
        }]
      }
    },

    // 价差分布直方图
    spreadHistogramOptions() {
      if (!this.spreadData || this.spreadData.length === 0) return {}

      const spreads = this.spreadData.map(d => d.spread).filter(s => s !== null && s !== undefined)
      if (spreads.length === 0) return {}

      const min = Math.min(...spreads)
      const max = Math.max(...spreads)
      const bins = 30
      const binWidth = (max - min) / bins
      const histogram = new Array(bins).fill(0)

      spreads.forEach(s => {
        const binIndex = Math.min(Math.floor((s - min) / binWidth), bins - 1)
        histogram[binIndex]++
      })

      const data = histogram.map((count, i) => [min + i * binWidth, count])

      return {
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e5e7eb',
          textStyle: { color: '#111827' }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '10%',
          containLabel: true
        },
        xAxis: {
          type: 'value',
          name: '价差 (USDT)',
          nameTextStyle: { color: '#6b7280' },
          axisLabel: { color: '#6b7280' }
        },
        yAxis: {
          type: 'value',
          name: '频次',
          nameTextStyle: { color: '#6b7280' },
          axisLabel: { color: '#6b7280' },
          splitLine: { lineStyle: { color: '#f3f4f6' } }
        },
        series: [{
          type: 'bar',
          data: data,
          itemStyle: { color: '#8b5cf6' },
          barWidth: '80%'
        }]
      }
    },

    // 价格对比图表
    priceCompareOptions() {
      if (!this.priceData || !this.priceData.cex || !this.priceData.dex) return {}

      const cexData = this.priceData.cex.map(d => [d.t * 1000, d.p])
      const dexData = this.priceData.dex.map(d => [d.t * 1000, d.p])

      return {
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e5e7eb',
          textStyle: { color: '#111827' }
        },
        legend: {
          data: ['CEX价格', 'DEX价格'],
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
              return `${date.getMonth()+1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
            }
          }
        },
        yAxis: {
          type: 'value',
          name: '价格 (USDT)',
          nameTextStyle: { color: '#6b7280' },
          axisLabel: { color: '#6b7280' },
          splitLine: { lineStyle: { color: '#f3f4f6' } }
        },
        series: [
          {
            name: 'CEX价格',
            type: 'line',
            data: cexData,
            smooth: true,
            symbol: 'none',
            lineStyle: { color: '#10b981', width: 2 }
          },
          {
            name: 'DEX价格',
            type: 'line',
            data: dexData,
            smooth: true,
            symbol: 'none',
            lineStyle: { color: '#3b82f6', width: 2 }
          }
        ]
      }
    },

  },

  mounted() {
    this.loadData()
  },

  methods: {
    // 将日期转换为时间戳（秒）
    dateToTimestamp(dateStr) {
      return Math.floor(new Date(dateStr).getTime() / 1000)
    },

    // 加载所有数据
    async loadData() {
      this.loading = true
      this.error = null
      this.hasData = false

      try {
        const start = this.dateToTimestamp(this.params.startDate)
        const end = this.dateToTimestamp(this.params.endDate) + 86400 - 1 // 当天的最后一秒

        // 并行加载所有数据（不再加载回测统计）
        const [signals, spreadData, priceData] = await Promise.all([
          apiClient.getSignals(start, end, this.params.zThreshold, this.params.tradeSize),
          apiClient.getSpreadData(start, end),
          apiClient.getPriceData(start, end)
        ])

        this.signals = signals
        this.spreadData = spreadData
        this.priceData = priceData

        this.hasData = true
      } catch (error) {
        console.error('加载数据失败:', error)
        this.error = error.message || '数据加载失败，请检查后端服务是否正常运行'
      } finally {
        this.loading = false
      }
    },

    // 参数变化时重新加载
    onParamsChange() {
      this.loadData()
    },

    // 格式化百分比
    formatPercent(value) {
      if (value === null || value === undefined) return '0%'
      return (value * 100).toFixed(2) + '%'
    },

    // 格式化货币
    formatCurrency(value) {
      if (value === null || value === undefined) return '0.00 USDT'
      return value.toFixed(2) + ' USDT'
    },

    // 格式化数字
    formatNumber(value, decimals = 2) {
      if (value === null || value === undefined) return '0'
      return value.toFixed(decimals)
    }
  }
}
</script>

<style lang="scss" scoped>
.market-compare-page {
  min-height: 100vh;
  background: $bg-primary;
  padding: 24px;
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
  label {
    display: block;
    font-size: 13px;
    font-weight: 500;
    color: $text-secondary;
    margin-bottom: 8px;
  }

  .input {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid $border-color;
    border-radius: 6px;
    font-size: 14px;
  background: $bg-primary;
    color: $text-primary;
    transition: all $transition-fast;

    &:focus {
      outline: none;
      border-color: $color-primary;
      box-shadow: 0 0 0 3px rgba($color-primary, 0.1);
    }
  }
}

.stats-module,
.signals-module,
.spread-module,
.price-module {
  margin-bottom: 32px;
}

.module-title {
  font-size: 24px;
  font-weight: 600;
  color: $text-primary;
  margin: 0 0 20px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid $border-color;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: $bg-card;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: $shadow-sm;
  border: 1px solid $border-color;
  transition: all $transition-fast;

  &:hover {
    box-shadow: $shadow-md;
    transform: translateY(-2px);
  }

  &.success {
    background: linear-gradient(135deg, rgba($color-success, 0.1) 0%, rgba($color-success, 0.05) 100%);
    border-color: rgba($color-success, 0.3);
  }

  .stat-icon {
    font-size: 36px;
    flex-shrink: 0;
  }

  .stat-content {
    flex: 1;
  }

  .stat-label {
    font-size: 13px;
    color: $text-secondary;
    margin-bottom: 4px;
  }

  .stat-value {
    font-size: 24px;
    font-weight: 700;
    color: $text-primary;
  }
}

.signals-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.signal-stat-card {
  background: $bg-card;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  border: 1px solid $border-color;

  .signal-stat-label {
    font-size: 13px;
    color: $text-secondary;
    margin-bottom: 8px;
  }

  .signal-stat-value {
    font-size: 20px;
    font-weight: 600;
    color: $text-primary;

    &.success {
      color: $color-success;
    }
  }
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 24px;

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
}

.chart-widget {
  background: $bg-card;
  border-radius: 12px;
  padding: 20px;
  box-shadow: $shadow-sm;
  border: 1px solid $border-color;
}

.widget-header {
  margin-bottom: 16px;

  h4 {
    font-size: 16px;
    font-weight: 600;
    color: $text-primary;
    margin: 0;
  }
}

.loading-state,
.error-state {
  text-align: center;
  padding: 80px 40px;
  background: $bg-card;
  border-radius: 12px;
  border: 1px solid $border-color;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid $border-color;
  border-top-color: $color-primary;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

.error-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.error-state {
  h3 {
    font-size: 20px;
    color: $text-primary;
    margin: 0 0 8px 0;
  }

  p {
      color: $text-secondary;
    margin: 0 0 24px 0;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
