<template>
  <div class="backtest-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">回测分析 Backtest & PnL</h1>
        <p class="page-desc">策略回测与收益分析</p>
      </div>
      <button class="btn btn-primary" @click="runBacktest">
        运行回测
      </button>
    </div>
    
    <div class="grid grid-4" style="margin-bottom: 24px;">
      <stat-card label="总交易次数" :value="results.totalTrades" type="number" :decimals="0" icon="📊" />
      <stat-card label="胜率" :value="results.winRate" type="percent" icon="🎯" />
      <stat-card label="总收益" :value="results.totalProfit" type="currency" unit="USDT" icon="💰" :value-color="'#19D3A2'" />
      <stat-card label="夏普比率" :value="results.sharpeRatio" type="number" :decimals="2" icon="📈" />
    </div>
    
    <chart-card
      title="权益曲线"
      :height="400"
      :options="equityCurveOptions"
      :loading="loading"
    />
  </div>
</template>

<script>
import ChartCard from '@/components/ChartCard.vue'
import StatCard from '@/components/StatCard.vue'
import { mapState } from 'vuex'
import axios from 'axios'

export default {
  name: 'Backtest',
  components: { ChartCard, StatCard },

  data() {
    return {
      loading: false,
      results: {
        totalTrades: 0,
        winRate: 0,
        totalProfit: 0,
        sharpeRatio: 0,
        equity: [],
        avgProfit: 0,
        maxDrawdown: 0,
        winningTrades: 0,
        signals: []
      }
    }
  },

  computed: {
    ...mapState(['config']),

    equityCurveOptions() {
      if (!this.results.equity || this.results.equity.length === 0) {
        return {
          title: { text: '暂无数据', left: 'center', top: 'center' },
          xAxis: { type: 'time', axisLabel: { color: '#9BA5B8' } },
          yAxis: { type: 'value', name: 'Equity (USDT)', axisLabel: { color: '#9BA5B8' } },
          series: []
        }
      }

      const data = this.results.equity.map(e => [e.time, e.equity])

      return {
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'time', axisLabel: { color: '#9BA5B8' } },
        yAxis: { type: 'value', name: 'Equity (USDT)', axisLabel: { color: '#9BA5B8' } },
        series: [{
          type: 'line',
          data,
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
        }]
      }
    }
  },
  
  methods: {
    async runBacktest() {
      this.loading = true
      
      try {
        // 从后端API获取回测数据
        const response = await axios.get('/api/app/getresult', {
          params: {
            type: 'backtest',
            zThreshold: this.config.detector.zScoreThreshold,
            tradeSize: this.config.detector.volumeMin,
            start: Math.floor(this.config.timeRange.start / 1000), // 转换为秒
            end: Math.floor(this.config.timeRange.end / 1000)       // 转换为秒
          }
        })
        
        // 直接使用后端返回的完整回测结果
        this.results = response.data
        
        // 确保所有必要字段都有值
        this.results = {
          totalTrades: this.results.totalTrades || 0,
          winRate: this.results.winRate || 0,
          totalProfit: this.results.totalProfit || 0,
          sharpeRatio: this.results.sharpeRatio || 0,
          equity: this.results.equity || [],
          avgProfit: this.results.avgProfit || 0,
          maxDrawdown: this.results.maxDrawdown || 0,
          winningTrades: this.results.winningTrades || 0,
          signals: this.results.signals || []
        }
        
        console.log('回测数据已从后端获取:', this.results)
        
      } catch (error) {
        console.error('获取回测数据失败:', error)
        // 出错时重置为默认值
        this.results = {
          totalTrades: 0,
          winRate: 0,
          totalProfit: 0,
          sharpeRatio: 0,
          equity: [],
          avgProfit: 0,
          maxDrawdown: 0,
          winningTrades: 0,
          signals: []
        }
        
        // 可以在这里添加用户提示
        this.$message?.error('回测数据获取失败，请检查后端服务')
      } finally {
        this.loading = false
      }
    }
  },
  
  created() {
    // 组件创建时自动运行回测
    this.runBacktest()
  }
}
</script>

<style lang="scss" scoped>
.backtest-page {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
