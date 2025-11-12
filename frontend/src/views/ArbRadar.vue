<template>
  <div class="arb-radar-page">
    <div class="grid grid-12">
      <!-- 左侧参数面板 -->
      <aside class="sidebar col-span-3">
        <div class="card">
          <div class="card-header">
            <h3>检测器配置</h3>
          </div>
          
          <div class="param-section">
            <label class="param-label">价差阈值 (USDT)</label>
            <input
              v-model.number="detectorParams.priceThreshold"
              type="number"
              step="0.1"
              class="input"
              @change="onParamsChange"
            />
          </div>
          
          <div class="param-section">
            <label class="param-label">Z-Score阈值</label>
            <input
              v-model.number="detectorParams.zScoreThreshold"
              type="number"
              step="0.1"
              class="input"
              @change="onParamsChange"
            />
          </div>
          
          <div class="param-section">
            <label class="param-label">最小成交量 (USDT)</label>
            <input
              v-model.number="detectorParams.volumeMin"
              type="number"
              step="100"
              class="input"
              @change="onParamsChange"
            />
          </div>
          
          <div class="param-section">
            <label class="param-label">时间窗口 (秒)</label>
            <div class="range-input">
              <input
                v-model.number="detectorParams.timeWindow[0]"
                type="number"
                class="input"
                style="width: 48%"
                @change="onParamsChange"
              />
              <span>-</span>
              <input
                v-model.number="detectorParams.timeWindow[1]"
                type="number"
                class="input"
                style="width: 48%"
                @change="onParamsChange"
              />
            </div>
          </div>
          
          <div class="param-section">
            <h4 class="section-title">费用设置</h4>
            
            <label class="param-label-sm">CEX手续费 (%)</label>
            <input
              v-model.number="detectorParams.fees.cex"
              type="number"
              step="0.001"
              class="input input-sm"
              @change="onParamsChange"
            />
            
            <label class="param-label-sm" style="margin-top: 8px;">DEX手续费 (%)</label>
            <input
              v-model.number="detectorParams.fees.dex"
              type="number"
              step="0.001"
              class="input input-sm"
              @change="onParamsChange"
            />
            
            <label class="param-label-sm" style="margin-top: 8px;">Gas费用 (USDT)</label>
            <input
              v-model.number="detectorParams.fees.gas"
              type="number"
              step="1"
              class="input input-sm"
              @change="onParamsChange"
            />
            
            <label class="param-label-sm" style="margin-top: 8px;">滑点 (%)</label>
            <input
              v-model.number="detectorParams.fees.slippage"
              type="number"
              step="0.001"
              class="input input-sm"
              @change="onParamsChange"
            />
          </div>
          
          <button class="btn btn-primary w-full" @click="detectSignals" :disabled="loading">
            <span v-if="!loading">🔍 检测信号</span>
            <span v-else>检测中...</span>
          </button>
          
          <button class="btn btn-secondary w-full" @click="resetParams" style="margin-top: 8px;">
            重置参数
          </button>
          
          <div class="param-section">
            <label class="param-label">预设方案</label>
            <select v-model="selectedPreset" @change="loadPreset" class="select">
              <option value="">自定义</option>
              <option value="conservative">保守型</option>
              <option value="balanced">平衡型</option>
              <option value="aggressive">激进型</option>
            </select>
          </div>
          
          <!-- 统计信息 -->
          <div class="stats-panel">
            <div class="stat-item">
              <span class="stat-label">检测信号</span>
              <span class="stat-value">{{ signals.length || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">总收益</span>
              <span class="stat-value positive">+{{ totalProfit.toFixed(2) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">平均置信度</span>
              <span class="stat-value">{{ (avgConfidence * 100).toFixed(0) }}%</span>
            </div>
          </div>
        </div>
      </aside>
      
      <!-- 右侧内容区 -->
      <main class="main-content col-span-9">
        <!-- 信号列表 -->
        <div class="card">
          <div class="card-header">
            <h3>套利信号 ({{ signals.length || 0 }})</h3>
            <div class="header-actions">
              <select v-model="sortBy" class="select select-sm">
                <option value="time">按时间</option>
                <option value="profit">按收益</option>
                <option value="confidence">按置信度</option>
              </select>
              <button class="btn-icon" @click="exportSignals" title="导出">↓</button>
            </div>
          </div>
          
          <data-table
            :columns="signalColumns"
            :data="sortedSignals"
            :max-height="500"
            :clickable="true"
            @row-click="onSignalClick"
          >
            <template #col-direction="{ value }">
              <span class="badge" :class="value === 'CEX->DEX' ? 'badge-primary' : 'badge-success'">
                {{ value }}
              </span>
            </template>
            
            <template #col-netProfit="{ value }">
              <span class="value-display positive">
                +{{ value.toFixed(2) }}
              </span>
            </template>
            
            <template #col-confidence="{ value }">
              <div class="confidence-bar">
                <div class="bar-fill" :style="{ width: (value * 100) + '%' }"></div>
                <span class="bar-text">{{ (value * 100).toFixed(0) }}%</span>
              </div>
            </template>
            
            <template #col-actions="{ row }">
              <button class="btn-text" @click.stop="viewDetail(row)">
                详情 →
              </button>
            </template>
          </data-table>
        </div>
        
        <!-- 信号空间分布 -->
        <div class="card" style="margin-top: 24px;">
          <div class="card-header">
            <h3>信号空间分布</h3>
          </div>
          <chart-card
            title=""
            :height="350"
            :options="signalScatterOptions"
            :loading="loading"
          />
        </div>
      </main>
    </div>
    
    <!-- 信号详情弹窗 -->
    <div v-if="selectedSignal" class="modal-overlay" @click="closeDetail">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>信号详情</h3>
          <button class="btn-close" @click="closeDetail">×</button>
        </div>
        
        <div class="modal-body">
          <div class="detail-grid">
            <div class="detail-item">
              <label>时间</label>
              <span>{{ formatTime(selectedSignal.time) }}</span>
            </div>
            <div class="detail-item">
              <label>方向</label>
              <span class="badge" :class="getBadgeClass(selectedSignal.direction)">
                {{ selectedSignal.direction }}
              </span>
            </div>
            <div class="detail-item">
              <label>CEX价格</label>
              <span>{{ selectedSignal.cexPrice.toFixed(2) }} USDT</span>
            </div>
            <div class="detail-item">
              <label>DEX价格</label>
              <span>{{ selectedSignal.dexPrice.toFixed(2) }} USDT</span>
            </div>
            <div class="detail-item">
              <label>价差</label>
              <span class="value-display" :class="getValueClass(selectedSignal.spread)">
                {{ selectedSignal.spread.toFixed(2) }} USDT
              </span>
            </div>
            <div class="detail-item">
              <label>价差百分比</label>
              <span>{{ selectedSignal.spreadPct.toFixed(4) }}%</span>
            </div>
            <div class="detail-item">
              <label>Z-Score</label>
              <span>{{ selectedSignal.zScore.toFixed(2) }}</span>
            </div>
            <div class="detail-item">
              <label>建议规模</label>
              <span>{{ selectedSignal.size.toFixed(2) }} USDT</span>
            </div>
          </div>
          
          <div class="profit-breakdown">
            <h4>收益分解</h4>
            <div class="breakdown-item">
              <span>毛收益</span>
              <span class="positive">+{{ selectedSignal.grossProfit.toFixed(2) }}</span>
            </div>
            <div class="breakdown-item">
              <span>总成本</span>
              <span class="negative">-{{ selectedSignal.totalCost.toFixed(2) }}</span>
            </div>
            <div class="breakdown-item total">
              <span>净收益</span>
              <span class="positive large">+{{ selectedSignal.netProfit.toFixed(2) }} USDT</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import ChartCard from '@/components/ChartCard.vue'
import DataTable from '@/components/DataTable.vue'

export default {
  name: 'ArbRadar',
  
  components: {
    ChartCard,
    DataTable
  },
  
  data() {
    return {
      loading: false,
      selectedSignal: null,
      selectedPreset: '',
      sortBy: 'profit',
      
      detectorParams: {
        priceThreshold: 0.8,
        zScoreThreshold: 2.0,
        timeWindow: [1, 20],
        volumeMin: 1000,
        fees: {
          cex: 0.001,
          dex: 0.003,
          gas: 15,
          slippage: 0.002
        }
      },
      
      signalColumns: [
        { key: 'time', label: '时间', type: 'time', width: '140px' },
        { key: 'direction', label: '方向', width: '140px' },
        { key: 'spread', label: '价差', type: 'number', decimals: 2, sortable: true },
        { key: 'netProfit', label: '净收益', type: 'number', decimals: 2, sortable: true },
        { key: 'confidence', label: '置信度', width: '140px' },
        { key: 'actions', label: '操作', width: '80px' }
      ]
    }
  },
  
  computed: {
    ...mapState(['signals']),
    
    sortedSignals() {
      if (!this.signals) return []
      
      const sorted = [...this.signals]
      
      switch (this.sortBy) {
        case 'profit':
          return sorted.sort((a, b) => b.netProfit - a.netProfit)
        case 'confidence':
          return sorted.sort((a, b) => b.confidence - a.confidence)
        case 'time':
        default:
          return sorted.sort((a, b) => b.time - a.time)
      }
    },
    
    totalProfit() {
      if (!this.signals || this.signals.length === 0) return 0
      return this.signals.reduce((sum, s) => sum + s.netProfit, 0)
    },
    
    avgConfidence() {
      if (!this.signals || this.signals.length === 0) return 0
      const sum = this.signals.reduce((sum, s) => sum + s.confidence, 0)
      return sum / this.signals.length
    },
    
    signalScatterOptions() {
      if (!this.signals || this.signals.length === 0) return {}
      
      const data = this.signals.map(s => [
        new Date(s.time).getHours(),
        Math.abs(s.spread),
        s.netProfit,
        s.confidence
      ])
      
      return {
        backgroundColor: 'transparent',
        tooltip: {
          formatter: (params) => {
            const [hour, spread, profit, confidence] = params.data
            return `时间: ${hour}:00<br/>价差: ${spread.toFixed(2)}<br/>收益: ${profit.toFixed(2)}<br/>置信度: ${(confidence * 100).toFixed(0)}%`
          },
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e5e7eb',
          textStyle: { color: '#111827' }
        },
        xAxis: {
          name: '时间 (小时)',
          nameTextStyle: { color: '#6b7280' },
          axisLabel: { color: '#6b7280' },
          axisLine: { lineStyle: { color: '#e5e7eb' } },
          splitLine: { lineStyle: { color: '#f3f4f6' } },
          min: 0,
          max: 24
        },
        yAxis: {
          name: '价差 (USDT)',
          nameTextStyle: { color: '#6b7280' },
          axisLabel: { color: '#6b7280' },
          axisLine: { lineStyle: { color: '#e5e7eb' } },
          splitLine: { lineStyle: { color: '#f3f4f6' } }
        },
        visualMap: {
          min: 0,
          max: Math.max(...data.map(d => d[2])),
          dimension: 2,
          orient: 'vertical',
          right: 10,
          top: 'center',
          text: ['高', '低'],
          calculable: true,
          inRange: {
            color: ['#f97316', '#3b82f6', '#10b981']
          },
          textStyle: { color: '#6b7280' }
        },
        series: [{
          type: 'scatter',
          data,
          symbolSize: (val) => val[3] * 20 + 5,
          emphasis: {
            focus: 'self',
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(59, 130, 246, 0.5)'
            }
          }
        }]
      }
    }
  },
  
  created() {
    this.detectSignals()
  },
  
  methods: {
    ...mapActions(['detectSignals: detectSignalsAction', 'updateDetectorParams']),
    
    async detectSignals() {
      this.loading = true
      try {
        await this.$store.dispatch('detectSignals')
      } catch (error) {
        console.error('检测信号失败:', error)
      } finally {
        this.loading = false
      }
    },
    
    onParamsChange() {
      this.updateDetectorParams(this.detectorParams)
    },
    
    resetParams() {
      this.detectorParams = {
        priceThreshold: 0.8,
        zScoreThreshold: 2.0,
        timeWindow: [1, 20],
        volumeMin: 1000,
        fees: {
          cex: 0.001,
          dex: 0.003,
          gas: 15,
          slippage: 0.002
        }
      }
      this.onParamsChange()
    },
    
    loadPreset() {
      const presets = {
        conservative: {
          priceThreshold: 1.5,
          zScoreThreshold: 3.0,
          volumeMin: 2000,
          fees: { cex: 0.001, dex: 0.003, gas: 20, slippage: 0.003 }
        },
        balanced: {
          priceThreshold: 0.8,
          zScoreThreshold: 2.0,
          volumeMin: 1000,
          fees: { cex: 0.001, dex: 0.003, gas: 15, slippage: 0.002 }
        },
        aggressive: {
          priceThreshold: 0.5,
          zScoreThreshold: 1.5,
          volumeMin: 500,
          fees: { cex: 0.001, dex: 0.003, gas: 10, slippage: 0.001 }
        }
      }
      
      if (this.selectedPreset && presets[this.selectedPreset]) {
        this.detectorParams = {
          ...this.detectorParams,
          ...presets[this.selectedPreset]
        }
        this.onParamsChange()
      }
    },
    
    onSignalClick(signal) {
      this.selectedSignal = signal
    },
    
    viewDetail(signal) {
      this.selectedSignal = signal
    },
    
    closeDetail() {
      this.selectedSignal = null
    },
    
    exportSignals() {
      if (!this.signals || this.signals.length === 0) return
      
      const csv = this.signalsToCSV()
      const blob = new Blob([csv], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `signals_${Date.now()}.csv`
      link.click()
      URL.revokeObjectURL(url)
    },
    
    signalsToCSV() {
      const header = 'Time,Direction,Spread,NetProfit,Confidence\n'
      const rows = this.signals.map(s => 
        `${new Date(s.time).toISOString()},${s.direction},${s.spread},${s.netProfit},${s.confidence}`
      ).join('\n')
      return header + rows
    },
    
    formatTime(timestamp) {
      return new Date(timestamp).toLocaleString('zh-CN')
    },
    
    getBadgeClass(direction) {
      return direction === 'CEX->DEX' ? 'badge-primary' : 'badge-success'
    },
    
    getValueClass(value) {
      return value > 0 ? 'positive' : value < 0 ? 'negative' : 'neutral'
    }
  }
}
</script>

<style lang="scss" scoped>
.arb-radar-page {
  animation: fadeIn 0.3s ease;
}

.col-span-3 {
  grid-column: span 3;
}

.col-span-9 {
  grid-column: span 9;
}

.sidebar {
  position: sticky;
  top: 96px;
  align-self: start;
}

.param-section {
  margin-bottom: 20px;
}

.param-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: $text-secondary;
  margin-bottom: 8px;
}

.param-label-sm {
  display: block;
  font-size: 11px;
  color: $text-tertiary;
  margin-bottom: 4px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: $text-primary;
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid $border-color;
}

.input-sm {
  padding: 6px 10px;
  font-size: 13px;
}

.range-input {
  display: flex;
  align-items: center;
  gap: 8px;
  
  span {
    color: $text-tertiary;
  }
}

.w-full {
  width: 100%;
}

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.select-sm {
  padding: 6px 12px;
  font-size: 13px;
  min-width: 120px;
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
  font-size: 14px;
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

.confidence-bar {
  position: relative;
  width: 100%;
  height: 24px;
  background: $bg-primary;
  border-radius: 12px;
  overflow: hidden;
  
  .bar-fill {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    background: linear-gradient(90deg, $color-primary, $color-success);
    transition: width 0.3s ease;
  }
  
  .bar-text {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    font-size: 11px;
    font-weight: 600;
    color: $text-primary;
    z-index: 1;
  }
}

.btn-text {
  background: none;
  border: none;
  color: $color-primary;
  font-size: 12px;
  cursor: pointer;
  transition: color $transition-fast;
  
  &:hover {
    color: darken($color-primary, 10%);
  }
}

// Modal
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

.modal-content {
  background: $bg-card;
  border-radius: $border-radius;
  width: 90%;
  max-width: 700px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: $shadow-lg;
  border: 1px solid $border-color;
  animation: slideUp 0.3s ease;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid $border-color;
  
  h3 {
    margin: 0;
    font-size: 20px;
    color: $text-primary;
  }
}

.btn-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid $border-color;
  border-radius: 50%;
  color: $text-secondary;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
  transition: all $transition-fast;
  
  &:hover {
    border-color: $color-danger;
    color: $color-danger;
    transform: rotate(90deg);
  }
}

.modal-body {
  padding: 24px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  
  label {
    font-size: 11px;
    color: $text-tertiary;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  
  span {
    font-size: 14px;
    font-weight: 500;
    color: $text-primary;
  }
}

.profit-breakdown {
  padding: 20px;
  background: $bg-primary;
  border-radius: $border-radius-sm;
  
  h4 {
    margin: 0 0 16px 0;
    font-size: 14px;
    color: $text-secondary;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid $border-color;
  font-size: 14px;
  
  &:last-child {
    border-bottom: none;
  }
  
  &.total {
    margin-top: 8px;
    padding-top: 16px;
    border-top: 2px solid $border-color;
    font-weight: 600;
    
    .large {
      font-size: 18px;
    }
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
