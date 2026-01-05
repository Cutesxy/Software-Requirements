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

    <!-- KPI 和 AI 结论卡 -->
    <div class="top-section" v-if="signals && signals.length > 0">
      <!-- KPI 卡片 -->
      <div class="kpi-section">
        <div class="kpi-card">
          <div class="kpi-label">信号总数</div>
          <div class="kpi-value">{{ signals.length }}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">平均净利润</div>
          <div class="kpi-value success">{{ formatCurrency(avgNetProfit) }}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">胜率</div>
          <div class="kpi-value">{{ formatPercent(winRate) }}</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-label">平均价差</div>
          <div class="kpi-value">{{ formatCurrency(avgSpread) }}</div>
        </div>
      </div>

      <!-- AI 结论卡 -->
      <div class="insight-card">
        <div class="insight-header">
          <span class="insight-icon">💡</span>
          <h3>AI 分析总结</h3>
          <button 
            class="btn-refresh" 
            @click="generateInsight" 
            :disabled="insightLoading"
            title="重新生成"
          >
            {{ insightLoading ? '生成中...' : '🔄' }}
          </button>
        </div>
        <div class="insight-content" v-if="insight">
          <p v-html="formatInsightLine(insight)"></p>
        </div>
        <div v-else class="insight-placeholder">
          点击刷新按钮生成 AI 分析总结
        </div>
      </div>
    </div>

    <!-- 图表区域 - 全宽布局 -->
    <div class="charts-section" v-if="hasData">
      <!-- 时间分布折线图 -->
      <div class="chart-card full-width">
        <div class="chart-header">
          <h3>📊 信号时间分布</h3>
        </div>
        <chart-card
          title=""
          :height="400"
          :options="signalsTimeDistributionOptions"
          :loading="loading"
        />
      </div>

      <!-- 价差趋势和分布 -->
      <div class="charts-row">
        <div class="chart-card">
          <div class="chart-header">
            <h3>📉 价差趋势</h3>
          </div>
          <chart-card
            title=""
            :height="350"
            :options="spreadTrendOptions"
            :loading="loading"
          />
        </div>

        <div class="chart-card">
          <div class="chart-header">
            <h3>📈 价差分布</h3>
            <div class="chart-controls">
              <label class="control-switch">
                <input type="checkbox" v-model="spreadOptions.removeOutliers" />
                去极值 (P1-P99)
              </label>
              <label class="control-switch">
                <input type="checkbox" v-model="spreadOptions.logScale" />
                对数坐标
              </label>
              <select v-model.number="spreadOptions.binCount" class="control-select">
                <option :value="20">20 bins</option>
                <option :value="30">30 bins</option>
                <option :value="50">50 bins</option>
                <option :value="100">100 bins</option>
              </select>
            </div>
          </div>
          <chart-card
            title=""
            :height="350"
            :options="spreadHistogramOptions"
            :loading="loading"
          />
        </div>
      </div>

      <!-- 套利热力图 -->
      <div class="chart-card full-width">
        <div class="chart-header">
          <h3>🔥 套利热力图 - 星期vs小时分布</h3>
          <div class="heatmap-info">
            <span v-if="bestWeekInfo">显示：{{ bestWeekInfo.label }}（套利机会最多）</span>
            <span v-else>识别高频套利时段</span>
          </div>
        </div>
        <chart-card
          title=""
          :height="500"
          :options="heatmapOptions"
          :loading="heatmapLoading"
        />
      </div>

      <!-- 价格对比 -->
      <div class="chart-card full-width">
        <div class="chart-header">
          <h3>💹 CEX vs DEX 价格对比</h3>
        </div>
        <chart-card
          title=""
          :height="400"
          :options="priceCompareOptions"
          :loading="loading"
        />
      </div>
    </div>

    <!-- 信号明细表 -->
    <div class="signals-table-section" v-if="signals && signals.length > 0">
      <div class="table-header">
        <h3>📋 信号明细表</h3>
        <div class="table-actions">
          <input 
            type="text" 
            v-model="tableFilter" 
            placeholder="搜索..."
            class="table-search"
          />
          <button class="btn btn-secondary" @click="exportTable">导出 CSV</button>
        </div>
      </div>
      <data-table
        :columns="tableColumns"
        :data="filteredTableData"
        :max-height="500"
        :clickable="true"
        @row-click="onRowClick"
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

    <!-- 详情抽屉 -->
    <transition name="drawer">
      <div v-if="selectedSignal" class="detail-drawer-overlay" @click="closeDetail">
        <div class="detail-drawer" @click.stop>
          <div class="drawer-header">
            <h3>信号详情</h3>
            <button class="close-btn" @click="closeDetail">✕</button>
          </div>
          <div class="drawer-content" v-if="selectedSignal">
            <div class="detail-section">
              <h4>基本信息</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>时间</label>
                  <span>{{ formatTime(selectedSignal.time) }}</span>
                </div>
                <div class="detail-item">
                  <label>方向</label>
                  <span>{{ selectedSignal.direction }}</span>
                </div>
                <div class="detail-item">
                  <label>价差</label>
                  <span>{{ selectedSignal.spread?.toFixed(2) || '-' }} USDT</span>
                </div>
                <div class="detail-item">
                  <label>Z-Score</label>
                  <span>{{ selectedSignal.zScore?.toFixed(2) || '-' }}</span>
                </div>
              </div>
            </div>
            <div class="detail-section">
              <h4>收益分析</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>净利润</label>
                  <span :class="selectedSignal.netProfit >= 0 ? 'positive' : 'negative'">
                    {{ selectedSignal.netProfit >= 0 ? '+' : '' }}{{ selectedSignal.netProfit?.toFixed(2) || '-' }} USDT
                  </span>
                </div>
                <div class="detail-item">
                  <label>总成本</label>
                  <span>{{ selectedSignal.totalCost?.toFixed(2) || '-' }} USDT</span>
                </div>
                <div class="detail-item">
                  <label>置信度</label>
                  <span>{{ (selectedSignal.confidence * 100)?.toFixed(1) || '-' }}%</span>
                </div>
              </div>
            </div>
            <div class="detail-section">
              <h4>价格信息</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>CEX 价格</label>
                  <span>{{ selectedSignal.cexPrice?.toFixed(2) || '-' }} USDT</span>
                </div>
                <div class="detail-item">
                  <label>DEX 价格</label>
                  <span>{{ selectedSignal.dexPrice?.toFixed(2) || '-' }} USDT</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>

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
import DataTable from '@/components/DataTable.vue'
import apiClient from '@/utils/api'

