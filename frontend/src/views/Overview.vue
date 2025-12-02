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
              <span class="param-tooltip" title="支持2025年9月内的日期选择">ℹ️</span>
            </label>

            <!-- 模式切换按钮 -->
            <div class="time-mode-select">
              <button
                class="btn-mode"
                :class="{ active: timeMode === 'single' }"
                @click="switchTimeMode('single')"
              >
                单天
              </button>
              <button
                class="btn-mode"
                :class="{ active: timeMode === 'range' }"
                @click="switchTimeMode('range')"
              >
                范围
              </button>
            </div>

            <!-- 嵌入的日历 -->
            <div class="embedded-calendar">
              <div class="calendar-month-header">
                <span class="month-title">2025年9月</span>
              </div>
              
              <!-- 星期标题 -->
              <div class="calendar-weekdays">
                <div v-for="day in ['日', '一', '二', '三', '四', '五', '六']" :key="day" class="weekday">
                  {{ day }}
                </div>
              </div>

              <!-- 日期网格 -->
              <div class="calendar-days-grid">
                <div
                  v-for="day in calendarDays"
                  :key="day.date ? day.date.getTime() : `empty-${day.index}`"
                  class="calendar-day-cell"
                  :class="{
                    'disabled': !day.enabled,
                    'selected': day.selected,
                    'in-range': day.inRange,
                    'range-start': day.isStart,
                    'range-end': day.isEnd,
                    'today': day.isToday
                  }"
                  @click="handleDayClick(day)"
                >
                  {{ day.date ? day.date.getDate() : '' }}
                </div>
              </div>
            </div>

            <!-- 当前选择显示 -->
            <div class="time-range-display">
              <span class="time-range-text">{{ currentSelectionLabel }}</span>
              <button 
                v-if="timeMode === 'range'" 
                class="btn-confirm-range" 
                @click.stop="confirmRangeSelection"
                :disabled="loading || !hasRangeSelection"
                :title="!hasRangeSelection ? '请先选择开始和结束日期' : ''"
              >
                {{ loading ? '加载中...' : '确定' }}
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
            <div class="checkbox-item">
              <input type="checkbox" id="showDex" v-model="showDex" />
              <label for="showDex">
                DEX池 (Uniswap V3)
                <span class="param-tooltip" title="显示/隐藏 Uniswap V3 价格线">ℹ️</span>
            </label>
            </div>
          </div>

          <div class="param-section">
            <div class="checkbox-item">
              <input type="checkbox" id="showCex" v-model="showCex" />
              <label for="showCex">
                CEX交易所 (Binance)
                <span class="param-tooltip" title="显示/隐藏 Binance 价格线">ℹ️</span>
            </label>
            </div>
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
                <input type="checkbox" id="showRadar" v-model="showRadar" />
                <label for="showRadar">
                  雷达图
                  <span class="chart-tooltip" title="雷达图展示套利机会的多个维度指标，包括价差幅度、交易频率、潜在利润等">ℹ️</span>
                </label>
              </div>
              <div class="checkbox-item">
                <input type="checkbox" id="showPie" v-model="showPie" />
                <label for="showPie">
                  交易方向比例
                  <span class="chart-tooltip" title="饼图显示交易方向的比例分布，帮助分析套利机会的主要流向">ℹ️</span>
                </label>
              </div>
              <div class="checkbox-item">
                <input type="checkbox" id="showHeatmap" v-model="showHeatmap" />
                <label for="showHeatmap">
                  价差热力图
                  <span class="chart-tooltip" title="热力图展示价差在不同时间段的分布情况，颜色深浅表示Z-Score强度">ℹ️</span>
                </label>
              </div>
              <div class="checkbox-item">
                <input type="checkbox" id="showVolumeChart" v-model="showVolumeChart" />
                <label for="showVolumeChart">
                  成交量对比
                  <span class="chart-tooltip" title="柱状图对比不同交易所的成交量变化趋势">ℹ️</span>
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


      <!-- 右侧主图表区 -->
      <main class="main-content col-span-9">
        <!-- 价格对比图（所有模式都显示折线图） -->
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
            :height="800"
            :options="priceCompareOptions"
            :loading="loading"
          />
        </div>

        <!-- 单天模式：在价格对比图下方显示两个K线图（按小时） -->
        <template v-if="timeMode === 'single'">
          <!-- Uniswap V3 K线图 -->
          <div v-if="showDex" class="card" style="margin-top: 24px;">
            <div class="card-header">
              <h3>Uniswap V3 价格K线图（按小时）</h3>
            </div>
            <chart-card
              title=""
              :height="400"
              :options="dexCandlestickOptions"
              :loading="loading"
            />
          </div>
          
          <!-- Binance K线图 -->
          <div v-if="showCex" class="card" style="margin-top: 24px;">
            <div class="card-header">
              <h3>Binance 价格K线图（按小时）</h3>
            </div>
            <chart-card
              title=""
              :height="400"
              :options="cexCandlestickOptions"
              :loading="loading"
            />
          </div>
        </template>
        
        <!-- 下方图表组 -->
        <div class="charts-grid" style="margin-top: 24px;">
          <!-- 雷达图 -->
          <div v-if="showRadar" class="chart-item">
            <div class="card">
              <div class="card-header">
                <h3>实时套利机会雷达图</h3>
              </div>
              <chart-card
                title=""
                :height="280"
                :options="radarOptions"
                :loading="loading"
              />
            </div>
          </div>

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

          <!-- 热力图 -->
          <div v-if="showHeatmap" class="chart-item">
            <div class="card">
              <div class="card-header">
                <h3>价差热力图</h3>
              </div>
              <chart-card
                title=""
                :height="280"
                :options="heatmapOptions"
                :loading="loading"
              />
            </div>
          </div>

          <!-- 成交量对比 -->
          <div v-if="showVolumeChart" class="chart-item">
            <div class="card">
              <div class="card-header">
                <h3>成交量对比</h3>
              </div>
              <chart-card
                v-if="volumeCompareOptions"
                title=""
                :height="280"
                :options="volumeCompareOptions"
                :loading="loading"
              />
              <div v-else class="chart-placeholder">
                <div class="placeholder-icon">📊</div>
                <div class="placeholder-text">数据加载中...</div>
              </div>
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
import processedDataLoader from '@/utils/processedDataLoader'



