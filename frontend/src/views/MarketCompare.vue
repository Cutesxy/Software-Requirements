<template>
  <div class="algorithm-visualization-page">
    <!-- 顶部控制面板 -->
    <div class="control-panel">
      <div class="control-section">
        <h3>算法参数配置</h3>
        <div class="params-grid">
          <div class="param-item">
            <label>利润阈值 (USDT)</label>
            <input 
              v-model.number="algorithmParams.profitThreshold" 
              type="number" 
              step="0.1" 
              min="0"
              class="input"
            />
        </div>
          <div class="param-item">
            <label>Binance 手续费率 (%)</label>
            <input 
              v-model.number="algorithmParams.binanceFeePct" 
              type="number" 
              step="0.001" 
              min="0"
              max="1"
              class="input"
            />
      </div>
          <div class="param-item">
            <label>Uniswap 手续费率 (%)</label>
            <input 
              v-model.number="algorithmParams.uniswapFeePct" 
              type="number" 
              step="0.001" 
              min="0"
              max="1"
              class="input"
            />
        </div>
        </div>
      </div>

      <div class="control-section">
        <h3>执行控制</h3>
        <div class="control-buttons">
          <button 
            class="btn btn-primary" 
            @click="startAnalysis"
            :disabled="isRunning || isPaused"
          >
            ▶️ 开始分析
            </button>
          <button 
            class="btn btn-secondary" 
            @click="togglePause"
            :disabled="!isRunning && !isPaused"
          >
            {{ isPaused ? '▶️ 继续' : '⏸️ 暂停' }}
            </button>
          <button 
            class="btn btn-danger" 
            @click="resetAnalysis"
            :disabled="!isRunning && !isPaused && processedBuckets === 0"
          >
            🔄 重置
            </button>
          </div>
        <div class="progress-section">
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
              :style="{ width: progressPercentage + '%' }"
                  ></div>
                </div>
          <span class="progress-text">{{ progressPercentage.toFixed(1) }}%</span>
              </div>
                </div>
              </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <!-- 左侧：算法流程图 -->
      <aside class="algorithm-flow">
        <div class="card">
          <div class="card-header">
            <h3>算法执行流程</h3>
                </div>
          <div class="flow-diagram">
            <div 
              v-for="(step, index) in algorithmSteps" 
              :key="index"
              class="flow-step"
              :class="{ 
                'active': currentStep === index,
                'completed': currentStep > index,
                'pending': currentStep < index
              }"
            >
              <!-- 进度条连接线 -->
              <div 
                v-if="index < algorithmSteps.length - 1"
                class="progress-line"
                :class="{
                  'completed': currentStep > index,
                  'active': currentStep === index
                }"
                  ></div>
              
              <!-- 步骤节点 -->
              <div class="step-node">
                <div 
                  class="step-indicator"
                  :class="{
                    'active': currentStep === index,
                    'completed': currentStep > index,
                    'pending': currentStep < index
                  }"
                >
                  <span v-if="currentStep > index" class="check-icon">✓</span>
                  <span v-else class="step-number">{{ index + 1 }}</span>
              </div>
            </div>

              <!-- 步骤内容 -->
              <div class="step-content">
                <div class="step-title">{{ step.title }}</div>
                <div class="step-desc">{{ step.description }}</div>
                <div v-if="step.data" class="step-data">
                  <span class="data-icon">📊</span>
                  {{ step.data }}
          </div>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <!-- 中间：实时数据流可视化 -->
      <main class="data-visualization">
        <!-- 时间桶列表 -->
        <div class="card" ref="middleCard">
          <div class="card-header" ref="middleCardHeader">
            <h3>时间桶数据流</h3>
            <div class="header-actions">
              <span v-if="totalBuckets > 0" class="status-badge">
                已处理: {{ processedBuckets }} / {{ totalBuckets }}
              </span>
              <span v-else-if="isRunning" class="status-badge">
                正在读取数据...
              </span>
            </div>
            </div>
          <div 
            class="time-buckets-container"
            :style="{ maxHeight: containerMaxHeight + 'px' }"
          >
            <div v-if="timeBuckets.length === 0 && !isRunning" class="empty-state">
              <div class="empty-icon">📊</div>
              <div class="empty-text">点击"开始分析"查看算法执行过程</div>
          </div>
            <div 
              v-for="(bucket, index) in visibleTimeBuckets" 
              :key="bucket.timestamp"
              class="time-bucket-item"
              :class="{
                'processing': bucket.status === 'processing',
                'completed': bucket.status === 'completed',
                'pending': bucket.status === 'pending',
                'expanded': expandedBucketIndex === bucket.timestamp
              }"
              @click="toggleBucketDetail(bucket.timestamp)"
            >
              <div class="bucket-header">
                <div class="bucket-info">
                  <span class="bucket-time">{{ formatTime(bucket.timestamp) }}</span>
                  <span class="bucket-swaps">Swap数量: {{ bucket.swapCount }}</span>
                  <span class="bucket-spread">价差: {{ bucket.priceDiff.toFixed(2) }} USDT</span>
        </div>
                <div class="bucket-status">
                  <span class="status-icon">{{ getStatusIcon(bucket.status) }}</span>
                  <span v-if="bucket.status === 'completed' && bucket.hasSignal" class="signal-badge">✓ 信号</span>
            </div>
          </div>

              <!-- 展开的详细分析 -->
              <div v-if="expandedBucketIndex === bucket.timestamp && bucket.status === 'completed'" class="bucket-detail">
                <!-- 毛利润计算 -->
                <div class="calculation-section">
                  <h4>毛利润计算</h4>
                  <div class="formula-box">
                    <div class="formula">毛利润 = |价差| × Uniswap交易量</div>
                    <div class="formula-result">
                      = |{{ bucket.priceDiff.toFixed(2)}}| × {{ bucket.uniswapVolume.toFixed(4)}}
                      = <strong>{{ bucket.grossProfit.toFixed(2)}} USDT</strong>
              </div>
            </div>
          </div>

                <!-- Swap交易列表 -->
                <div class="calculation-section">
                  <h4>Swap交易详情 ({{ bucket.swaps.length }} 笔)</h4>
                  <div class="swaps-table">
                    <table>
                      <thead>
                        <tr>
                          <th>Swap ID</th>
                          <th>Amount0</th>
                          <th>Amount1</th>
                          <th>Price</th>
                          <th>Gas Used</th>
                          <th>Binance费用</th>
                          <th>Uniswap费用</th>
                          <th>Gas成本</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(swap, sIdx) in bucket.swaps" :key="sIdx">
                          <td>#{{ sIdx + 1 }}</td>
                          <td>{{ swap.amount0.toFixed(4) }}</td>
                          <td>{{ swap.amount1.toFixed(4) }}</td>
                          <td>{{ swap.price.toFixed(2) }}</td>
                          <td>{{ swap.gasUsed }}</td>
                          <td>{{ swap.binanceFee.toFixed(4) }}</td>
                          <td>{{ swap.uniswapFee.toFixed(4) }}</td>
                          <td>{{ swap.gasCost.toFixed(4) }}</td>
                        </tr>
                      </tbody>
                    </table>
          </div>
        </div>

                <!-- 成本累计图表 -->
                <div class="calculation-section">
                  <h4>成本累计</h4>
            <chart-card
              title=""
                    :height="250"
                    :options="getCostAccumulationChart(bucket)"
            />
          </div>

                <!-- 净利润计算 -->
                <div class="calculation-section">
                  <h4>净利润计算</h4>
                  <div class="profit-comparison">
                    <div class="profit-item">
                      <span class="profit-label">毛利润:</span>
                      <span class="profit-value positive">+{{ bucket.grossProfit.toFixed(2)}} USDT</span>
            </div>
                    <div class="profit-item">
                      <span class="profit-label">总成本:</span>
                      <span class="profit-value negative">-{{ bucket.totalCost.toFixed(2)}} USDT</span>
          </div>
                    <div class="profit-divider">─</div>
                    <div class="profit-item total">
                      <span class="profit-label">净利润:</span>
                      <span class="profit-value" :class="bucket.netProfit >= 0 ? 'positive' : 'negative'">
                        {{ bucket.netProfit >= 0 ? '+' : '' }}{{ bucket.netProfit.toFixed(2)}} USDT
                      </span>
            </div>
                    <div class="profit-item">
                      <span class="profit-label">阈值:</span>
                      <span class="profit-value">{{ algorithmParams.profitThreshold.toFixed(2)}} USDT</span>
          </div>
                    <div class="profit-judgment" :class="bucket.hasSignal ? 'signal-yes' : 'signal-no'">
                      {{ bucket.hasSignal ? '✓ 生成信号' : '✗ 不生成信号' }}
            </div>
          </div>
        </div>

                <!-- 置信度计算 -->
                <div v-if="bucket.hasSignal" class="calculation-section">
                  <h4>置信度计算</h4>
                  <div class="formula-box">
                    <div class="formula">置信度 = exp(-价格标准差 / 1000)</div>
                    <div class="formula-result">
                      = exp(-{{ bucket.priceStd.toFixed(2)}} / 1000)
                      = <strong>{{ bucket.confidence.toFixed(4)}}</strong>
            </div>
          </div>
                </div>
                </div>
                </div>
                </div>
              </div>
      </main>

      <!-- 右侧：统计面板 -->
      <aside class="statistics-panel" ref="statsPanel">
        <div class="card">
          <div class="card-header">
            <h3>实时统计</h3>
                </div>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-label">已处理时间桶</span>
              <span class="stat-value">{{ processedBuckets }}</span>
                </div>
            <div class="stat-item">
              <span class="stat-label">已处理 Swap</span>
              <span class="stat-value">{{ totalProcessedSwaps }}</span>
                </div>
            <div class="stat-item">
              <span class="stat-label">生成信号数</span>
              <span class="stat-value positive">{{ generatedSignals.length }}</span>
                </div>
            <div class="stat-item">
              <span class="stat-label">总毛利润</span>
              <span class="stat-value positive">+{{ totalGrossProfit.toFixed(2)}} USDT</span>
              </div>
            <div class="stat-item">
              <span class="stat-label">总成本</span>
              <span class="stat-value negative">-{{ totalCost.toFixed(2)}} USDT</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">总净利润</span>
              <span class="stat-value" :class="totalNetProfit >= 0 ? 'positive' : 'negative'">
                {{ totalNetProfit >= 0 ? '+' : '' }}{{ totalNetProfit.toFixed(2)}} USDT
              </span>
        </div>
      </div>
    </div>

        <!-- 成本分解饼图 -->
        <div class="card">
          <div class="card-header">
            <h3>成本分解</h3>
        </div>
          <chart-card
            title=""
            :height="250"
            :options="costBreakdownChart"
          />
            </div>

        <!-- 信号质量分布 -->
        <div class="card">
          <div class="card-header">
            <h3>信号质量分布</h3>
              </div>
          <chart-card
            title=""
            :height="300"
            :options="signalQualityChart"
          />
            </div>
      </aside>
          </div>

    <!-- 底部：信号输出区 -->
    <div class="signals-output">
      <div class="card">
        <div class="card-header">
          <h3>生成的信号 ({{ generatedSignals.length }})</h3>
          <div class="header-actions">
            <button class="btn btn-sm" @click="exportSignals">📥 导出</button>
            </div>
          </div>
        <data-table
          :columns="signalColumns"
          :data="generatedSignals"
          :max-height="300"
        >
          <template #col-direction="{ value }">
            <span class="badge" :class="value === 'buy' ? 'badge-primary' : 'badge-success'">
              {{ value === 'buy' ? '买入' : '卖出' }}
            </span>
          </template>
          <template #col-netProfit="{ value }">
            <span class="value-display" :class="value >= 0 ? 'positive' : 'negative'">
              {{ value >= 0 ? '+' : '' }}{{ value.toFixed(2) }}
            </span>
          </template>
        </data-table>
      </div>
    </div>
  </div>