export default {
  name: 'MarketCompare',
  components: {
    ChartCard,
    DataTable
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
      },

      // AI 结论
      insight: null,
      insightLoading: false,

      // 热力图相关
      heatmapData: null,
      heatmapLoading: false,

      // 图表选项
      spreadOptions: {
        removeOutliers: true,
        logScale: false,
        binCount: 30
      },

      // 表格
      tableFilter: '',
      selectedSignal: null,
      tableColumns: [
        { key: 'time', label: '时间', type: 'time', width: '160px', sortable: true },
        { key: 'direction', label: '方向', width: '120px' },
        { key: 'spread', label: '价差', type: 'number', decimals: 2, sortable: true },
        { key: 'netProfit', label: '净利润', type: 'number', decimals: 2, sortable: true },
        { key: 'zScore', label: 'Z-Score', type: 'number', decimals: 2, sortable: true },
        { key: 'confidence', label: '置信度', type: 'number', decimals: 2, sortable: true }
      ]
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

    // 胜率
    winRate() {
      if (!this.signals || this.signals.length === 0) return 0
      const wins = this.signals.filter(s => (s.netProfit || 0) > 0).length
      return wins / this.signals.length
    },

    // 信号时间分布折线图（按日期）
    signalsTimeDistributionOptions() {
      if (!this.signals || this.signals.length === 0) return {}

      // 按日期统计信号数量
      const dateCounts = {}
      this.signals.forEach(s => {
        const date = new Date(s.time * 1000)
        // 格式化为 YYYY-MM-DD
        const dateStr = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
        dateCounts[dateStr] = (dateCounts[dateStr] || 0) + 1
      })

      // 转换为数组并排序
      const sortedDates = Object.keys(dateCounts).sort()
      const data = sortedDates.map(date => {
        const timestamp = new Date(date).getTime()
        return [timestamp, dateCounts[date]]
      })

      return {
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e5e7eb',
          borderWidth: 1,
          textStyle: { 
            color: '#111827',
            fontSize: 13
          },
          padding: [10, 14],
          formatter: (params) => {
            if (!params || !Array.isArray(params) || params.length === 0) return ''
            const param = params[0]
            const date = new Date(param.data[0])
            const count = param.data[1]
            const dateStr = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
            return `
              <div style="font-weight: 600; margin-bottom: 6px; color: #111827;">
                ${dateStr}
              </div>
              <div style="color: #6b7280; font-size: 12px;">
                信号数量
              </div>
              <div style="color: #111827; font-size: 16px; font-weight: 700; margin-top: 4px;">
                ${count} 个
              </div>
            `
          }
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
            fontSize: 12,
            formatter: (value) => {
              const date = new Date(value)
              return `${date.getMonth() + 1}/${date.getDate()}`
            }
          },
          axisLine: {
            lineStyle: {
              color: '#e5e7eb'
            }
          },
          splitLine: {
            show: true,
            lineStyle: {
              color: '#f3f4f6',
              type: 'dashed'
            }
          }
        },
        yAxis: {
          type: 'value',
          name: '信号数量',
          nameTextStyle: { 
            color: '#6b7280',
            fontSize: 12
          },
          axisLabel: { 
            color: '#6b7280',
            fontSize: 12
          },
          axisLine: {
            lineStyle: {
              color: '#e5e7eb'
            }
          },
          splitLine: { 
            lineStyle: { 
              color: '#f3f4f6' 
            } 
          }
        },
        series: [{
          name: '信号数量',
          type: 'line',
          data: data,
          smooth: true,
          symbol: 'circle',
          symbolSize: 6,
          lineStyle: {
            color: '#3b82f6',
            width: 3
          },
          itemStyle: {
            color: '#3b82f6',
            borderColor: '#ffffff',
            borderWidth: 2
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
                { offset: 1, color: 'rgba(59, 130, 246, 0.05)' }
              ]
            }
          },
          emphasis: {
            itemStyle: {
              color: '#1e40af',
              borderColor: '#ffffff',
              borderWidth: 3,
              shadowBlur: 10,
              shadowColor: 'rgba(59, 130, 246, 0.5)'
            },
            symbolSize: 10
          },
          animation: true,
          animationDuration: 1000,
          animationEasing: 'cubicOut'
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

    // 价差分布直方图（改进版）
    spreadHistogramOptions() {
      if (!this.signals || this.signals.length === 0) return {}

      let spreads = this.signals.map(s => ({
        value: Math.abs(s.spread || 0),
        direction: s.direction
      })).filter(s => s.value !== null && s.value !== undefined)

      // 去极值
      if (this.spreadOptions.removeOutliers && spreads.length > 0) {
        const values = spreads.map(s => s.value).sort((a, b) => a - b)
        const p1 = values[Math.floor(values.length * 0.01)]
        const p99 = values[Math.floor(values.length * 0.99)]
        spreads = spreads.filter(s => s.value >= p1 && s.value <= p99)
      }

      if (spreads.length === 0) return {}

      const min = Math.min(...spreads.map(s => s.value))
      const max = Math.max(...spreads.map(s => s.value))
      const bins = this.spreadOptions.binCount
      const binWidth = (max - min) / bins

      // 生成直方图数据
      const histogram = new Array(bins).fill(0)
      spreads.forEach(s => {
        const binIndex = Math.min(Math.floor((s.value - min) / binWidth), bins - 1)
        histogram[binIndex]++
      })

      const data = histogram.map((count, i) => [min + i * binWidth, count])
      const series = [{
        type: 'bar',
        data: data,
        itemStyle: { color: '#8b5cf6' }
      }]

      // 计算统计线
      const values = spreads.map(s => s.value)
      const mean = values.reduce((a, b) => a + b, 0) / values.length
      const sorted = [...values].sort((a, b) => a - b)
      const median = sorted[Math.floor(sorted.length / 2)]
      const p95 = sorted[Math.floor(sorted.length * 0.95)]

      // 添加统计线
      const markLines = [
        { name: '均值', yAxis: mean, lineStyle: { color: '#3b82f6', type: 'dashed' } },
        { name: '中位数', yAxis: median, lineStyle: { color: '#10b981', type: 'dashed' } },
        { name: '95分位', yAxis: p95, lineStyle: { color: '#f97316', type: 'dashed' } }
      ]

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
          axisLabel: { 
            color: '#6b7280',
            formatter: this.spreadOptions.logScale ? (value) => {
              return value > 0 ? Math.log10(value).toFixed(1) : '0'
            } : undefined
          },
          scale: this.spreadOptions.logScale
        },
        yAxis: {
          type: 'value',
          name: '频次',
          nameTextStyle: { color: '#6b7280' },
          axisLabel: { color: '#6b7280' },
          splitLine: { lineStyle: { color: '#f3f4f6' } }
        },
        series: series.map(s => ({
          ...s,
          barWidth: '80%',
          markLine: {
            data: markLines,
            label: { show: true, position: 'end' }
          }
        }))
      }
    },

    // 热力图选项 - 星期vs小时分布（只显示套利机会最多的星期）
    heatmapOptions() {
      if (!this.bestWeekInfo || !this.bestWeekInfo.signals || this.bestWeekInfo.signals.length === 0) {
        return {
          title: {
            text: '暂无热力图数据',
            left: 'center',
            top: 'middle',
            textStyle: {
              color: '#6b7280',
              fontSize: 16
            }
          }
        }
      }

      // 只使用最佳星期的信号数据
      const bestWeekSignals = this.bestWeekInfo.signals
      
      // 按星期和小时分组
      const weekHourData = {}
      
      bestWeekSignals.forEach(signal => {
        const date = new Date(signal.time * 1000)
        const dayOfWeek = date.getDay() // 0=周日, 1=周一, ..., 6=周六
        const hour = date.getHours()
        
        const key = `${dayOfWeek}_${hour}`
        if (!weekHourData[key]) {
          weekHourData[key] = []
        }
        
        // 使用Z-Score或价差作为强度值
        const intensity = Math.abs(signal.zScore || signal.spread || 0)
        weekHourData[key].push(intensity)
      })

      // 计算每个星期-小时组合的平均值
      const heatmapData = []
      
      for (let day = 0; day < 7; day++) {
        for (let hour = 0; hour < 24; hour++) {
          const key = `${day}_${hour}`
          const values = weekHourData[key] || []
          const avgValue = values.length > 0
            ? values.reduce((sum, val) => sum + val, 0) / values.length
            : 0
          
          // ECharts热力图数据格式：[x轴索引, y轴索引, 值]
          heatmapData.push([hour, day, avgValue])
        }
      }

      const maxValue = Math.max(...heatmapData.map(item => item[2]), 1)

      return {
        tooltip: {
          position: 'top',
          formatter: (params) => {
            if (!params.data) return ''
            const [hour, day, value] = params.data
            const weekDay = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][day]
            return `${weekDay} ${hour}:00<br/>套利强度: ${value.toFixed(2)}`
          },
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e5e7eb',
          textStyle: { color: '#111827' }
        },
        grid: {
          height: '70%',
          top: '10%',
          left: '10%',
          right: '10%'
        },
        xAxis: {
          type: 'category',
          data: Array.from({ length: 24 }, (_, i) => `${i}:00`),
          splitArea: {
            show: true
          },
          axisLabel: {
            color: '#6b7280',
            fontSize: 11,
            interval: 1
          },
          name: '小时',
          nameLocation: 'middle',
          nameGap: 30,
          nameTextStyle: {
            color: '#6b7280',
            fontSize: 14
          }
        },
        yAxis: {
          type: 'category',
          data: ['周日', '周一', '周二', '周三', '周四', '周五', '周六'],
          splitArea: {
            show: true
          },
          axisLabel: {
            color: '#6b7280',
            fontSize: 12
          },
          name: '星期',
          nameLocation: 'middle',
          nameGap: 50,
          nameTextStyle: {
            color: '#6b7280',
            fontSize: 14
          }
        },
        visualMap: {
          min: 0,
          max: maxValue,
          calculable: true,
          orient: 'horizontal',
          left: 'center',
          bottom: '5%',
          inRange: {
            color: ['#e0f2fe', '#3b82f6', '#1e40af', '#7c3aed']
          },
          textStyle: {
            color: '#6b7280'
          },
          text: ['高', '低']
        },
        series: [{
          name: '套利强度',
          type: 'heatmap',
          data: heatmapData,
          label: {
            show: true,
            formatter: (params) => {
              const value = params.data[2]
              return value > 0 ? value.toFixed(1) : ''
            },
            fontSize: 10,
            color: '#111827'
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
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

    // 过滤后的表格数据
    filteredTableData() {
      if (!this.signals) return []
      let filtered = [...this.signals]
      
      if (this.tableFilter) {
        const filter = this.tableFilter.toLowerCase()
        filtered = filtered.filter(s => {
          return (
            s.direction?.toLowerCase().includes(filter) ||
            s.spread?.toString().includes(filter) ||
            s.netProfit?.toString().includes(filter) ||
            s.zScore?.toString().includes(filter)
          )
        })
      }
      
      return filtered
    },

    // 找出套利机会最多的星期
    bestWeekInfo() {
      if (!this.signals || this.signals.length === 0) return null

      // 按星期分组统计
      const weekStats = {}
      
      this.signals.forEach(signal => {
        const date = new Date(signal.time * 1000)
        // 获取该日期所在周的起始日期（周一）
        const weekStart = this.getWeekStart(date)
        const weekKey = `${weekStart.getFullYear()}-${String(weekStart.getMonth() + 1).padStart(2, '0')}-${String(weekStart.getDate()).padStart(2, '0')}`
        
        if (!weekStats[weekKey]) {
          weekStats[weekKey] = {
            weekStart: weekStart,
            count: 0,
            totalIntensity: 0,
            signals: []
          }
        }
        
        const intensity = Math.abs(signal.zScore || signal.spread || 0)
        weekStats[weekKey].count++
        weekStats[weekKey].totalIntensity += intensity
        weekStats[weekKey].signals.push(signal)
      })

      // 找出套利机会最多的星期（按信号数量，如果相同则按总强度）
      let bestWeek = null
      let maxScore = 0

      Object.values(weekStats).forEach(week => {
        // 综合评分：信号数量 * 1000 + 总强度
        const score = week.count * 1000 + week.totalIntensity
        if (score > maxScore) {
          maxScore = score
          bestWeek = week
        }
      })

      if (!bestWeek) return null

      // 格式化星期标签
      const weekEnd = new Date(bestWeek.weekStart)
      weekEnd.setDate(weekEnd.getDate() + 6)
      
      const startStr = `${bestWeek.weekStart.getMonth() + 1}/${bestWeek.weekStart.getDate()}`
      const endStr = `${weekEnd.getMonth() + 1}/${weekEnd.getDate()}`
      
      return {
        weekStart: bestWeek.weekStart,
        weekEnd: weekEnd,
        label: `${startStr} - ${endStr}`,
        count: bestWeek.count,
        signals: bestWeek.signals
      }
    }
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
        const end = this.dateToTimestamp(this.params.endDate) + 86400 - 1

        const [signals, spreadData, priceData] = await Promise.all([
          apiClient.getSignals(start, end, this.params.zThreshold, this.params.tradeSize),
          apiClient.getSpreadData(start, end),
          apiClient.getPriceData(start, end)
        ])

        this.signals = signals
        this.spreadData = spreadData
        this.priceData = priceData

        // 加载热力图数据
        this.loadHeatmapData()

        this.hasData = true
      } catch (error) {
        console.error('加载数据失败:', error)
        this.error = error.message || '数据加载失败，请检查后端服务是否正常运行'
      } finally {
        this.loading = false
      }
    },

    // 生成 AI 结论
    async generateInsight() {
      if (!this.signals || this.signals.length === 0) return
      
      this.insightLoading = true
      try {
        // 计算统计数据
        const stats = {
          signalCount: this.signals.length,
          avgProfit: this.avgNetProfit,
          winRate: this.winRate,
          avgSpread: this.avgSpread
        }

        // 分析时间分布
        const hourCounts = Array(24).fill(0)
        const dateCounts = {}
        this.signals.forEach(s => {
          const date = new Date(s.time * 1000)
          const hour = date.getHours()
          hourCounts[hour]++
          const dateStr = `${date.getMonth()+1}/${date.getDate()}`
          dateCounts[dateStr] = (dateCounts[dateStr] || 0) + 1
        })

        const maxHour = hourCounts.indexOf(Math.max(...hourCounts))
        const maxDate = Object.entries(dateCounts).sort((a, b) => b[1] - a[1])[0]?.[0]

        // 调用 AI API 生成总结
        const response = await apiClient.chatWithAI({
          message: `【任务：生成数据分析总结】

请根据以下统计数据，直接生成一段简洁的数据分析总结（3-4句话），不需要调用任何筛选函数，只需要用自然语言描述分析结果。

【重要】这是一个文本生成任务，请直接输出分析总结文本，不要尝试筛选数据或调用函数。

分析参数：
- 时间范围：${this.params.startDate} 至 ${this.params.endDate}
- Z-Score 阈值：${this.params.zThreshold}
- 交易规模：${this.params.tradeSize} USDT

数据统计结果：
- 信号总数：${stats.signalCount} 个
- 平均净利润：${stats.avgProfit.toFixed(2)} USDT
- 胜率：${(stats.winRate * 100).toFixed(2)}%
- 平均价差：${stats.avgSpread.toFixed(2)} USDT
- 信号高发时段：${maxHour}:00
- 极值出现日期：${maxDate || '无'}

请生成分析总结，格式示例：
"本周期检测到 ${stats.signalCount} 次套利信号，平均净利润 ${stats.avgProfit.toFixed(2)} USDT，胜率为 ${(stats.winRate * 100).toFixed(2)}%。"
"信号高发时段集中在 ${maxHour}:00 附近；${maxDate ? `极值主要出现在 ${maxDate}` : '无明显极值日期'}。"
"${stats.signalCount > 0 ? `建议关注 ${maxHour}:00 时段的套利机会，该时段信号密度较高。` : '当前参数下未检测到有效信号，建议调整阈值或扩大时间范围。'}"

【参数调整建议】
请根据当前参数和统计结果，用一句话提出参数调整建议。考虑因素：
- 如果信号数量过少（<10个），建议降低 Z-Score 阈值或扩大时间范围
- 如果信号数量过多（>100个），建议提高 Z-Score 阈值以筛选更高质量信号
- 如果胜率较低（<50%），建议提高 Z-Score 阈值
- 如果平均净利润较低，建议调整交易规模或提高 Z-Score 阈值
- 如果信号数量适中且质量良好，可以建议保持当前参数或微调

请用一句话总结参数调整建议，例如："建议将 Z-Score 阈值调整为 2.5 以获取更多信号" 或 "当前参数设置合理，建议保持"。`,
          context: { 
            page: 'MarketCompare',
            params: {
              startDate: this.params.startDate,
              endDate: this.params.endDate,
              zThreshold: this.params.zThreshold,
              tradeSize: this.params.tradeSize
            }
          }
        })

        this.insight = response.content || response.message
      } catch (error) {
        console.error('生成 AI 结论失败:', error)
        this.insight = 'AI 分析暂时不可用，请稍后重试。'
      } finally {
        this.insightLoading = false
      }
    },

    // 格式化结论文本
    formatInsightLine(line) {
      if (!line) return ''
      return line
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, ' ')
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

    // 格式化时间
    formatTime(timestamp) {
      if (!timestamp) return '-'
      const timeMs = (timestamp || 0) * 1000
      return new Date(timeMs).toLocaleString('zh-CN')
    },

    // 获取日期所在周的起始日期（周一）
    getWeekStart(date) {
      const d = new Date(date)
      const day = d.getDay()
      const diff = d.getDate() - day + (day === 0 ? -6 : 1) // 如果周日，则往前6天到周一
      return new Date(d.setDate(diff))
    },

    // 表格行点击
    onRowClick(row) {
      this.selectedSignal = row
    },

    // 关闭详情抽屉
    closeDetail() {
      this.selectedSignal = null
    },

    // 加载热力图数据
    async loadHeatmapData() {
      this.heatmapLoading = true
      try {
        const start = this.dateToTimestamp(this.params.startDate)
        const end = this.dateToTimestamp(this.params.endDate) + 86400 - 1
        
        // 调用后端API获取热力图数据
        const rawHeatmapData = await apiClient.getHeatmapData(start, end)
        
        // 后端返回的格式应该是 [day, hour, value]，其中day是0-6（星期几）
        if (rawHeatmapData && rawHeatmapData.length > 0) {
          // 验证数据格式
          if (Array.isArray(rawHeatmapData[0]) && rawHeatmapData[0].length === 3) {
            // 检查是否是 [day, hour, value] 格式（day是0-6）
            if (typeof rawHeatmapData[0][0] === 'number' && rawHeatmapData[0][0] < 7) {
              // 直接使用后端返回的 [day, hour, value] 格式
              this.heatmapData = rawHeatmapData
            } else {
              // 如果是时间戳格式，需要转换为星期格式
              this.heatmapData = this.convertTimestampToWeekDay(rawHeatmapData)
            }
          } else {
            // 格式不正确，从signals生成
            this.heatmapData = this.generateHeatmapFromSignals()
          }
        } else {
          // 如果没有数据，从signals生成
          this.heatmapData = this.generateHeatmapFromSignals()
        }
      } catch (error) {
        console.error('加载热力图数据失败:', error)
        // 如果API失败，从signals生成
        this.heatmapData = this.generateHeatmapFromSignals()
      } finally {
        this.heatmapLoading = false
      }
    },

    // 将时间戳格式转换为星期格式
    convertTimestampToWeekDay(timestampData) {
      const weekDayData = []
      timestampData.forEach(item => {
        if (item.length >= 3) {
          const date = new Date(item[0] * 1000)
          const dayOfWeek = date.getDay() // 0=周日, 1=周一, ..., 6=周六
          const hour = item[1]
          const value = item[2]
          weekDayData.push([dayOfWeek, hour, value])
        }
      })
      return weekDayData
    },

    // 从信号数据生成热力图
    generateHeatmapFromSignals() {
      if (!this.signals || this.signals.length === 0) return []
      
      const heatmapData = []
      
      // 按星期和小时分组
      const grouped = {}
      this.signals.forEach(signal => {
        const date = new Date(signal.time * 1000)
        const dayOfWeek = date.getDay() // 0=周日, 1=周一, ..., 6=周六
        const hour = date.getHours()
        
        const key = `${dayOfWeek}_${hour}`
        if (!grouped[key]) {
          grouped[key] = []
        }
        
        // 使用Z-Score或价差作为强度值
        const intensity = Math.abs(signal.zScore || signal.spread || 0)
        grouped[key].push(intensity)
      })
      
      // 转换为热力图数据格式 [dayOfWeek, hour, avgValue]
      // dayOfWeek: 0=周日, 1=周一, ..., 6=周六
      Object.entries(grouped).forEach(([key, values]) => {
        const [dayOfWeek, hour] = key.split('_').map(Number)
        const avgValue = values.reduce((sum, val) => sum + val, 0) / values.length
        heatmapData.push([dayOfWeek, hour, avgValue])
      })
      
      return heatmapData
    },


    // 导出表格
    exportTable() {
      if (!this.filteredTableData || this.filteredTableData.length === 0) return

      const header = '时间,方向,价差,净利润,Z-Score,置信度\n'
      const rows = this.filteredTableData.map(s => {
        const timeMs = (s.time || 0) * 1000
        return `${new Date(timeMs).toISOString()},${s.direction},${s.spread || 0},${s.netProfit || 0},${s.zScore || 0},${s.confidence || 0}`
      }).join('\n')
      
      const csv = header + rows
      const blob = new Blob([csv], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `signals_${Date.now()}.csv`
      link.click()
      URL.revokeObjectURL(url)
    }
  }
}
</script>

<style lang="scss" scoped>
.market-compare-page {
  min-height: 100vh;
  background: $bg-primary;
  padding: 24px;
  max-width: 100%;
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

// KPI 和结论卡区域
.top-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  margin-bottom: 24px;

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
}

.kpi-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;

  @media (max-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }
}

