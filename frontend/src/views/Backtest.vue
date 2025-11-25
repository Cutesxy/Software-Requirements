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
import mockData from '@/utils/mockData'

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
        equity: []
      }
    }
  },
  
  computed: {
    equityCurveOptions() {
      if (!this.results.equity || this.results.equity.length === 0) return {}
      
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
    runBacktest() {
      this.loading = true
      setTimeout(() => {
        this.results = mockData.generateBacktestResults({
          priceThreshold: 0.8,
          zScoreThreshold: 2.0,
          timeWindow: [1, 20],
          volumeMin: 1000,
          fees: { cex: 0.001, dex: 0.003, gas: 15, slippage: 0.002 }
        })
        this.loading = false
      }, 1000)
    }
  },
  
  created() {
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