</template>

<script>
import ChartCard from '@/components/ChartCard.vue'
import DataTable from '@/components/DataTable.vue'
import processedDataLoader from '@/utils/processedDataLoader'

export default {
  name: 'MarketCompare',
  
  components: {
    ChartCard,
    DataTable
  },

  data() {
    return {
      containerMaxHeight: 800, // 默认高度
      // 算法参数
      algorithmParams: {
        profitThreshold: 10.0,
        binanceFeePct: 0.001,
        uniswapFeePct: 0.003
      },
      
      // 执行状态
      isRunning: false,
      isPaused: false,
      currentStep: -1,
      processedBuckets: 0,
      totalBuckets: 0,
      expandedBucketIndex: -1,
      
      // 算法步骤
      algorithmSteps: [
        { title: '读取数据源', description: '从数据库读取 uniswap_swaps 和 merged_trading_data', data: null },
        { title: '遍历时间桶', description: '按时间顺序处理每个时间桶', data: null },
        { title: '计算毛利润', description: '毛利润 = |价差| × Uniswap交易量', data: null },
        { title: '遍历Swap交易', description: '处理时间桶内的所有Swap交易', data: null },
        { title: '累计计算成本', description: '累计Binance手续费、Uniswap手续费、Gas成本', data: null },
        { title: '计算净利润', description: '净利润 = 毛利润 - 总成本', data: null },
        { title: '判断生成信号', description: '净利润 > 阈值时生成套利信号', data: null }
      ],
      
      // 时间桶数据
      timeBuckets: [],
      
      // 生成的信号
      generatedSignals: [],
      
      // 表格列定义
      signalColumns: [
        { key: 'timestamp', label: '时间', type: 'time', width: '180px' },
        { key: 'direction', label: '方向', width: '100px' },
        { key: 'grossProfit', label: '毛利润', type: 'number', decimals: 2 },
        { key: 'totalCost', label: '总成本', type: 'number', decimals: 2 },
        { key: 'netProfit', label: '净利润', type: 'number', decimals: 2 },
        { key: 'confidence', label: '置信度', type: 'number', decimals: 4 }
      ]
    }
  },

  mounted() {
    this.updateMaxHeight()
    window.addEventListener('resize', this.updateMaxHeight)
    // 使用 ResizeObserver 监听右侧面板高度变化
    this.resizeObserver = new ResizeObserver(this.updateMaxHeight)
    if (this.$refs.statsPanel) {
      this.resizeObserver.observe(this.$refs.statsPanel)
    }
  },

  beforeDestroy() {
    window.removeEventListener('resize', this.updateMaxHeight)
    if (this.resizeObserver) {
      this.resizeObserver.disconnect()
    }
  },



  computed: {
    progressPercentage() {
      return this.totalBuckets > 0 ? (this.processedBuckets / this.totalBuckets) * 100 : 0
    },
    
    // 只显示已处理的时间桶（包括正在处理的）
    visibleTimeBuckets() {
      return this.timeBuckets.filter(b => 
        b.status === 'processing' || b.status === 'completed'
      )
    },
    
    totalProcessedSwaps() {
      return this.timeBuckets
        .filter(b => b.status === 'completed')
        .reduce((sum, b) => sum + b.swapCount, 0)
    },
    
    totalGrossProfit() {
      return this.generatedSignals.reduce((sum, s) => sum + s.grossProfit, 0)
    },
    
    totalCost() {
      return this.generatedSignals.reduce((sum, s) => sum + s.totalCost, 0)
    },
    
    totalNetProfit() {
      return this.generatedSignals.reduce((sum, s) => sum + s.netProfit, 0)
    },
    
    costBreakdownChart() {
      const binanceFee = this.generatedSignals.reduce((sum, s) => sum + s.binanceFee, 0)
      const uniswapFee = this.generatedSignals.reduce((sum, s) => sum + s.uniswapFee, 0)
      const gasCost = this.generatedSignals.reduce((sum, s) => sum + s.gasCost, 0)
      const total = binanceFee + uniswapFee + gasCost
      
      if (total === 0) {
        return { series: [] }
      }
      
      return {
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c} USDT ({d}%)'
        },
        legend: {
          bottom: '0%',
          left: 'center'
        },
        series: [{
            type: 'pie',
            radius: ['40%', '60%'],
            center: ['50%', '40%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false,
              position: 'center'
            },
            data: [
            { value: binanceFee.toFixed(2), name: 'Binance手续费' },
            { value: uniswapFee.toFixed(2), name: 'Uniswap手续费' },
            { value: gasCost.toFixed(2), name: 'Gas成本' }
          ],
          emphasis: {
            label: {
              show: true,
              fontSize: '16',
              fontWeight: 'bold'
            },
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      }
    },
    
    signalQualityChart() {
      if (this.generatedSignals.length === 0) {
        return { series: [] }
      }
      
      const profits = this.generatedSignals.map(s => s.netProfit)
      const confidences = this.generatedSignals.map(s => s.confidence)

      return {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'cross' }
        },
        grid: {
          left: '5%',
          right: '10%',
          bottom: '5%',
          containLabel: true
        },
        legend: {
          data: ['净利润分布', '置信度分布']
        },
        xAxis: {
          type: 'value',
          name: '数值',
          axisLabel: {
            rotate: 0,
            hideOverlap: true,
            formatter: function (value) {
              if (value >= 1000) {
                return (value / 1000).toFixed(0) + 'k';
              }
              return value;
            }
          }
        },
        yAxis: {
          type: 'value',
          name: '频次'
        },
        series: [
          {
            name: '净利润分布',
            type: 'bar',
            data: this.calculateHistogram(profits, 10)
          },
          {
            name: '置信度分布',
            type: 'line',
            data: this.calculateHistogram(confidences, 10)
          }
        ]
      }
    }
  },
  
  methods: {
    updateMaxHeight() {
      if (this.$refs.statsPanel && this.$refs.middleCard && this.$refs.middleCardHeader) {
        // 获取右侧面板的总高度
        const rightHeight = this.$refs.statsPanel.offsetHeight
        
        // 获取中间卡片的样式信息
        const cardStyle = window.getComputedStyle(this.$refs.middleCard)
        const cardPaddingY = parseFloat(cardStyle.paddingTop || 0) + parseFloat(cardStyle.paddingBottom || 0)
        const cardBorderY = parseFloat(cardStyle.borderTopWidth || 0) + parseFloat(cardStyle.borderBottomWidth || 0)
        
        // 获取头部的样式信息
        const headerHeight = this.$refs.middleCardHeader.offsetHeight
        const headerStyle = window.getComputedStyle(this.$refs.middleCardHeader)
        const headerMarginBottom = parseFloat(headerStyle.marginBottom || 0)
        
        // 计算容器高度：右侧高度 - 卡片内边距 - 卡片边框 - 头部高度 - 头部下边距
        // 减去 2px 的缓冲值以避免计算误差导致的滚动条
        this.containerMaxHeight = rightHeight - cardPaddingY - cardBorderY - headerHeight - headerMarginBottom - 2
      }
    },

    startAnalysis() {
      this.isRunning = true
      this.isPaused = false
      this.currentStep = 0
      this.processedBuckets = 0
      this.totalBuckets = 0
      this.timeBuckets = []
      this.generatedSignals = []
      this.expandedBucketIndex = -1

      console.log('开始分析算法...')

      // 开始执行（数据会在读取数据源步骤时生成）
      this.executeAnalysis()
    },
    
    togglePause() {
      this.isPaused = !this.isPaused
      if (!this.isPaused) {
        this.executeAnalysis()
      }
    },
    
    resetAnalysis() {
      this.isRunning = false
      this.isPaused = false
      this.currentStep = -1
      this.processedBuckets = 0
      this.totalBuckets = 0
      this.timeBuckets = []
      this.generatedSignals = []
      this.expandedBucketIndex = -1
      
      // 重置所有步骤数据
      this.algorithmSteps.forEach(step => {
        step.data = null
      })
    },
    
    async executeAnalysis() {
      if (!this.isRunning || this.isPaused) return
      
      // 步骤1: 读取数据源 - 加载9/1的真实数据
      this.currentStep = 0
      this.algorithmSteps[0].data = '正在读取数据...'
      await this.delay(800)
      
      try {
        // 加载processed_data.json
        const rawData = await processedDataLoader.loadData()
        
        // 9/1的时间范围：2025-09-01 00:00:00 到 23:59:59 UTC
        const startTime = new Date('2025-09-01T00:00:00Z').getTime() // 毫秒
        const endTime = new Date('2025-09-01T23:59:59Z').getTime() // 毫秒
        
        // 过滤9/1的数据
        const sept1Data = rawData.data.filter(item => {
          const timestamp = item[0] * 1000 // 转换为毫秒
          return timestamp >= startTime && timestamp <= endTime
        })
        
        this.algorithmSteps[0].data = `已读取 ${sept1Data.length} 条9/1数据`
        await this.delay(300)
        
        // 将数据按时间桶组织（每5分钟一个桶）
        const bucketSize = 5 * 60 * 1000 // 5分钟，单位毫秒
        const bucketsMap = new Map()
        
        sept1Data.forEach(item => {
          const timestamp = item[0] * 1000 // 转换为毫秒
          const bucketKey = Math.floor(timestamp / bucketSize) * bucketSize
          
          if (!bucketsMap.has(bucketKey)) {
            bucketsMap.set(bucketKey, [])
          }
          bucketsMap.get(bucketKey).push(item)
        })
        
        // 转换为时间桶数组，按时间排序
        const bucketDataSources = Array.from(bucketsMap.entries())
          .sort((a, b) => a[0] - b[0])
          .map(([bucketTime, items]) => {
            // 计算桶的统计数据
            const uData = items.map(item => item[1]) // Uniswap数据
            const bData = items.map(item => item[2]) // Binance数据
            const priceDiffs = items.map(item => item[3]) // 价差
            
            // 计算平均价差
            const avgPriceDiff = priceDiffs.reduce((sum, pd) => sum + pd, 0) / priceDiffs.length
            
            // 计算Uniswap总交易量
            const totalUniswapVolume = uData.reduce((sum, u) => sum + (u[1] || 0), 0) // ve: 成交量
            
            // 计算价格标准差（使用Uniswap价格）
            const prices = uData.map(u => u[3] || 0) // ap: 平均价格
            let priceStd = 0
            if (prices.length > 0) {
              const avgPrice = prices.reduce((sum, p) => sum + p, 0) / prices.length
              priceStd = Math.sqrt(
                prices.reduce((sum, p) => sum + Math.pow(p - avgPrice, 2), 0) / prices.length
              )
            }
            
            // 为每个数据点生成swap信息（模拟）
            const swaps = items.map((item, idx) => {
              const u = item[1]
              const b = item[2]
              const uniswapPrice = u[3] || 0 // ap: 平均价格
              const uniswapVolume = u[1] || 0 // ve: 成交量
              const binancePrice = b[3] || 0 // c: 收盘价
              
              // 计算手续费（基于交易量）
              const binanceFee = uniswapVolume * binancePrice * this.algorithmParams.binanceFeePct
              const uniswapFee = uniswapVolume * uniswapPrice * this.algorithmParams.uniswapFeePct
              
              // Gas成本估算（固定值，实际应该从数据中获取）
              const gasUsed = 150000 // 估算gas使用量
              const gasPrice = 30 // gwei
              const gasCost = (gasUsed * gasPrice * uniswapPrice) / 1e18
              
              return {
                amount0: uniswapVolume,
                amount1: uniswapVolume * uniswapPrice,
                price: uniswapPrice,
                gasUsed,
                gasPrice,
                binanceFee,
                uniswapFee,
                gasCost
              }
            })
            
            return {
              timestamp: bucketTime,
              swapCount: items.length,
              priceDiff: avgPriceDiff,
              uniswapVolume: totalUniswapVolume,
              status: 'pending',
              hasSignal: false,
              grossProfit: 0,
              totalCost: 0,
              netProfit: 0,
              priceStd: priceStd || 0,
              confidence: 0,
              swaps: swaps
            }
          })
        
        this.totalBuckets = bucketDataSources.length
        this.algorithmSteps[0].data = `已读取 ${this.totalBuckets} 个时间桶数据（9/1真实数据）`
        await this.delay(300)
        
        // 步骤2: 遍历时间桶
        this.currentStep = 1
        this.algorithmSteps[1].data = `开始处理 ${this.totalBuckets} 个时间桶`
        
        // 处理每个时间桶（一个个添加）
        for (let i = this.processedBuckets; i < this.totalBuckets; i++) {
          if (this.isPaused) break
          
          // 从数据源获取并添加到列表
          const bucket = bucketDataSources[i]
          this.timeBuckets.push(bucket)
          bucket.status = 'processing'
          
          // 更新步骤2的数据
          this.algorithmSteps[1].data = `处理中: ${i + 1} / ${this.totalBuckets}`
          await this.delay(200)
          
          // 步骤3: 计算毛利润
          this.currentStep = 2
          bucket.grossProfit = Math.abs(bucket.priceDiff) * bucket.uniswapVolume
          this.algorithmSteps[2].data = `时间桶 ${i + 1}: ${bucket.grossProfit.toFixed(2)} USDT`
          await this.delay(300)
          
          // 步骤4: 遍历Swap交易
          this.currentStep = 3
          this.algorithmSteps[3].data = `处理 ${bucket.swapCount} 笔Swap交易`
          await this.delay(300)
          
          // 步骤5: 累计计算成本
          this.currentStep = 4
          bucket.totalCost = bucket.swaps.reduce((sum, swap) => {
            return sum + swap.binanceFee + swap.uniswapFee + swap.gasCost
          }, 0)
          this.algorithmSteps[4].data = `总成本: ${bucket.totalCost.toFixed(2)} USDT`
          await this.delay(300)
          
          // 步骤6: 计算净利润
          this.currentStep = 5
          bucket.netProfit = bucket.grossProfit - bucket.totalCost
          this.algorithmSteps[5].data = `净利润: ${bucket.netProfit.toFixed(2)} USDT`
          await this.delay(300)
          
          // 步骤7: 判断生成信号
          this.currentStep = 6
          if (bucket.netProfit > this.algorithmParams.profitThreshold) {
            bucket.hasSignal = true
            bucket.confidence = Math.exp(-bucket.priceStd / 1000)
            
            const signal = {
              timestamp: bucket.timestamp,
              direction: bucket.priceDiff > 0 ? 'buy' : 'sell',
              grossProfit: bucket.grossProfit,
              binanceFee: bucket.swaps.reduce((sum, s) => sum + s.binanceFee, 0),
              uniswapFee: bucket.swaps.reduce((sum, s) => sum + s.uniswapFee, 0),
              gasCost: bucket.swaps.reduce((sum, s) => sum + s.gasCost, 0),
              totalCost: bucket.totalCost,
              netProfit: bucket.netProfit,
              confidence: bucket.confidence
            }
            
            this.generatedSignals.push(signal)
            this.algorithmSteps[6].data = `✓ 生成信号 #${this.generatedSignals.length}`
          } else {
            this.algorithmSteps[6].data = '✗ 不满足阈值条件'
          }
          
          bucket.status = 'completed'
          this.processedBuckets = i + 1
          
          await this.delay(500)
        }
        
        if (this.processedBuckets >= this.totalBuckets) {
          this.isRunning = false
          this.currentStep = -1
        }
      } catch (error) {
        console.error('加载数据失败:', error)
        this.algorithmSteps[0].data = '数据加载失败: ' + error.message
        this.isRunning = false
        this.currentStep = -1
        alert('数据加载失败: ' + error.message)
      }
    },
    
    toggleBucketDetail(timestamp) {
      if (this.expandedBucketIndex === timestamp) {
        this.expandedBucketIndex = -1
      } else {
        this.expandedBucketIndex = timestamp
      }
    },
    
    getCostAccumulationChart(bucket) {
      const data = []
      let binanceAcc = 0
      let uniswapAcc = 0
      let gasAcc = 0
      
      bucket.swaps.forEach((swap, idx) => {
        binanceAcc += swap.binanceFee
        uniswapAcc += swap.uniswapFee
        gasAcc += swap.gasCost
        
        data.push({
          swap: idx + 1,
          binance: binanceAcc,
          uniswap: uniswapAcc,
          gas: gasAcc,
          total: binanceAcc + uniswapAcc + gasAcc
        })
      })
      
      return {
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'cross' }
        },
        legend: {
          data: ['Binance手续费', 'Uniswap手续费', 'Gas成本', '总成本']
        },
        xAxis: {
          type: 'category',
          data: data.map(d => `Swap ${d.swap}`)
        },
        yAxis: {
          type: 'value',
          name: '累计成本 (USDT)'
        },
        series: [
          {
            name: 'Binance手续费',
            type: 'line',
            stack: 'cost',
            data: data.map(d => d.binance.toFixed(4))
          },
          {
            name: 'Uniswap手续费',
            type: 'line',
            stack: 'cost',
            data: data.map(d => d.uniswap.toFixed(4))
          },
          {
            name: 'Gas成本',
            type: 'line',
            stack: 'cost',
            data: data.map(d => d.gas.toFixed(4))
          },
          {
            name: '总成本',
            type: 'line',
            data: data.map(d => d.total.toFixed(4)),
            lineStyle: { width: 2 }
          }
        ]
      }
    },
    
    calculateHistogram(data, bins) {
      const min = Math.min(...data)
      const max = Math.max(...data)
      const binWidth = (max - min) / bins
      const histogram = new Array(bins).fill(0)
      
      data.forEach(value => {
        const binIndex = Math.min(Math.floor((value - min) / binWidth), bins - 1)
        histogram[binIndex]++
      })
      
      return histogram.map((count, i) => [min + i * binWidth, count])
    },
    
    formatTime(timestamp) {
      return new Date(timestamp).toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    },
    
    getStatusIcon(status) {
      switch (status) {
        case 'processing': return '⏳'
        case 'completed': return '✓'
        default: return '○'
      }
    },
    
    exportSignals() {
      if (this.generatedSignals.length === 0) return
      
      const csv = this.signalsToCSV()
      const blob = new Blob([csv], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `arbitrage_signals_${Date.now()}.csv`
      link.click()
      URL.revokeObjectURL(url)
    },

    signalsToCSV() {
      const header = '时间,方向,毛利润,总成本,净利润,置信度\n'
      const rows = this.generatedSignals.map(s => 
        `${new Date(s.timestamp).toISOString()},${s.direction},${s.grossProfit},${s.totalCost},${s.netProfit},${s.confidence}`
      ).join('\n')
      return header + rows
    },
    
    delay(ms) {
      return new Promise(resolve => setTimeout(resolve, ms))
    }
  }
}
</script>

