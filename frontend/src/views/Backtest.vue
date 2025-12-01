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
    ...mapState(['signals']),

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
        // 使用真实的信号数据进行回测分析
        if (this.signals && this.signals.length > 0) {
          this.results = this.calculateBacktestResults(this.signals)
        } else {
          console.warn('No signal data available for backtest')
          this.results = {
            totalTrades: 0,
            winningTrades: 0,
            winRate: 0,
            totalProfit: 0,
            avgProfit: 0,
            maxDrawdown: 0,
            sharpeRatio: 0,
            equity: [],
            signals: []
          }
        }
        this.loading = false
      }, 1000)
    },

    calculateBacktestResults(signals) {
      // 计算统计指标
      const totalTrades = signals.length
      const winningTrades = signals.filter(s => s.netProfit > 0).length
      const totalProfit = signals.reduce((sum, s) => sum + s.netProfit, 0)
      const avgProfit = totalProfit / totalTrades
      const winRate = winningTrades / totalTrades

      // 生成权益曲线
      const equity = []
      let cumProfit = 100000 // 初始资金
      signals.forEach(s => {
        cumProfit += s.netProfit
        equity.push({ time: s.time, equity: cumProfit })
      })

      // 计算最大回撤
      let maxDrawdown = 0
      let peak = equity[0]?.equity || 0
      equity.forEach(e => {
        if (e.equity > peak) peak = e.equity
        const drawdown = (peak - e.equity) / peak
        if (drawdown > maxDrawdown) maxDrawdown = drawdown
      })

      // 计算夏普比率（简化）
      const returns = []
      for (let i = 1; i < equity.length; i++) {
        const ret = (equity[i].equity - equity[i-1].equity) / equity[i-1].equity
        returns.push(ret)
      }
      const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length
      const stdReturn = Math.sqrt(
        returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length
      )
      const sharpeRatio = stdReturn > 0 ? (avgReturn / stdReturn) * Math.sqrt(252) : 0

      return {
        totalTrades,
        winningTrades,
        winRate,
        totalProfit,
        avgProfit,
        maxDrawdown,
        sharpeRatio,
        equity,
        signals
      }
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