export default {
  name: 'Overview',
  
  components: {
    ChartCard
  },
  
  data() {
    return {
      loading: false,
      showDex: true, // 是否显示 DEX 价格线
      showCex: true, // 是否显示 CEX 价格线
      logScale: false,
      candlestickOptions: null, // K线图配置（范围模式使用，已废弃）
      dexCandlestickOptions: null, // Uniswap V3 K线图配置（范围模式）
      cexCandlestickOptions: null, // Binance K线图配置（范围模式）
      showRadar: false,
      showPie: false,
      showHeatmap: false,
      showVolumeChart: false,
      showSpreadDist: false,
      showCorrelation: false,

      stats: {
        signalCount: 0,
        avgSpread: '0.00',
        totalProfit: '0.00'
      },

      // 时间选择相关
      timeMode: 'single', // 'single' 单天模式, 'range' 范围模式
      selectedDate: new Date(2025, 8, 1), // 单天模式选中的日期（默认9月1日）
      rangeStartDate: null, // 范围模式开始日期
      rangeEndDate: null, // 范围模式结束日期
      calendarDays: [] // 日历天数数据
    }
  },
  
  computed: {
    ...mapState(['priceData', 'spreadData', 'signals']),

    currentSelectionLabel() {
      if (this.timeMode === 'single') {
        if (this.selectedDate) {
          return `当前查看: ${this.selectedDate.getFullYear()}年${this.selectedDate.getMonth() + 1}月${this.selectedDate.getDate()}日`
        }
        return '请选择日期'
      } else {
        // 范围模式
        if (this.rangeStartDate && this.rangeEndDate) {
          const start = this.rangeStartDate
          const end = this.rangeEndDate
      return `${start.getFullYear()}年${start.getMonth() + 1}月${start.getDate()}日 - ${end.getFullYear()}年${end.getMonth() + 1}月${end.getDate()}日`
        } else if (this.rangeStartDate) {
          const start = this.rangeStartDate
          return `已选择开始: ${start.getFullYear()}年${start.getMonth() + 1}月${start.getDate()}日，请选择结束日期`
        }
        return '请选择日期范围'
      }
    },

    hasRangeSelection() {
      return this.rangeStartDate !== null && this.rangeEndDate !== null
    },

    
    priceCompareOptions() {
      // 所有模式都需要 priceData
      if (!this.priceData) return null

      // 单天模式：显示折线图
      // 完全按照原始数据绘制，不进行任何采样
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
          data: [
            ...(this.showDex ? ['Uniswap V3'] : []),
            ...(this.showCex ? ['Binance'] : [])
          ].filter(name => {
            // 在同步版本中，总是显示选中的legend，即使暂时没有数据
            // 因为数据可能还在加载中
            return true
          }),
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
          min: 0, // 最小值
          max: 9000, // 最大值
          axisLabel: {
            color: '#6b7280',
            formatter: (value) => value.toFixed(2)
          },
          splitLine: { lineStyle: { color: '#f3f4f6' } },
          axisLine: { lineStyle: { color: '#e5e7eb' } }
        },
        series: [
          // 根据复选框条件添加 Uniswap V3 系列
          ...(this.showDex ? [{
            name: 'Uniswap V3',
            type: 'line',
            data: dexData,
            symbol: 'none',
            lineStyle: { color: '#3b82f6', width: 2 }, // 细线
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
            smooth: false // 不使用平滑，完全按照原始数据点绘制
          }] : []),
          // 根据复选框条件添加 Binance 系列
          ...(this.showCex ? [{
            name: 'Binance',
            type: 'line',
            data: cexData,
            symbol: 'none',
            lineStyle: { color: '#10b981', width: 1 }, // 更细的线
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
            smooth: false // 不使用平滑，完全按照原始数据点绘制
          }] : [])
        ]
      }
    },
    
    radarOptions() {
      if (!this.signals || this.signals.length === 0) return null

      // 计算雷达图指标 (0-10 分)
      // 1. 价差幅度: 平均价差 / 平均价格 * 100 (basis points)
      const avgSpread = this.signals.reduce((sum, s) => sum + Math.abs(s.spread), 0) / this.signals.length
      const avgPrice = this.signals.reduce((sum, s) => sum + (s.cexPrice + s.dexPrice)/2, 0) / this.signals.length
      const spreadScore = Math.min(10, (avgSpread / avgPrice) * 1000) // 假设1%价差(100bps)为满分

      // 2. 平均套利: 平均净利润
      const avgProfit = this.signals.reduce((sum, s) => sum + s.netProfit, 0) / this.signals.length
      const profitScore = Math.min(10, avgProfit / 10) // 假设平均100U利润为满分

      // 3. 交易频率: 信号数量 / 天数 (假设30天)
      const frequencyScore = Math.min(10, this.signals.length / 30 / 2) // 假设每天20个信号为满分

      // 4. 潜在利润: 总净利润 (对数刻度)
      const totalProfit = this.signals.reduce((sum, s) => sum + s.netProfit, 0)
      const totalProfitScore = Math.min(10, Math.log10(totalProfit > 0 ? totalProfit : 1) * 1.5)

      // 5. 市场波动: 暂时用价差标准差代替
      const spreadVariance = this.signals.reduce((sum, s) => sum + Math.pow(Math.abs(s.spread) - avgSpread, 2), 0) / this.signals.length
      const spreadStdDev = Math.sqrt(spreadVariance)
      const volatilityScore = Math.min(10, spreadStdDev / 5) 

      const radarData = [
        { metric: '价差幅度', value: parseFloat(spreadScore.toFixed(1)) },
        { metric: '平均套利', value: parseFloat(profitScore.toFixed(1)) },
        { metric: '交易频率', value: parseFloat(frequencyScore.toFixed(1)) },
        { metric: '潜在利润', value: parseFloat(totalProfitScore.toFixed(1)) },
        { metric: '市场波动', value: parseFloat(volatilityScore.toFixed(1)) }
      ]

      return {
        responsive: true,
        maintainAspectRatio: false,
        tooltip: {
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e5e7eb',
          textStyle: { color: '#111827' },
          formatter: (params) => {
            if (!params || !params.data || !params.data.value) return ''
            const value = params.data.value
            let result = `${params.seriesName}<br/>`
            radarData.forEach((item, index) => {
              result += `${item.metric}: ${value[index]}<br/>`
            })
            return result
          }
        },
        radar: {
          indicator: radarData.map(d => ({
            name: d.metric,
            max: 10,
            color: '#6b7280'
          })),
          center: ['50%', '50%'],
          radius: '70%',
          axisLine: { lineStyle: { color: '#e5e7eb' } },
          splitLine: { lineStyle: { color: '#e5e7eb', opacity: 0.5 } },
          splitArea: {
            areaStyle: {
              color: ['rgba(59, 130, 246, 0.05)', 'rgba(255, 255, 255, 0)']
            }
          },
          axisLabel: {
            show: false
          },
          name: {
            textStyle: {
              color: '#6b7280',
              fontSize: 12
            }
          }
        },
        series: [{
          type: 'radar',
          data: [{
            value: radarData.map(d => d.value),
            name: '套利指标',
            lineStyle: { color: '#3b82f6', width: 1.5 }, // 细线
            areaStyle: { color: 'rgba(59, 130, 246, 0.4)' },
            itemStyle: { color: '#3b82f6' },
            symbolSize: 6
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
    
    heatmapOptions() {
      if (!this.spreadData || this.spreadData.length === 0) return null

      const heatmapData = this.generateHeatmapData()

      return {
        responsive: true,
        maintainAspectRatio: false,
        tooltip: {
          position: 'top',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e5e7eb',
          textStyle: { color: '#111827' },
          formatter: (params) => {
            if (!params.data || !Array.isArray(params.data)) return ''
            const [hour, minute, value] = params.data
            return `时间: ${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}<br/>Z-Score: ${value.toFixed(2)}`
          }
        },
        grid: {
          left: '12%',
          right: '8%',
          top: '8%',
          bottom: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: this.generateHourLabels(),
          splitArea: { show: true, areaStyle: { color: ['rgba(0,0,0,0.02)', 'rgba(0,0,0,0.01)'] } },
          axisLabel: {
            color: '#6b7280',
            fontSize: 11,
            rotate: 0,
            interval: 2 // 每隔2个显示一个标签，避免拥挤
          },
          axisLine: { lineStyle: { color: '#e5e7eb' } },
          axisTick: { show: false }
        },
        yAxis: {
          type: 'category',
          data: this.generateMinuteLabels(),
          splitArea: { show: true, areaStyle: { color: ['rgba(0,0,0,0.02)', 'rgba(0,0,0,0.01)'] } },
          axisLabel: {
            color: '#6b7280',
            fontSize: 11
          },
          axisLine: { lineStyle: { color: '#e5e7eb' } },
          axisTick: { show: false }
        },
        visualMap: {
          min: -3,
          max: 3,
          calculable: true,
          orient: 'horizontal',
          left: 'center',
          bottom: '2%',
          itemWidth: 12,
          itemHeight: 80,
          text: ['高', '低'],
          textStyle: {
            color: '#6b7280',
            fontSize: 11
          },
          inRange: {
            color: ['#ef4444', '#f3f4f6', '#10b981']
          }
        },
        series: [{
          name: 'Z-Score',
          type: 'heatmap',
          data: heatmapData,
          emphasis: {
            itemStyle: {
              shadowBlur: 8,
              shadowColor: 'rgba(0, 0, 0, 0.2)'
            }
          }
        }]
      }
    },

    volumeCompareOptions() {
      if (!this.priceData || !this.priceData.cex || !this.priceData.dex) {
        return null
      }

      try {
        // 优化大数据集的处理：只处理前10000个点以提高性能
        const maxPoints = Math.min(10000, Math.min(this.priceData.cex.length, this.priceData.dex.length))
        const data = []

        for (let i = 0; i < maxPoints; i++) {
          data.push({
            time: this.priceData.cex[i].t,
            cexVolume: this.priceData.cex[i].v || 0,
            dexVolume: this.priceData.dex[i]?.v || 0
          })
        }

        const timeData = data.map(d => d.time)
        const cexVolumes = data.map(d => d.cexVolume)
        const dexVolumes = data.map(d => d.dexVolume)

        return {
          tooltip: {
            trigger: 'axis',
            backgroundColor: 'rgba(255, 255, 255, 0.95)',
            borderColor: '#e5e7eb',
            textStyle: { color: '#111827' }
          },
          legend: {
            data: ['CEX成交量', 'DEX成交量'],
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
            },
            axisLine: { lineStyle: { color: '#e5e7eb' } }
          },
          yAxis: {
            type: 'value',
            name: '成交量',
            nameTextStyle: { color: '#6b7280' },
            axisLabel: {
              color: '#6b7280',
              formatter: (value) => (value / 1000).toFixed(0) + 'K'
            },
            splitLine: { lineStyle: { color: '#f3f4f6' } },
            axisLine: { lineStyle: { color: '#e5e7eb' } }
          },
          series: [
            {
              name: 'CEX成交量',
              type: 'bar',
              data: cexVolumes.map((v, i) => [timeData[i], v]),
              itemStyle: { color: '#3b82f6' }
            },
            {
              name: 'DEX成交量',
              type: 'bar',
              data: dexVolumes.map((v, i) => [timeData[i], v]),
              itemStyle: { color: '#10b981' }
            }
          ]
        }
      } catch (error) {
        console.error('volumeCompareOptions 计算错误:', error)
        return null
      }
    },

    spreadDistributionOptions() {
      if (!this.spreadData || !Array.isArray(this.spreadData) || this.spreadData.length === 0) {
        return null
      }

      try {
        // 限制为前5000个点以提高性能
        const spreads = this.spreadData.slice(0, 5000).map(d => d.spread)
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
        // 限制为前2000个点以提高性能
        const scatterData = []
        const len = Math.min(2000, Math.min(this.priceData.cex.length, this.priceData.dex.length))

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
    this.initializeCalendar()
    this.loadData()
  },
  
  methods: {
    ...mapActions(['loadPriceData', 'loadSpreadData', 'detectSignals', 'updateConfig']),

    // 切换时间模式
    switchTimeMode(mode) {
      this.timeMode = mode
      if (mode === 'single') {
        // 切换到单天模式时，清理K线图配置和范围选择状态
        this.dexCandlestickOptions = null
        this.cexCandlestickOptions = null
        // 清空范围选择状态（但不影响selectedDate）
        this.rangeStartDate = null
        this.rangeEndDate = null
        // 刷新日历显示状态
        this.updateCalendarSelection()
        // 如果有选中的日期，立即加载
        if (this.selectedDate) {
          this.loadData()
        }
      } else {
        // 切换到范围模式时，清空范围选择和K线图配置
        this.rangeStartDate = null
        this.rangeEndDate = null
        this.dexCandlestickOptions = null
        this.cexCandlestickOptions = null
        this.updateCalendarSelection()
      }
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

      // 获取今天的日期（用于标记今天）
      const today = new Date()
      const isCurrentMonth = today.getFullYear() === year && today.getMonth() === month

      // 生成日历网格（6行 x 7列）
      for (let i = 0; i < 42; i++) {
        const dayNumber = i - firstDayOfWeek + 1
        const isCurrentMonthDay = dayNumber >= 1 && dayNumber <= totalDays

        if (isCurrentMonthDay) {
          const date = new Date(year, month, dayNumber)
          const isToday = isCurrentMonth && dayNumber === today.getDate()

          this.calendarDays.push({
            date,
            enabled: true,
            index: i,
            isToday: isToday,
            selected: false,
            inRange: false,
            isStart: false,
            isEnd: false
          })
        } else {
          // 空白日期
          this.calendarDays.push({
            date: null,
            enabled: false,
            index: i,
            isToday: false,
            selected: false,
            inRange: false,
            isStart: false,
            isEnd: false
          })
        }
      }

      this.updateCalendarSelection()
    },

    handleDayClick(day) {
      if (!day.enabled || !day.date) return

      if (this.timeMode === 'single') {
        // 单天模式：点击立即加载
        this.selectedDate = day.date
        this.updateCalendarSelection()
        this.loadData()
      } else {
          // 范围模式：选择开始和结束日期
          if (!this.rangeStartDate || (this.rangeStartDate && this.rangeEndDate)) {
            // 开始新的范围选择
            this.rangeStartDate = day.date
            this.rangeEndDate = null
            console.log('选择开始日期:', day.date)
        } else {
            // 选择结束日期
            if (day.date < this.rangeStartDate) {
              // 如果选择的日期早于开始日期，交换它们
              this.rangeEndDate = this.rangeStartDate
              this.rangeStartDate = day.date
            } else {
              this.rangeEndDate = day.date
            }
            console.log('选择结束日期:', day.date, '范围:', this.rangeStartDate, '到', this.rangeEndDate)
          }
      this.updateCalendarSelection()
          // 强制更新视图
          this.$forceUpdate()
        }
    },

    updateCalendarSelection() {
      // 更新日历中日期的选择状态
      this.calendarDays.forEach(day => {
        if (!day.date) return

        if (this.timeMode === 'single') {
          // 单天模式
          day.selected = this.selectedDate && day.date.getTime() === this.selectedDate.getTime()
          day.inRange = false
          day.isStart = false
          day.isEnd = false
        } else {
          // 范围模式
          if (this.rangeStartDate && this.rangeEndDate) {
            const sorted = [this.rangeStartDate, this.rangeEndDate].sort((a, b) => a - b)
            const start = sorted[0]
            const end = sorted[1]
            day.inRange = day.date >= start && day.date <= end
            day.isStart = day.date.getTime() === start.getTime()
            day.isEnd = day.date.getTime() === end.getTime()
            day.selected = day.isStart || day.isEnd
          } else if (this.rangeStartDate) {
            day.selected = day.date.getTime() === this.rangeStartDate.getTime()
            day.inRange = false
            day.isStart = day.selected
            day.isEnd = false
          } else {
            day.selected = false
          day.inRange = false
          day.isStart = false
          day.isEnd = false
          }
        }
      })
    },

    confirmRangeSelection() {
      console.log('确认范围选择', {
        rangeStartDate: this.rangeStartDate,
        rangeEndDate: this.rangeEndDate,
        hasRangeSelection: this.hasRangeSelection
      })
      
      if (this.rangeStartDate && this.rangeEndDate) {
        console.log('开始加载数据...')
        this.loadData()
      } else {
        console.warn('范围选择不完整，无法加载数据')
        alert('请先选择开始和结束日期')
      }
    },

    async loadData() {
      this.loading = true
      try {
        // 根据时间模式设置时间范围
        let startTime, endTime

        if (this.timeMode === 'single') {
          // 单天模式：选择的那一天
          if (!this.selectedDate) {
            this.loading = false
            return
          }
          const date = new Date(this.selectedDate)
          date.setHours(0, 0, 0, 0)
          startTime = date.getTime()
          date.setHours(23, 59, 59, 999)
          endTime = date.getTime()
        } else {
          // 范围模式：选择的日期范围
          if (!this.rangeStartDate || !this.rangeEndDate) {
            console.warn('范围模式：缺少开始或结束日期', {
              rangeStartDate: this.rangeStartDate,
              rangeEndDate: this.rangeEndDate
            })
            this.loading = false
            return
          }
          const start = new Date(this.rangeStartDate)
          start.setHours(0, 0, 0, 0)
          startTime = start.getTime()
          
          const end = new Date(this.rangeEndDate)
          end.setHours(23, 59, 59, 999)
          endTime = end.getTime()
        }

        await this.updateConfig({
          timeRange: {
            start: startTime,
            end: endTime
          }
        })

        await Promise.all([
          this.loadPriceData(),
          this.loadSpreadData(),
          this.detectSignals()
        ])
        
        // 如果是单天模式，加载K线图数据（按小时聚合）
        if (this.timeMode === 'single') {
          await this.loadCandlestickOptions(startTime, endTime)
        } else {
          // 范围模式：清空K线图配置
          this.dexCandlestickOptions = null
          this.cexCandlestickOptions = null
        }
        
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
    },


    /**
     * 创建单个K线图配置（股票样式）
     * @param {Array} data - K线数据 [[time, open, close, low, high], ...]
     * @param {String} title - 图表标题
     * @param {Function} axisLabelFormatter - X轴标签格式化函数
     */
    createSingleCandlestickOptions(data, title, axisLabelFormatter) {
      if (!data || data.length === 0) {
        return {
          grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            top: '3%',
            containLabel: true
          },
          xAxis: {
            type: 'time',
            scale: true,
            boundaryGap: false
          },
          yAxis: {
            type: 'value',
            name: 'Price (USDT)'
          },
          series: []
        }
      }

      return {
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '3%',
          containLabel: true
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'cross' },
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e5e7eb',
          borderWidth: 1,
          textStyle: { color: '#111827' },
          formatter: (params) => {
            if (!params || params.length === 0) return ''
            
            const param = params[0]
            if (param.seriesType === 'candlestick' && param.data && param.data.length >= 5) {
              const date = new Date(param.data[0])
              const timeStr = date.toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
              })
              
              const open = param.data[1]
              const close = param.data[2]
              const low = param.data[3]
              const high = param.data[4]
              const change = close - open
              const changePct = ((change / open) * 100).toFixed(2)
              
              // 涨跌颜色
              const changeColor = change >= 0 ? '#ef4444' : '#10b981'
              const changeText = change >= 0 ? '↑' : '↓'
              
              let result = `<div style="font-weight: 600; margin-bottom: 8px;">${title}</div>`
              result += `<div style="color: #6b7280; margin-bottom: 4px;">时间: ${timeStr}</div>`
              result += `<div style="margin-top: 8px;">`
              result += `<div>开盘: <span style="font-weight: 600;">${open.toFixed(2)}</span> USDT</div>`
              result += `<div>收盘: <span style="font-weight: 600; color: ${changeColor};">${close.toFixed(2)}</span> USDT</div>`
              result += `<div>最高: <span style="font-weight: 600;">${high.toFixed(2)}</span> USDT</div>`
              result += `<div>最低: <span style="font-weight: 600;">${low.toFixed(2)}</span> USDT</div>`
              result += `<div style="margin-top: 4px; color: ${changeColor}; font-weight: 600;">${changeText} ${Math.abs(change).toFixed(2)} (${changePct}%)</div>`
              result += `</div>`
              return result
            }
            return ''
          }
        },
        xAxis: {
          type: 'time',
          scale: true,
          boundaryGap: false,
          axisLabel: {
            color: '#6b7280',
            formatter: axisLabelFormatter
          },
          axisLine: { lineStyle: { color: '#e5e7eb' } },
          splitLine: { show: false }
        },
        yAxis: {
          type: 'value',
          name: 'Price (USDT)',
          nameTextStyle: { color: '#6b7280' },
          axisLabel: {
            color: '#6b7280',
            formatter: (value) => value.toFixed(2)
          },
          splitLine: { 
            lineStyle: { 
              color: '#f3f4f6',
              type: 'dashed'
            } 
          },
          axisLine: { lineStyle: { color: '#e5e7eb' } }
        },
        series: [{
          name: title,
          type: 'candlestick',
          data: data,
          large: true,
          largeThreshold: 100,
          // 股票K线样式：涨红跌绿（中国习惯）
          itemStyle: {
            color: '#ef4444',      // 涨：红色（收盘 >= 开盘）
            color0: '#10b981',      // 跌：绿色（收盘 < 开盘）
            borderColor: '#ef4444', // 涨：红色边框
            borderColor0: '#10b981', // 跌：绿色边框
            borderWidth: 1
          },
          emphasis: {
            itemStyle: {
              borderWidth: 2,
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.3)'
            }
          }
        }]
      }
    },

    /**
     * 加载K线图配置（单天模式）- 异步方法
     * 生成两个独立的K线图配置（按小时聚合）
     */
    async loadCandlestickOptions(startTime, endTime) {
      try {
        console.log('开始加载K线图配置，时间范围:', {
          start: new Date(startTime).toISOString(),
          end: new Date(endTime).toISOString()
        })
        
        // 单天模式：使用priceData按小时聚合生成K线数据
        if (!this.priceData) {
          this.dexCandlestickOptions = null
          this.cexCandlestickOptions = null
          return
        }
        
        // 使用实时计算，按小时聚合
        const candlestickData = this.generateCandlestickData()
        console.log('生成的K线数据（按小时）:', {
          dexCount: candlestickData.dex?.length || 0,
          cexCount: candlestickData.cex?.length || 0,
          dexFirst3: candlestickData.dex?.slice(0, 3),
          cexFirst3: candlestickData.cex?.slice(0, 3)
        })

        // 计算时间范围（用于X轴格式化）
        const allCandles = [...(candlestickData.dex || []), ...(candlestickData.cex || [])]
        if (allCandles.length === 0) {
          this.dexCandlestickOptions = null
          this.cexCandlestickOptions = null
          return
        }

        // 单天模式：使用小时格式化器（HH:MM）
        const axisLabelFormatter = (value) => {
          const date = new Date(value)
          return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
        }

        // 为每个交易所创建独立的K线图配置
        if (this.showDex && candlestickData.dex && candlestickData.dex.length > 0) {
          this.dexCandlestickOptions = this.createSingleCandlestickOptions(
            candlestickData.dex,
            'Uniswap V3',
            axisLabelFormatter
          )
        } else {
          this.dexCandlestickOptions = null
        }

        if (this.showCex && candlestickData.cex && candlestickData.cex.length > 0) {
          this.cexCandlestickOptions = this.createSingleCandlestickOptions(
            candlestickData.cex,
            'Binance',
            axisLabelFormatter
          )
        } else {
          this.cexCandlestickOptions = null
        }

        console.log('K线图配置已更新:', {
          dexCount: candlestickData.dex?.length || 0,
          cexCount: candlestickData.cex?.length || 0,
          hasDexOptions: !!this.dexCandlestickOptions,
          hasCexOptions: !!this.cexCandlestickOptions
        })
        
        // 强制触发视图更新
        this.$forceUpdate()
      } catch (error) {
        console.error('加载K线图配置失败:', error)
        this.dexCandlestickOptions = null
        this.cexCandlestickOptions = null
      }
    },

    /**
     * 获取K线图配置（范围模式）- 同步版本（返回基础配置）
     */
    getCandlestickOptionsSync() {
      // 返回基础配置，数据通过异步加载
      return {
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '15%',
          containLabel: true
        },
        legend: {
          data: [
            ...(this.showDex ? ['Uniswap V3'] : []),
            ...(this.showCex ? ['Binance'] : [])
          ].filter(name => {
            // 在同步版本中，总是显示选中的legend，即使暂时没有数据
            // 因为数据可能还在加载中
            return true
          }),
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
            color: '#6b7280'
          },
          axisLine: { lineStyle: { color: '#e5e7eb' } },
          splitLine: { lineStyle: { color: '#f3f4f6', opacity: 0.5 } }
        },
        yAxis: {
          type: 'value',
          name: 'Price (USDT)',
          nameTextStyle: { color: '#6b7280' },
          // 移除固定范围
          axisLabel: {
            color: '#6b7280',
            formatter: (value) => value.toFixed(2)
          },
          splitLine: { lineStyle: { color: '#f3f4f6' } },
          axisLine: { lineStyle: { color: '#e5e7eb' } }
        },
        series: []
      }
    },

    /**
     * 生成K线图数据
     * 将原始数据按时间窗口聚合（1小时）
     */
    generateCandlestickData() {
      if (!this.priceData) {
        return { dex: [], cex: [] }
      }

      // 按1小时聚合数据
      const interval = 60 * 60 * 1000 // 1小时（毫秒）

      const dexCandles = this.aggregateToCandles(this.priceData.dex, interval)
      const cexCandles = this.aggregateToCandles(this.priceData.cex, interval)

      return {
        dex: dexCandles,
        cex: cexCandles
      }
    },

    /**
     * 将价格数据聚合为K线数据
     * @param {Array} priceData - 价格数据 [{t: timestamp, p: price}, ...]
     * @param {Number} interval - 时间间隔（毫秒）
     * @returns {Array} K线数据 [[timestamp, [open, close, low, high]], ...]
     */
    aggregateToCandles(priceData, interval) {
      if (!priceData || priceData.length === 0) return []

      // 按时间窗口分组
      const buckets = new Map()

      priceData.forEach(point => {
        const bucketTime = Math.floor(point.t / interval) * interval
        if (!buckets.has(bucketTime)) {
          buckets.set(bucketTime, [])
        }
        buckets.get(bucketTime).push(point.p)
      })

      // 转换为K线格式
      const candles = []
      buckets.forEach((prices, bucketTime) => {
        if (prices.length === 0) return

        const open = prices[0] // 开盘价：第一个价格
        const close = prices[prices.length - 1] // 收盘价：最后一个价格
        const high = Math.max(...prices) // 最高价
        const low = Math.min(...prices) // 最低价

        // ECharts K线格式：[时间, 开盘, 收盘, 最低, 最高]
        candles.push([bucketTime, open, close, low, high])
      })

      // 按时间排序
      candles.sort((a, b) => a[0] - b[0])

      return candles
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
.time-mode-select {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  background: $bg-secondary;
  padding: 4px;
  border-radius: 8px;
}

.btn-mode {
  flex: 1;
  padding: 8px 12px;
  font-size: 13px;
  font-weight: 500;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: $text-secondary;
  cursor: pointer;
  transition: all $transition-fast;

  &:hover {
    color: $color-primary;
  }

  &.active {
    background: white;
    color: $color-primary;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
}

// 嵌入的日历样式
.embedded-calendar {
  margin-bottom: 16px;
  padding: 12px;
  background: $bg-secondary;
  border-radius: 8px;
}

.calendar-month-header {
  text-align: center;
  margin-bottom: 12px;
  
  .month-title {
    font-size: 14px;
    font-weight: 600;
    color: $text-primary;
  }
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 8px;
}

.weekday {
  text-align: center;
  font-size: 11px;
  font-weight: 600;
  color: $text-tertiary;
  padding: 4px 0;
}

.calendar-days-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.calendar-day-cell {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 500;
  color: $text-primary;
  cursor: pointer;
  border-radius: 4px;
  transition: all $transition-fast;
  position: relative;
  min-height: 32px;

  &:hover:not(.disabled) {
    background: rgba(59, 130, 246, 0.1);
  }

  &.disabled {
    color: transparent;
    cursor: default;
  }

  &.selected {
    background: $color-primary;
    color: white;
    font-weight: 600;
  }

  &.in-range {
    background: rgba(59, 130, 246, 0.15);
    color: $text-primary;
  }

  &.range-start {
    background: $color-primary;
    color: white;
    font-weight: 600;
    border-top-left-radius: 4px;
    border-bottom-left-radius: 4px;
  }

  &.range-end {
    background: $color-primary;
    color: white;
    font-weight: 600;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
  }

  &.today {
    border: 2px solid $color-primary;
  }

  &.today:not(.selected) {
    background: rgba(59, 130, 246, 0.05);
  }
}

.btn-confirm-range {
  margin-left: 8px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 500;
  background: $color-primary;
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  transition: all $transition-fast;

  &:hover:not(:disabled) {
    background: darken($color-primary, 10%);
  }

  &:active:not(:disabled) {
    transform: scale(0.98);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
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