<style lang="scss" scoped>
.algorithm-visualization-page {
  padding: 24px;
  background: $bg-primary;
  min-height: 100vh;
}

// 控制面板
.control-panel {
  background: $bg-card;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  border: 1px solid $border-color;

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
}

.control-section {
  h3 {
    font-size: 16px;
    font-weight: 600;
    color: $text-primary;
    margin: 0 0 16px 0;
  }
}

.params-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.param-item {
  label {
    display: block;
    font-size: 13px;
    color: $text-secondary;
    margin-bottom: 8px;
  }
}

.control-buttons {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.progress-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: $bg-primary;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, $color-primary, $color-success);
  transition: width 0.3s ease;
}

.progress-text {
    font-size: 14px;
    font-weight: 600;
    color: $text-primary;
  min-width: 60px;
}

// 主内容区域
.main-content {
  display: grid;
  grid-template-columns: 280px 1fr 320px;
  gap: 24px;
  margin-bottom: 24px;
  align-items: start; /* 关键：防止默认拉伸，让高度由内容决定 */

  @media (max-width: 1400px) {
    grid-template-columns: 250px 1fr 280px;
  }

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
}

// 算法流程图 - 进度条样式
.algorithm-flow {
  .flow-diagram {
    padding: 20px 0;
    position: relative;
  }
}

