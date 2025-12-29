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
            <label class="param-label">
              时间范围
              <span class="param-tooltip" title="支持2025年9月内的自定义时间范围选择">ℹ️</span>
            </label>

            <!-- 快捷选择按钮 -->
            <div class="time-quick-select">
              <button
                class="btn-time-preset"
                :class="{ active: timePreset === 'full' }"
                @click="selectTimePreset('full')"
              >
                全月
              </button>
              <button
                class="btn-time-preset"
                :class="{ active: timePreset === 'first-half' }"
                @click="selectTimePreset('first-half')"
              >
                上半月
              </button>
              <button
                class="btn-time-preset"
                :class="{ active: timePreset === 'second-half' }"
                @click="selectTimePreset('second-half')"
              >
                下半月
              </button>
              <button
                class="btn-time-preset"
                :class="{ active: timePreset === 'custom' }"
                @click="selectTimePreset('custom')"
              >
                自定义
              </button>
            </div>

            <!-- 当前选择显示 -->
            <div class="time-range-display">
              <span class="time-range-text">{{ customRangeLabel }}</span>
              <button class="btn-calendar-toggle" @click="toggleCalendar" :disabled="!isCustomMode">
                📅
              </button>
            </div>
          </div>

          <div class="param-section">
            <label class="param-label">
              交易对
              <span class="param-tooltip" title="当前分析的加密货币交易对，默认USDT/ETH">ℹ️</span>
            </label>
            <input type="text" class="input" value="ETH/USDT" disabled />
          </div>

          <div class="param-section">
            <label class="param-label">
              DEX池
              <span class="param-tooltip" title="选择要分析的Uniswap V3流动性池，不同费率对应不同的流动性深度和滑点">ℹ️</span>
            </label>
            <select v-model="dexPool" class="input" @change="onDexPoolChange">
              <option>Uniswap V3 (0.3%)</option>
              <option>Uniswap V3 (0.05%)</option>
              <option>Uniswap V3 (1%)</option>
            </select>
          </div>

          <div class="param-section">
            <label class="param-label">
              CEX交易所
              <span class="param-tooltip" title="Binance根据VIP等级和BNB抵扣有不同的手续费率">ℹ️</span>
            </label>
            <select v-model="cexExchange" class="input" @change="onCexExchangeChange">
              <option>Binance (0.1%)</option>
              <option>Binance (0.075%)</option>
              <option>Binance (0.05%)</option>
            </select>
          </div>
          
          <button class="btn btn-primary w-full" @click="startAnalysis" :disabled="loading">
            {{ loading ? '分析中...' : '开始分析' }}
          </button>
          
          <div class="param-section">
            <label class="param-label">
              图表显示选项
              <span class="param-tooltip" title="选择要显示的分析图表类型，可根据需要开启或关闭">ℹ️</span>
            </label>
            <div class="checkbox-grid">
              <div class="checkbox-item">
                <input type="checkbox" id="showPie" v-model="showPie" />
                <label for="showPie">
                  交易方向比例
                  <span class="chart-tooltip" title="饼图显示交易方向的比例分布，帮助分析套利机会的主要流向">ℹ️</span>
                </label>
              </div>
              <div class="checkbox-item">
                <input type="checkbox" id="showSpreadDist" v-model="showSpreadDist" />
                <label for="showSpreadDist">
                  价差分布
                  <span class="chart-tooltip" title="直方图展示价差的频率分布，帮助分析价差的统计特征">ℹ️</span>
                </label>
              </div>
              <div class="checkbox-item">
                <input type="checkbox" id="showCorrelation" v-model="showCorrelation" />
                <label for="showCorrelation">
                  价格相关性
                  <span class="chart-tooltip" title="散点图展示两个交易所价格的相关性分析">ℹ️</span>
                </label>
              </div>
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

      <!-- 自定义时间日历组件 -->
      <div
        v-if="showCalendar"
        class="calendar-overlay"
        @click.self="hideCalendar"
      >
        <div class="calendar-popup">
          <div class="calendar-header">
            <h4>选择时间范围 (2025年9月)</h4>
            <button class="btn-close" @click="hideCalendar">×</button>
          </div>

          <div class="calendar-body">
            <!-- 月历网格 -->
            <div class="calendar-grid">
              <!-- 星期标题 -->
              <div class="calendar-weekdays">
                <div v-for="day in ['日', '一', '二', '三', '四', '五', '六']" :key="day" class="weekday">
                  {{ day }}
                </div>
              </div>

              <!-- 日期网格 -->
              <div class="calendar-days">
                <div
                  v-for="day in calendarDays"
                  :key="day.date"
                  class="calendar-day"
                  :class="{
                    'disabled': !day.enabled,
                    'selected': day.selected,
                    'in-range': day.inRange,
                    'range-start': day.isStart,
                    'range-end': day.isEnd
                  }"
                  @click="selectDay(day)"
                >
                  {{ day.date ? day.date.getDate() : '' }}
                </div>
              </div>
            </div>

            <!-- 快速选择 -->
            <div class="calendar-presets">
              <button class="btn-preset" @click="applyPreset('week1')">第1周</button>
              <button class="btn-preset" @click="applyPreset('week2')">第2周</button>
              <button class="btn-preset" @click="applyPreset('week3')">第3周</button>
              <button class="btn-preset" @click="applyPreset('week4')">第4周</button>
              <button class="btn-preset" @click="applyPreset('week5')">第5周</button>
            </div>
          </div>

          <div class="calendar-footer">
            <div class="selected-range">
              <span>已选择: {{ selectedRangeText }}</span>
            </div>
            <div class="calendar-actions">
              <button class="btn btn-secondary" @click="clearSelection">清空</button>
              <button class="btn btn-primary" @click="confirmSelection" :disabled="!hasValidSelection">
                确定
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧主图表区 -->
      <main class="main-content col-span-9">
        <!-- 价格对比图 -->
        <div class="card">
          <div class="card-header">
            <h3>Uniswap vs Binance 价格对比</h3>
            <div class="header-actions">
              <button
                class="btn-icon"
                @click="toggleLogScale"
                :title="logScale ? '切换到线性坐标轴' : '切换到对数坐标轴'"
              >
                {{ logScale ? 'LOG' : 'LIN' }}
              </button>
              <button
                class="btn-icon"
                @click="exportChart"
                title="导出图表为图片"
              >
                ↓
              </button>
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
        <div class="charts-grid" style="margin-top: 24px;">
          <!-- 饼图 -->
          <div v-if="showPie" class="chart-item">
            <div class="card">
              <div class="card-header">
                <h3>交易方向比例图</h3>
              </div>
              <chart-card
                title=""
                :height="280"
                :options="pieOptions"
                :loading="loading"
              />
            </div>
          </div>

          <!-- 价差分布 -->
          <div v-if="showSpreadDist" class="chart-item">
            <div class="card">
              <div class="card-header">
                <h3>价差分布</h3>
              </div>
              <chart-card
                v-if="spreadDistributionOptions"
                title=""
                :height="280"
                :options="spreadDistributionOptions"
                :loading="loading"
              />
              <div v-else class="chart-placeholder">
                <div class="placeholder-icon">📊</div>
                <div class="placeholder-text">数据加载中...</div>
              </div>
            </div>
          </div>

          <!-- 价格相关性 -->
          <div v-if="showCorrelation" class="chart-item">
            <div class="card">
              <div class="card-header">
                <h3>价格相关性</h3>
              </div>
              <chart-card
                v-if="correlationOptions"
                title=""
                :height="280"
                :options="correlationOptions"
                :loading="loading"
              />
              <div v-else class="chart-placeholder">
                <div class="placeholder-icon">📊</div>
                <div class="placeholder-text">数据加载中...</div>
              </div>
            </div>
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
      dexPool: 'Uniswap V3 (0.3%)',
      cexExchange: 'Binance (0.1%)',
      logScale: false,
      showPie: true,
      showSpreadDist: true,
      showCorrelation: true,

      stats: {
        signalCount: 0,
        avgSpread: '0.00',
        totalProfit: '0.00'
      },

      // 时间选择相关
      timePreset: 'full', // full, first-half, second-half, custom
      showCalendar: false,
      selectedDates: [], // 选中的日期数组
      calendarDays: [], // 日历天数数据
      customRange: {
        start: '2025-09-01',
        end: '2025-09-30'
      }
    }
  },
  
  computed: {
    ...mapState(['priceData', 'spreadData', 'signals']),

    customRangeLabel() {
      if (this.timePreset === 'full') {
        return '2025年9月1日 - 2025年9月30日'
      } else if (this.timePreset === 'first-half') {
        return '2025年9月1日 - 2025年9月15日'
      } else if (this.timePreset === 'second-half') {
        return '2025年9月16日 - 2025年9月30日'
      } else if (this.timePreset === 'custom') {
        const startDate = new Date(this.customRange.start)
        const endDate = new Date(this.customRange.end)
        return `${startDate.getFullYear()}年${startDate.getMonth() + 1}月${startDate.getDate()}日 - ${endDate.getFullYear()}年${endDate.getMonth() + 1}月${endDate.getDate()}日`
      }
      return '请选择时间范围'
    },

    isCustomMode() {
      return this.timePreset === 'custom'
    },

    selectedRangeText() {
      if (this.selectedDates.length === 0) return '未选择'
      if (this.selectedDates.length === 1) {
        const date = this.selectedDates[0]
        return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`
      }
      const sorted = [...this.selectedDates].sort((a, b) => a - b)
      const start = sorted[0]
      const end = sorted[sorted.length - 1]
      return `${start.getFullYear()}年${start.getMonth() + 1}月${start.getDate()}日 - ${end.getFullYear()}年${end.getMonth() + 1}月${end.getDate()}日`
    },

    hasValidSelection() {
      return this.selectedDates.length >= 1
    },

    
    priceCompareOptions() {
      if (!this.priceData) return null

      const dexData = this.priceData.dex.map(d => [d.t, d.p])
      const cexData = this.priceData.cex.map(d => [d.t, d.p])

      // 计算时间范围，用于动态调整横坐标显示格式
      const allData = [...cexData, ...dexData]
      const timeRange = this.calculateTimeRange(allData)
      const axisLabelFormatter = this.getDynamicAxisFormatter(timeRange)

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
          textStyle: { color: '#111827' },
          formatter: (params) => {
            const date = new Date(params[0].data[0])
            const timeStr = date.toLocaleString('zh-CN', {
              year: 'numeric',
              month: '2-digit',
              day: '2-digit',
              hour: '2-digit',
              minute: '2-digit'
            })
            let result = `时间: ${timeStr}<br/>`
            params.forEach(param => {
              result += `${param.seriesName}: ${param.data[1].toFixed(2)} USDT<br/>`
            })
            return result
          }
        },
        xAxis: {
          type: 'time',
          axisLabel: {
            color: '#6b7280',
            formatter: axisLabelFormatter
          },
          axisLine: { lineStyle: { color: '#e5e7eb' } },
          splitLine: { lineStyle: { color: '#f3f4f6', opacity: 0.5 } }
        },
        yAxis: {
          type: this.logScale ? 'log' : 'value',
          name: 'Price (USDT)',
          nameTextStyle: { color: '#6b7280' },
          axisLabel: {
            color: '#6b7280',
            formatter: (value) => value.toFixed(2)
          },
          splitLine: { lineStyle: { color: '#f3f4f6' } },
          axisLine: { lineStyle: { color: '#e5e7eb' } }
        },
        series: [
          {
            name: 'Uniswap V3',
            type: 'line',
            data: dexData,
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
            },
            smooth: true
          },
          {
            name: 'Binance',
            type: 'line',
            data: cexData,
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
            },
            smooth: true
          }
        ]
      }
    },
    
    pieOptions() {
      // 从signals数据中统计交易方向分布
      if (!this.signals || this.signals.length === 0) {
        return {
          responsive: true,
          maintainAspectRatio: false,
          tooltip: {
            trigger: 'item',
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            borderColor: '#e5e7eb',
            textStyle: { color: '#111827' }
          },
          series: [{
            type: 'pie',
            center: ['50%', '50%'],
            radius: ['35%', '65%'],
            data: [
              { name: '暂无数据', value: 0 }
            ]
          }]
        }
      }

      // 统计交易方向
      let uniswapToBinance = 0
      let binanceToUniswap = 0

      this.signals.forEach(signal => {
        const direction = signal.direction || ''
        if (direction.includes('CEX->DEX') || direction.includes('Binance->Uniswap') || direction === 'Long') {
          binanceToUniswap++
        } else if (direction.includes('DEX->CEX') || direction.includes('Uniswap->Binance') || direction === 'Short') {
          uniswapToBinance++
        } else {
          // 根据价差判断方向：如果CEX价格 > DEX价格，应该是CEX->DEX
          if (signal.cexPrice && signal.dexPrice) {
            if (signal.cexPrice > signal.dexPrice) {
              binanceToUniswap++
            } else {
              uniswapToBinance++
            }
          }
        }
      })

      const directionData = [
        { name: 'Uniswap → Binance', value: uniswapToBinance },
        { name: 'Binance → Uniswap', value: binanceToUniswap }
      ]

      return {
        responsive: true,
        maintainAspectRatio: false,
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e5e7eb',
          textStyle: { color: '#111827' },
          formatter: '{b}: {c} 次 ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          top: 'center',
          textStyle: {
            color: '#6b7280',
            fontSize: 12
          },
          itemGap: 8
        },
        series: [{
          type: 'pie',
          center: ['65%', '50%'],
          radius: ['35%', '65%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 8,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false,
            position: 'center'
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 16,
              fontWeight: 'bold',
              formatter: '{d}%'
            }
          },
          labelLine: {
            show: false
          },
          data: directionData,
          color: ['#10b981', '#f97316']
        }]
      }
    },

    spreadDistributionOptions() {
      if (!this.spreadData || !Array.isArray(this.spreadData) || this.spreadData.length === 0) {
        return null
      }

      try {
        const spreads = this.spreadData.map(d => d.spread)
        const bins = this.calculateHistogram(spreads, 20)

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
            top: '15%',
            containLabel: true
          },
          xAxis: {
            type: 'value',
            name: '价差 (USDT)',
            nameTextStyle: { color: '#6b7280' },
            axisLabel: { color: '#6b7280' },
            axisLine: { lineStyle: { color: '#e5e7eb' } }
          },
          yAxis: {
            type: 'value',
            name: '频次',
            nameTextStyle: { color: '#6b7280' },
            axisLabel: { color: '#6b7280' },
            axisLine: { lineStyle: { color: '#e5e7eb' } },
            splitLine: { lineStyle: { color: '#f3f4f6' } }
          },
          series: [{
            type: 'bar',
            data: bins,
            itemStyle: { color: '#8b5cf6' },
            barWidth: '80%'
          }]
        }
      } catch (error) {
        console.error('spreadDistributionOptions 计算错误:', error)
        return null
      }
    },

    correlationOptions() {
      if (!this.priceData || !this.priceData.cex || !this.priceData.dex) return null

      try {
        // 创建散点图数据：CEX价格 vs DEX价格
        const scatterData = []
        const len = Math.min(this.priceData.cex.length, this.priceData.dex.length)

        for (let i = 0; i < len; i++) {
          const cexPrice = this.priceData.cex[i]?.p || 0
          const dexPrice = this.priceData.dex[i]?.p || 0
          if (cexPrice > 0 && dexPrice > 0) {
            scatterData.push([cexPrice, dexPrice])
          }
        }

        return {
          tooltip: {
            trigger: 'item',
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            borderColor: '#e5e7eb',
            textStyle: { color: '#111827' },
            formatter: (params) => {
              return `CEX: ${params.data[0].toFixed(2)} USDT<br/>DEX: ${params.data[1].toFixed(2)} USDT`
            }
          },
          grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            top: '15%',
            containLabel: true
          },
          xAxis: {
            type: 'value',
            name: 'CEX价格 (USDT)',
            nameTextStyle: { color: '#6b7280' },
            axisLabel: { color: '#6b7280' },
            axisLine: { lineStyle: { color: '#e5e7eb' } },
            splitLine: { lineStyle: { color: '#f3f4f6' } }
          },
          yAxis: {
            type: 'value',
            name: 'DEX价格 (USDT)',
            nameTextStyle: { color: '#6b7280' },
            axisLabel: { color: '#6b7280' },
            axisLine: { lineStyle: { color: '#e5e7eb' } },
            splitLine: { lineStyle: { color: '#f3f4f6' } }
          },
          series: [{
            type: 'scatter',
            data: scatterData,
            symbolSize: 4,
            itemStyle: {
              color: 'rgba(59, 130, 246, 0.6)'
            },
            emphasis: {
              itemStyle: {
                color: '#3b82f6'
              }
            }
          }]
        }
      } catch (error) {
        console.error('correlationOptions 计算错误:', error)
        return null
      }
    }
  },

  created() {
    console.log('Overview component created, loading data...')
    this.loadData()
  },
  
  methods: {
    ...mapActions(['loadPriceData', 'loadSpreadData', 'detectSignals', 'updateConfig']),

    // 时间选择相关方法
    selectTimePreset(preset) {
      this.timePreset = preset

      switch (preset) {
        case 'full':
          this.customRange = { start: '2025-09-01', end: '2025-09-30' }
          break
        case 'first-half':
          this.customRange = { start: '2025-09-01', end: '2025-09-15' }
          break
        case 'second-half':
          this.customRange = { start: '2025-09-16', end: '2025-09-30' }
          break
        case 'custom':
          // 保持当前选择，不立即切换到日历
          break
      }

      if (preset !== 'custom') {
        this.loadData()
      }
    },

    toggleCalendar() {
      if (this.timePreset === 'custom') {
        if (!this.showCalendar) {
          this.initializeCalendar()
        }
        this.showCalendar = !this.showCalendar
      }
    },

    hideCalendar() {
      this.showCalendar = false
    },

    initializeCalendar() {
      const year = 2025
      const month = 8 // JavaScript中月份从0开始，9月是8

      // 生成2025年9月的日历
      this.calendarDays = []

      // 获取9月1日是星期几
      const firstDay = new Date(year, month, 1)
      const firstDayOfWeek = firstDay.getDay()

      // 获取9月的天数
      const lastDay = new Date(year, month + 1, 0)
      const totalDays = lastDay.getDate()

      // 生成日历网格（6行 x 7列）
      for (let i = 0; i < 42; i++) {
        const dayNumber = i - firstDayOfWeek + 1
        const isCurrentMonth = dayNumber >= 1 && dayNumber <= totalDays

        if (isCurrentMonth) {
          const date = new Date(year, month, dayNumber)
          const isSelected = this.selectedDates.some(d =>
            d.getFullYear() === year && d.getMonth() === month && d.getDate() === dayNumber
          )

          this.calendarDays.push({
            date,
            enabled: true,
            selected: isSelected,
            inRange: false,
            isStart: false,
            isEnd: false
          })
        } else {
          // 空白日期
          this.calendarDays.push({
            date: null,
            enabled: false,
            selected: false,
            inRange: false,
            isStart: false,
            isEnd: false
          })
        }
      }

      this.updateCalendarSelection()
    },

    selectDay(day) {
      if (!day.enabled || !day.date) return

      const date = day.date
      const dateStr = date.toISOString().split('T')[0]

      // 如果已经选择了这个日期，则取消选择
      const existingIndex = this.selectedDates.findIndex(d =>
        d.getTime() === date.getTime()
      )

      if (existingIndex >= 0) {
        this.selectedDates.splice(existingIndex, 1)
      } else {
        // 如果还没有选择日期，或者已经选择了2个日期，则重新开始选择
        if (this.selectedDates.length >= 2) {
          this.selectedDates = [date]
        } else {
          this.selectedDates.push(date)
        }
      }

      this.updateCalendarSelection()
    },

    updateCalendarSelection() {
      // 更新日历中日期的选择状态
      this.calendarDays.forEach(day => {
        if (!day.date) return

        const isSelected = this.selectedDates.some(d => d.getTime() === day.date.getTime())

        if (this.selectedDates.length === 2) {
          const sorted = [...this.selectedDates].sort((a, b) => a - b)
          const inRange = day.date >= sorted[0] && day.date <= sorted[1]
          const isStart = day.date.getTime() === sorted[0].getTime()
          const isEnd = day.date.getTime() === sorted[1].getTime()

          day.inRange = inRange
          day.isStart = isStart
          day.isEnd = isEnd
          day.selected = isSelected
        } else {
          day.inRange = false
          day.isStart = false
          day.isEnd = false
          day.selected = isSelected
        }
      })
    },

    applyPreset(preset) {
      const year = 2025
      const month = 8 // 9月

      switch (preset) {
        case 'week1':
          this.selectedDates = [
            new Date(year, month, 1),
            new Date(year, month, 7)
          ]
          break
        case 'week2':
          this.selectedDates = [
            new Date(year, month, 8),
            new Date(year, month, 14)
          ]
          break
        case 'week3':
          this.selectedDates = [
            new Date(year, month, 15),
            new Date(year, month, 21)
          ]
          break
        case 'week4':
          this.selectedDates = [
            new Date(year, month, 22),
            new Date(year, month, 28)
          ]
          break
        case 'week5':
          this.selectedDates = [
            new Date(year, month, 29),
            new Date(year, month, 30)
          ]
          break
      }

      this.updateCalendarSelection()
    },

    clearSelection() {
      this.selectedDates = []
      this.updateCalendarSelection()
    },

    confirmSelection() {
      if (this.selectedDates.length === 0) return

      const sorted = [...this.selectedDates].sort((a, b) => a - b)
      this.customRange.start = sorted[0].toISOString().split('T')[0]
      this.customRange.end = sorted[sorted.length - 1].toISOString().split('T')[0]

      this.hideCalendar()
      this.loadData()
    },

    async loadData() {
      console.log('loadData called, timePreset:', this.timePreset)
      this.loading = true
      try {
        // 根据选择的预设设置时间范围
        let startDate, endDate

        switch (this.timePreset) {
          case 'full':
            startDate = '2025-09-01'
            endDate = '2025-09-30'
            break
          case 'first-half':
            startDate = '2025-09-01'
            endDate = '2025-09-15'
            break
          case 'second-half':
            startDate = '2025-09-16'
            endDate = '2025-09-30'
            break
          case 'custom':
            startDate = this.customRange.start
            endDate = this.customRange.end
            break
          default:
            startDate = '2025-09-01'
            endDate = '2025-09-30'
        }

        const startTime = new Date(startDate).getTime()
        const endTime = new Date(endDate).getTime()
        
        console.log('Time range:', new Date(startTime), 'to', new Date(endTime))

        await this.updateConfig({
          timeRange: {
            start: startTime,
            end: endTime
          }
        })

        console.log('Config updated, loading data...')
        await Promise.all([
          this.loadPriceData(),
          this.loadSpreadData(),
          this.detectSignals()
        ])
        console.log('Data loaded successfully')
        this.updateStats()
      } catch (error) {
        console.error('加载数据失败:', error)
        alert('数据加载失败: ' + error.message)
      } finally {
        this.loading = false
      }
    },
    
    async startAnalysis() {
      await this.loadData()
    },
    
    
    onDexPoolChange() {
      // 从选项中提取费率 "Uniswap V3 (0.3%)" -> 0.003
      const match = this.dexPool.match(/\(([\d.]+)%\)/)
      if (match) {
        const feePercent = parseFloat(match[1])
        const feeRate = feePercent / 100
        console.log('Updating DEX fee to:', feeRate)
        this.updateConfig({
          detector: {
            ...this.$store.state.config.detector,
            fees: {
              ...this.$store.state.config.detector.fees,
              dex: feeRate
            }
          }
        })
      }
      this.loadData()
    },

    onCexExchangeChange() {
      // 从选项中提取费率 "Binance (0.1%)" -> 0.001
      const match = this.cexExchange.match(/\(([\d.]+)%\)/)
      if (match) {
        const feePercent = parseFloat(match[1])
        const feeRate = feePercent / 100
        console.log('Updating CEX fee to:', feeRate)
        this.updateConfig({
          detector: {
            ...this.$store.state.config.detector,
            fees: {
              ...this.$store.state.config.detector.fees,
              cex: feeRate
            }
          }
        })
      }
      this.loadData()
    },

    toggleLogScale() {
      this.logScale = !this.logScale
    },

    exportChart() {
      alert('图表导出功能开发中...')
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

    calculateTimeRange(data) {
      if (!data || data.length === 0) return { duration: 0, start: null, end: null }

      const timestamps = data.map(d => d[0]).sort((a, b) => a - b)
      const start = timestamps[0]
      const end = timestamps[timestamps.length - 1]
      const duration = end - start // 毫秒

      return { duration, start, end }
    },

    getDynamicAxisFormatter(timeRange) {
      const { duration } = timeRange

      // 少于1小时：显示 HH:MM
      if (duration < 60 * 60 * 1000) {
        return (value) => {
          const date = new Date(value)
          return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
        }
      }
      // 少于1天：显示 MM/DD HH:MM
      else if (duration < 24 * 60 * 60 * 1000) {
        return (value) => {
          const date = new Date(value)
          return `${(date.getMonth() + 1).toString().padStart(2, '0')}/${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
        }
      }
      // 少于7天：显示 MM/DD
      else if (duration < 7 * 24 * 60 * 60 * 1000) {
        return (value) => {
          const date = new Date(value)
          return `${(date.getMonth() + 1).toString().padStart(2, '0')}/${date.getDate().toString().padStart(2, '0')}`
        }
      }
      // 超过7天：显示 MM/DD
      else {
        return (value) => {
          const date = new Date(value)
          return `${(date.getMonth() + 1).toString().padStart(2, '0')}/${date.getDate().toString().padStart(2, '0')}`
        }
      }
    },

    calculateHistogram(data, bins) {
      if (!data || data.length === 0) return []

      const min = Math.min(...data)
      const max = Math.max(...data)

      // 处理所有值相等的情况
      if (min === max) {
        return [[min, data.length]]
      }

      const binWidth = (max - min) / bins
      const histogram = new Array(bins).fill(0)

      data.forEach(value => {
        const binIndex = Math.min(Math.floor((value - min) / binWidth), bins - 1)
        histogram[binIndex]++
      })

      return histogram.map((count, i) => [min + i * binWidth, count])
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

.time-range-display {
  padding: 12px 16px;
  background: $bg-primary;
  border-radius: 8px;
  border: 1px solid $border-color;
}

.time-range-text {
  font-size: 14px;
  font-weight: 600;
  color: $text-primary;
  display: block;
}

.time-range-note {
  font-size: 12px;
  color: $text-tertiary;
  display: block;
  margin-top: 4px;
}

.param-tooltip, .chart-tooltip {
  display: inline-block;
  margin-left: 6px;
  color: $color-primary;
  font-size: 12px;
  cursor: help;
  opacity: 0.7;
  transition: opacity $transition-fast;

  &:hover {
    opacity: 1;
  }
}

.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 8px;

  input[type="checkbox"] {
    width: 16px;
    height: 16px;
    accent-color: $color-primary;
  }

  label {
    font-size: 13px;
    color: $text-secondary;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 4px;
  }
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
  gap: 16px;
  margin: 24px 0;

  @media (max-width: 1400px) {
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  }

  @media (max-width: 1200px) {
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  }

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}

.chart-item {
  display: flex;
  flex-direction: column;
  min-width: 0; // 允许flex子项缩小

  .card {
    height: 100%;
    display: flex;
    flex-direction: column;

    .card-header {
      flex-shrink: 0;
      padding: 16px 20px;
      border-bottom: 1px solid $border-color;

      h3 {
        margin: 0;
        font-size: 14px;
        font-weight: 600;
        color: $text-primary;
      }
    }

    .chart-card {
      flex: 1;
      min-height: 280px;
    }
  }
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 280px;
  background: $bg-primary;
  border-radius: 8px;
  border: 2px dashed $border-color;

  .placeholder-icon {
    font-size: 48px;
    opacity: 0.5;
    margin-bottom: 16px;
  }

  .placeholder-text {
    font-size: 14px;
    color: $text-tertiary;
    text-align: center;
  }
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

// 时间选择相关样式
.time-quick-select {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.btn-time-preset {
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 500;
  border: 1px solid $border-color;
  border-radius: 6px;
  background: transparent;
  color: $text-secondary;
  cursor: pointer;
  transition: all $transition-fast;

  &:hover {
    border-color: $color-primary;
    color: $color-primary;
  }

  &.active {
    background: $color-primary;
    color: white;
    border-color: $color-primary;
  }
}

.btn-calendar-toggle {
  margin-left: 8px;
  padding: 6px 10px;
  font-size: 14px;
  background: transparent;
  border: 1px solid $border-color;
  border-radius: 4px;
  color: $text-secondary;
  cursor: pointer;
  transition: all $transition-fast;

  &:hover:not(:disabled) {
    border-color: $color-primary;
    color: $color-primary;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

// 日历组件样式
.calendar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.calendar-popup {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  width: 320px;
  max-width: 90vw;
  overflow: hidden;
  animation: calendarSlideIn 0.2s ease;
}

.calendar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;

  h4 {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: #111827;
  }

  .btn-close {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    color: #6b7280;
    font-size: 18px;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      border-color: #ef4444;
      color: #ef4444;
    }
  }
}

.calendar-body {
  padding: 20px 24px;
}

.calendar-grid {
  margin-bottom: 16px;
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
  margin-bottom: 8px;
}

.weekday {
  padding: 8px 4px;
  text-align: center;
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
}

.calendar-days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
}

.calendar-day {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #111827;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
  position: relative;

  &:hover:not(.disabled) {
    background: #f3f4f6;
  }

  &.disabled {
    color: #d1d5db;
    cursor: not-allowed;
  }

  &.selected {
    background: #3b82f6;
    color: white;
  }

  &.in-range {
    background: #dbeafe;
    color: #1e40af;
  }

  &.range-start,
  &.range-end {
    background: #1d4ed8;
    color: white;
  }

  &.range-start::before {
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 4px;
    height: 60%;
    background: white;
    border-radius: 2px;
  }

  &.range-end::after {
    content: '';
    position: absolute;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 4px;
    height: 60%;
    background: white;
    border-radius: 2px;
  }
}

.calendar-presets {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
  margin-bottom: 20px;
}

.btn-preset {
  padding: 8px 6px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  background: white;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: #3b82f6;
    color: #3b82f6;
  }

  &:active {
    background: #3b82f6;
    color: white;
  }
}

.calendar-footer {
  padding: 16px 24px;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.selected-range {
  margin-bottom: 12px;

  span {
    font-size: 14px;
    color: #374151;
    font-weight: 500;
  }
}

.calendar-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@keyframes calendarSlideIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
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