.kpi-card {
  background: $bg-card;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid $border-color;
  box-shadow: $shadow-sm;
  text-align: center;

  .kpi-label {
    font-size: 13px;
    color: $text-secondary;
    margin-bottom: 8px;
  }

  .kpi-value {
    font-size: 24px;
    font-weight: 700;
    color: $text-primary;

    &.success {
      color: $color-success;
    }
  }
}

.insight-card {
  background: linear-gradient(135deg, rgba($color-primary, 0.1) 0%, rgba($color-accent, 0.05) 100%);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba($color-primary, 0.2);
  box-shadow: $shadow-sm;

  .insight-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;

    .insight-icon {
      font-size: 24px;
    }

    h3 {
      flex: 1;
      font-size: 18px;
      font-weight: 600;
      color: $text-primary;
      margin: 0;
    }

    .btn-refresh {
      background: none;
      border: 1px solid $border-color;
      border-radius: 6px;
      padding: 6px 12px;
      cursor: pointer;
      font-size: 14px;
      transition: all $transition-fast;

      &:hover:not(:disabled) {
        background: $bg-card-hover;
        border-color: $color-primary;
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
  }

  .insight-content {
    color: $text-primary;
    line-height: 1.6;
    font-size: 14px;

    p {
      margin: 0;
      white-space: normal;
      word-wrap: break-word;
    }

    ::v-deep strong {
      color: $color-primary;
      font-weight: 600;
    }
  }

  .insight-placeholder {
    color: $text-tertiary;
    font-style: italic;
    font-size: 14px;
  }
}

// 图表区域 - 全宽布局
.charts-section {
  margin-bottom: 32px;
}

.charts-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
}