.flow-step {
  position: relative;
  display: flex;
  align-items: flex-start;
  margin-bottom: 0;
  padding-left: 20px;
  padding-right: 12px;
  padding-bottom: 24px;

  &:last-child {
    padding-bottom: 0;
  }

  &.active {
    .step-indicator {
      background: linear-gradient(135deg, $color-primary, lighten($color-primary, 10%));
      border-color: $color-primary;
      box-shadow: 0 0 0 4px rgba($color-primary, 0.2);
      animation: pulse-ring 2s ease-in-out infinite;
    }

    .step-title {
      color: $color-primary;
      font-weight: 700;
    }
  }

  &.completed {
    .step-indicator {
      background: linear-gradient(135deg, $color-success, lighten($color-success, 10%));
      border-color: $color-success;
    }

    .step-title {
    color: $text-primary;
  }
}

  &.pending {
    .step-indicator {
  background: $bg-primary;
      border-color: $border-color;
    }

    .step-title,
    .step-desc {
      color: $text-tertiary;
      opacity: 0.6;
    }
  }
}

// 进度条连接线
.progress-line {
  position: absolute;
  left: 29px;
  top: 40px;
  width: 2px;
  height: calc(100% - 20px);
  background: $border-color;
  transition: all 0.3s ease;
  z-index: 0;

  &.completed {
    background: linear-gradient(180deg, $color-success, lighten($color-success, 10%));
    box-shadow: 0 0 4px rgba($color-success, 0.3);
  }

  &.active {
    background: linear-gradient(180deg, $color-success, $color-primary);
    box-shadow: 0 0 6px rgba($color-primary, 0.4);
  }
}

