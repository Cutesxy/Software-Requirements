<template>
  <div class="overview-page">
    <div class="grid grid-12">
      <!-- 左侧参数面板 -->
      <aside class="sidebar col-span-3">
        <div class="card">
          <div class="card-header">
            <h3>分析参数设置</h3>
          </div>
          
          <div class="param-section">
            <label class="param-label">时间范围</label>
            <select v-model="timePreset" @change="onTimeRangeChange" class="input">
              <option value="week">最近7天</option>
              <option value="month">9月全月</option>
              <option value="custom">自定义</option>
            </select>
          </div>
          
          <div class="param-section">
            <label class="param-label">交易对</label>
            <input type="text" class="input" value="USDT/ETH" disabled />
          </div>
          
          <div class="param-section">
            <label class="param-label">DEX池</label>
            <select v-model="dexPool" class="input">
              <option>Uniswap V3 (0.3%)</option>
              <option>Uniswap V3 (0.05%)</option>
              <option>Uniswap V3 (1%)</option>
            </select>
          </div>
          
          <div class="param-section">
            <label class="param-label">CEX交易所</label>
            <select v-model="cexExchange" class="input">
              <option>Binance</option>
              <option>OKX</option>
              <option>Coinbase</option>
            </select>
          </div>
          
          <button class="btn btn-primary w-full" @click="startAnalysis" :disabled="loading">
            {{ loading ? '分析中...' : '开始分析' }}
          </button>
          
          <div class="param-section">
            <div class="checkbox">
              <input type="checkbox" id="showRadar" v-model="showRadar" />
              <label for="showRadar">显示雷达图</label>
            </div>
            <div class="checkbox">
              <input type="checkbox" id="showPie" v-model="showPie" />
              <label for="showPie">显示饼图</label>
            </div>
            <div class="checkbox">
              <input type="checkbox" id="showHeatmap" v-model="showHeatmap" />
              <label for="showHeatmap">显示热力图</label>
            </div>
          </div>
          
          <!-- 实时统计 -->
          <div class="stats-panel">
            <div class="stat-item">
              <span class="stat-label">检测信号</span>
              <span class="stat-value">{{ stats.signalCount }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">平均价差</span>
              <span class="stat-value">{{ stats.avgSpread }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">潜在收益</span>
              <span class="stat-value positive">+{{ stats.totalProfit }}</span>
            </div>
          </div>
        </div>
      </aside>
      
      <!-- 右侧主图表区 -->
      <main class="main-content col-span-9">
        <!-- 价格对比图 -->
        <div class="card">
          <div class="card-header">
            <h3>Uniswap vs Binance 价格对比</h3>
            <div class="header-actions">
              <button class="btn-icon" @click="toggleLogScale" title="切换坐标">
                {{ logScale ? 'LOG' : 'LIN' }}
              </button>
              <button class="btn-icon" @click="exportChart" title="导出">↓</button>
            </div>
          </div>
          <chart-card
            title=""
            :height="400"
            :options="priceCompareOptions"
            :loading="loading"
          />
        </div>
        
        <!-- 下方图表组 -->
        <div class="grid grid-2" style="margin-top: 24px;">
          <!-- 雷达图 -->
          <div v-if="showRadar" class="card">
            <div class="card-header">
              <h3>实时套利机会雷达图</h3>
            </div>
            <chart-card
              title=""
              :height="300"
              :options="radarOptions"
              :loading="loading"
            />
          </div>
          
          <!-- 饼图 -->
          <div v-if="showPie" class="card">
            <div class="card-header">
              <h3>交易方向比例图</h3>
            </div>
            <chart-card
              title=""
              :height="300"
              :options="pieOptions"
              :loading="loading"
            />
          </div>
          
          <!-- 热力图 -->
          <div v-if="showHeatmap" class="card" :class="{ 'col-span-2': !showRadar || !showPie }">
            <div class="card-header">
              <h3>价差热力图</h3>
            </div>
            <chart-card
              title=""
              :height="300"
              :options="heatmapOptions"
              :loading="loading"
            />
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import ChartCard from '@/components/ChartCard.vue'

export default {
  name: 'Overview',
  
  components: {
    ChartCard
  },
  
  data() {
    return {
      loading: false,
      timePreset: 'month',
      dexPool: 'Uniswap V3 (0.3%)',
      cexExchange: 'Binance',
      logScale: false,
      showRadar: true,
      showPie: true,
      showHeatmap: true,
      
      stats: {
        signalCount: 0,
        avgSpread: '0.00',
        totalProfit: '0.00'
      }
    }
  },
  
  computed: {
    ...mapState(['priceData', 'spreadData', 'signals']),
    
    priceCompareOptions() {
      if (!this.priceData) return {}
      
      const cexData = this.priceData.cex.map(d => [d.t, d.p])
      const dexData = this.priceData.dex.map(d => [d.t, d.p])
      
      return {
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '15%',
          containLabel: true
        },
        legend: {
          data: ['Uniswap V3', 'Binance'],
          top: 10,
          textStyle: { color: '#6b7280' }
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'cross' },
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e5e7eb',
          textStyle: { color: '#111827' }
        },
        xAxis: {
          type: 'time',
          axisLabel: {
            color: '#6b7280',
            formatter: (value) => {
              const date = new Date(value)
              return `${date.getMonth()+1}/${date.getDate()}`
            }
          },
          axisLine: { lineStyle: { color: '#e5e7eb' } }
        },
        yAxis: {
          type: this.logScale ? 'log' : 'value',
          name: 'Price (USDT)',
          nameTextStyle: { color: '#6b7280' },
          axisLabel: {
            color: '#6b7280',
            formatter: (value) => value.toFixed(0)
          },
          splitLine: { lineStyle: { color: '#f3f4f6' } },
          axisLine: { lineStyle: { color: '#e5e7eb' } }
        },
        series: [
          {
            name: 'Uniswap V3',
            type: 'line',
            data: cexData,
            symbol: 'none',
            lineStyle: { color: '#3b82f6', width: 2 },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
                  { offset: 1, color: 'rgba(59, 130, 246, 0.05)' }
                ]
              }
            }
          },
          {
            name: 'Binance',
            type: 'line',
            data: dexData,
            symbol: 'none',
            lineStyle: { color: '#10b981', width: 2 },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(16, 185, 129, 0.3)' },
                  { offset: 1, color: 'rgba(16, 185, 129, 0.05)' }
                ]
              }
            }
          }
        ]
      }
    },
    
    radarOptions() {
      const radarData = [
        { metric: '价差幅度', value: 10 },
        { metric: '平均套利', value: 7 },
        { metric: '交易频率', value: 8 },
        { metric: '潜在利润', value: 6 },
        { metric: '市场波动', value: 9 }
      ]
      
      return {
        tooltip: {
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e5e7eb',
          textStyle: { color: '#111827' }
        },
        radar: {
          indicator: radarData.map(d => ({ name: d.metric, max: 10 })),
          axisLine: { lineStyle: { color: '#e5e7eb' } },
          splitLine: { lineStyle: { color: '#e5e7eb' } },
          splitArea: {
            areaStyle: {
              color: ['rgba(59, 130, 246, 0.05)', 'rgba(255, 255, 255, 0)']
            }
          }
        },
        series: [{
          type: 'radar',
          data: [{
            value: radarData.map(d => d.value),
            name: '套利指标',
            lineStyle: { color: '#3b82f6', width: 2 },
            areaStyle: { color: 'rgba(59, 130, 246, 0.4)' },
            itemStyle: { color: '#3b82f6' }
          }]
        }]
      }
    },
    
    pieOptions() {
      const directionData = [
        { name: 'Uniswap → Binance', value: 6 },
        { name: 'Binance → Uniswap', value: 4 }
      ]
      
      return {
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e5e7eb',
          textStyle: { color: '#111827' }
        },
        legend: {
          bottom: 10,
          textStyle: { color: '#6b7280' }
        },
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 10,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: true,
            formatter: '{b}: {d}%',
            color: '#111827'
          },
          data: directionData,
          color: ['#10b981', '#f97316']
        }]
      }
    },
    
    heatmapOptions() {
      if (!this.spreadData || this.spreadData.length === 0) return {}
      
      const heatmapData = this.generateHeatmapData()
      
      return {
        tooltip: {
          position: 'top',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e5e7eb',
          textStyle: { color: '#111827' },
          formatter: (params) => {
            if (!params.data || !Array.isArray(params.data)) return ''
            const [hour, minute, value] = params.data
            return `时间: ${hour}:${minute}<br/>Z-Score: ${value.toFixed(2)}`
          }
        },
        grid: {
          left: '10%',
          right: '5%',
          top: '5%',
          bottom: '10%'
        },
        xAxis: {
          type: 'category',
          data: this.generateHourLabels(),
          splitArea: { show: true },
          axisLabel: { color: '#6b7280' },
          axisLine: { lineStyle: { color: '#e5e7eb' } }
        },
        yAxis: {
          type: 'category',
          data: this.generateMinuteLabels(),
          splitArea: { show: true },
          axisLabel: { color: '#6b7280' },
          axisLine: { lineStyle: { color: '#e5e7eb' } }
        },
        visualMap: {
          min: -3,
          max: 3,
          calculable: true,
          orient: 'horizontal',
          left: 'center',
          bottom: '0%',
          inRange: {
            color: ['#ef4444', '#f3f4f6', '#10b981']
          },
          textStyle: { color: '#6b7280' }
        },
        series: [{
          name: 'Z-Score',
          type: 'heatmap',
          data: heatmapData,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.3)'
            }
          }
        }]
      }
    }
  },
  
  created() {
    this.loadData()
  },
  
  methods: {
    ...mapActions(['loadPriceData', 'loadSpreadData', 'detectSignals']),
    
    async loadData() {
      this.loading = true
      try {
        await Promise.all([
          this.loadPriceData(),
          this.loadSpreadData(),
          this.detectSignals()
        ])
        this.updateStats()
      } catch (error) {
        console.error('加载数据失败:', error)
      } finally {
        this.loading = false
      }
    },
    
    async startAnalysis() {
      await this.loadData()
    },
    
    onTimeRangeChange() {
      // 时间范围变化处理
      this.loadData()
    },
    
    toggleLogScale() {
      this.logScale = !this.logScale
    },
    
    exportChart() {
      alert('图表导出功能')
    },
    
    updateStats() {
      if (this.signals) {
        this.stats.signalCount = this.signals.length
        const totalProfit = this.signals.reduce((sum, s) => sum + s.netProfit, 0)
        this.stats.totalProfit = totalProfit.toFixed(2)
      }
      
      if (this.spreadData) {
        const spreads = this.spreadData.map(d => d.spread)
        const avgSpread = spreads.reduce((a, b) => a + b, 0) / spreads.length
        this.stats.avgSpread = avgSpread.toFixed(2)
      }
    },
    
    generateHeatmapData() {
      if (!this.spreadData) return []
      
      const data = []
      const grouped = {}
      
      this.spreadData.forEach(d => {
        const date = new Date(d.t)
        const hour = date.getHours()
        const minute = Math.floor(date.getMinutes() / 5) * 5
        const key = `${hour}:${minute}`
        
        if (!grouped[key]) grouped[key] = []
        grouped[key].push(d.z)
      })
      
      Object.keys(grouped).forEach(key => {
        const [hour, minute] = key.split(':').map(Number)
        const avgZ = grouped[key].reduce((a, b) => a + b, 0) / grouped[key].length
        data.push([hour, minute, avgZ])
      })
      
      return data
    },
    
    generateHourLabels() {
      return Array.from({ length: 24 }, (_, i) => `${i}:00`)
    },
    
    generateMinuteLabels() {
      return Array.from({ length: 12 }, (_, i) => `${i * 5}m`)
    }
  }
}
</script>

<style lang="scss" scoped>
.overview-page {
  animation: fadeIn 0.3s ease;
}

.col-span-3 {
  grid-column: span 3;
}

.col-span-9 {
  grid-column: span 9;
}

.col-span-2 {
  grid-column: span 2;
}

.sidebar {
  position: sticky;
  top: 96px;
  align-self: start;
}

.param-section {
  margin-bottom: 20px;
  
  &:last-child {
    margin-top: 24px;
    padding-top: 20px;
    border-top: 1px solid $border-color;
  }
}

.param-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: $text-secondary;
  margin-bottom: 8px;
}

.w-full {
  width: 100%;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid $border-color;
  border-radius: 6px;
  color: $text-secondary;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all $transition-fast;
  
  &:hover {
    border-color: $color-primary;
    color: $color-primary;
  }
}

.stats-panel {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid $border-color;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  
  &:not(:last-child) {
    border-bottom: 1px solid $border-color;
  }
}

.stat-label {
  font-size: 13px;
  color: $text-secondary;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: $text-primary;
  
  &.positive {
    color: $color-success;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>