.heatmap-info {
  font-size: 14px;
  color: $text-secondary;
  font-weight: 500;
}

.chart-card {
  background: $bg-card;
  border-radius: 12px;
  padding: 20px;
  box-shadow: $shadow-sm;
  border: 1px solid $border-color;

  &.full-width {
    margin-bottom: 24px;
  }

  .chart-header {
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

    .chart-controls {
      display: flex;
      gap: 12px;
      align-items: center;
      flex-wrap: wrap;
    }

    .control-label,
    .control-switch {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 13px;
      color: $text-secondary;
      cursor: pointer;

      input[type="radio"],
      input[type="checkbox"] {
        cursor: pointer;
      }
    }

    .control-select {
      padding: 4px 8px;
      border: 1px solid $border-color;
      border-radius: 4px;
      font-size: 13px;
      background: $bg-primary;
      color: $text-primary;
    }
  }
}

// 信号明细表
.signals-table-section {
  background: $bg-card;
  border-radius: 12px;
  padding: 20px;
  box-shadow: $shadow-sm;
  border: 1px solid $border-color;
  margin-bottom: 24px;

  .table-header {
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

    .table-actions {
      display: flex;
      gap: 12px;
      align-items: center;
    }

    .table-search {
      padding: 8px 12px;
      border: 1px solid $border-color;
      border-radius: 6px;
      font-size: 14px;
      width: 200px;
    }
  }
}