// 步骤节点
.step-node {
  position: relative;
  z-index: 1;
  margin-right: 16px;
  flex-shrink: 0;
}

.step-indicator {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid;
  transition: all 0.3s ease;
  position: relative;

  .step-number {
    font-size: 16px;
    font-weight: 700;
    color: white;
  }

  .check-icon {
    font-size: 20px;
    color: white;
    font-weight: 700;
  }

  &.active {
    transform: scale(1.1);
  }

  &.completed {
    .step-number {
      display: none;
    }
  }

  &.pending {
    .step-number {
      color: $text-tertiary;
    }
  }
}

@keyframes pulse-ring {
  0% {
    box-shadow: 0 0 0 4px rgba($color-primary, 0.2);
  }
  50% {
    box-shadow: 0 0 0 8px rgba($color-primary, 0.1);
  }
  100% {
    box-shadow: 0 0 0 4px rgba($color-primary, 0.2);
  }
}

// 步骤内容
.step-content {
  flex: 1;
  padding-top: 4px;
}

.step-title {
  font-size: 14px;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 6px;
  transition: all 0.3s ease;
}

.step-desc {
  font-size: 12px;
  color: $text-secondary;
  line-height: 1.5;
  margin-bottom: 6px;
}

.step-data {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: $color-primary;
  margin-top: 8px;
  font-weight: 500;
  padding: 6px 10px;
  background: rgba($color-primary, 0.08);
  border-radius: 4px;
  border-left: 2px solid $color-primary;

  .data-icon {
    font-size: 12px;
  }
}

// 数据可视化
.data-visualization {
  .time-buckets-container {
    max-height: 800px;
    overflow-y: auto;
  }
}

.time-bucket-item {
  background: $bg-primary;
  border: 1px solid $border-color;
  border-radius: 8px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    border-color: $color-primary;
    box-shadow: $shadow-sm;
  }

  &.processing {
    border-color: $color-warning;
    background: rgba($color-warning, 0.05);
    animation: pulse 1.5s ease-in-out infinite;
  }

  &.completed {
    border-color: $color-success;
  }

  &.expanded {
    border-color: $color-primary;
    box-shadow: $shadow-md;
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.bucket-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
}

.bucket-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.bucket-time {
  font-size: 14px;
    font-weight: 600;
    color: $text-primary;
}

.bucket-swaps,
.bucket-spread {
  font-size: 12px;
  color: $text-secondary;
}

.bucket-status {
    display: flex;
    align-items: center;
  gap: 8px;
}

.status-icon {
  font-size: 20px;
}

.signal-badge {
  padding: 4px 8px;
  background: $color-success;
  color: white;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.bucket-detail {
  padding: 20px;
  border-top: 1px solid $border-color;
  background: $bg-card;
}

.calculation-section {
  margin-bottom: 24px;

  &:last-child {
    margin-bottom: 0;
  }

  h4 {
    font-size: 14px;
    font-weight: 600;
    color: $text-primary;
    margin: 0 0 12px 0;
  }
}

.formula-box {
  background: rgba($color-primary, 0.05);
  border-left: 3px solid $color-primary;
  padding: 12px 16px;
  border-radius: 4px;
}

.formula {
    font-size: 13px;
    color: $text-secondary;
    margin-bottom: 8px;
  font-family: 'Courier New', monospace;
  }

.formula-result {
  font-size: 14px;
    color: $text-primary;

  strong {
    color: $color-primary;
    font-size: 16px;
  }
}

.swaps-table {
  overflow-x: auto;
  max-height: 300px;
  overflow-y: auto;

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;

    th, td {
      padding: 8px;
      text-align: left;
      border-bottom: 1px solid $border-color;
    }

    th {
      background: $bg-primary;
      font-weight: 600;
      color: $text-primary;
      position: sticky;
      top: 0;
    }

    td {
      color: $text-secondary;
    }
  }
}

.profit-comparison {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: rgba($color-primary, 0.05);
  border-radius: 8px;
}

.profit-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;

  &.total {
    padding-top: 12px;
    border-top: 2px solid $border-color;
    font-weight: 600;
    font-size: 16px;
  }
}

.profit-label {
    color: $text-secondary;
}

.profit-value {
  font-weight: 600;

  &.positive {
    color: $color-success;
  }

  &.negative {
    color: $color-danger;
  }
}

.profit-divider {
  text-align: center;
  color: $border-color;
  font-size: 20px;
  margin: 4px 0;
}

.profit-judgment {
  padding: 8px 16px;
  border-radius: 6px;
  text-align: center;
  font-weight: 600;
  font-size: 14px;

  &.signal-yes {
    background: rgba($color-success, 0.1);
    color: $color-success;
  }

  &.signal-no {
    background: rgba($color-danger, 0.1);
    color: $color-danger;
  }
}

// 统计面板
.statistics-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: $bg-primary;
  border-radius: 6px;
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

  &.negative {
    color: $color-danger;
  }
}

// 信号输出区
.signals-output {
  margin-top: 24px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-badge {
  padding: 4px 12px;
  background: rgba($color-primary, 0.1);
    color: $color-primary;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}
</style>