// 详情抽屉
.detail-drawer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
}

.detail-drawer {
  width: 500px;
  max-width: 90vw;
  height: 100vh;
  background: $bg-card;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;

  .drawer-header {
    padding: 20px;
    border-bottom: 1px solid $border-color;
    display: flex;
    justify-content: space-between;
    align-items: center;

    h3 {
      font-size: 18px;
      font-weight: 600;
      color: $text-primary;
      margin: 0;
    }

    .close-btn {
      background: none;
      border: none;
      font-size: 24px;
      color: $text-secondary;
      cursor: pointer;
      padding: 0;
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      transition: all $transition-fast;

      &:hover {
        background: $bg-card-hover;
        color: $text-primary;
      }
    }
  }

  .drawer-content {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
  }

  .detail-section {
    margin-bottom: 24px;

    h4 {
      font-size: 16px;
      font-weight: 600;
      color: $text-primary;
      margin: 0 0 16px 0;
      padding-bottom: 8px;
      border-bottom: 1px solid $border-color;
    }
  }

  .detail-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }

  .detail-item {
    label {
      display: block;
      font-size: 12px;
      color: $text-secondary;
      margin-bottom: 4px;
    }

    span {
      font-size: 14px;
      color: $text-primary;
      font-weight: 500;

      &.positive {
        color: $color-success;
      }

      &.negative {
        color: $color-danger;
      }
    }
  }
}

.drawer-enter-active,
.drawer-leave-active {
  transition: opacity $transition-normal;
  
  .detail-drawer {
    transition: transform $transition-normal;
  }
}

.drawer-enter,
.drawer-leave-to {
  opacity: 0;
  
  .detail-drawer {
    transform: translateX(100%);
  }
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
