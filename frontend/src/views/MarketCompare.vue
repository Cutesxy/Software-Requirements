<template>
  <div class="market-compare-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">市场对比 Market Compare</h1>
        <p class="page-desc">CEX-DEX深度对比与流动性分析</p>
      </div>
    </div>
    
    <div class="grid grid-2">
      <chart-card
        title="价差时间序列"
        :height="380"
        :options="spreadTimeSeriesOptions"
        :loading="loading"
      />
      
      <chart-card
        title="价差分布对比"
        :height="380"
        :options="spreadDistOptions"
        :loading="loading"
      />
    </div>
    
    <div class="grid grid-2" style="margin-top: 24px;">
      <chart-card
        title="成交量对比"
        :height="350"
        :options="volumeCompareOptions"
        :loading="loading"
      />
      
      <chart-card
        title="波动率对比"
        :height="350"
        :options="volatilityOptions"
        :loading="loading"
      />
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import ChartCard from '@/components/ChartCard.vue'

export default {
  name: 'MarketCompare',
  components: { ChartCard },
  
  data() {
    return {
      loading: false
    }
  },
  
  computed: {
    ...mapState(['priceData', 'spreadData']),
    
    spreadTimeSeriesOptions() {
      if (!this.spreadData) return {}
      
      const data = this.spreadData.map(d => [d.t, d.spread])
      
      return {
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'time', axisLabel: { color: '#9BA5B8' } },
        yAxis: { type: 'value', name: 'Spread (USDT)', axisLabel: { color: '#9BA5B8' } },
        series: [{
          type: 'line',
          data,
          symbol: 'none',
          lineStyle: { color: '#00C2FF', width: 2 }
        }]
      }
    },
    
    spreadDistOptions() {
      if (!this.spreadData) return {}
      
      const spreads = this.spreadData.map(d => d.spread)
      const bins = this.calculateHistogram(spreads, 30)
      
      return {
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'value', name: 'Spread', axisLabel: { color: '#9BA5B8' } },
        yAxis: { type: 'value', name: 'Count', axisLabel: { color: '#9BA5B8' } },
        series: [{
          type: 'bar',
          data: bins,
          itemStyle: { color: '#9A6BFF' }
        }]
      }
    },
    
    volumeCompareOptions() {
      if (!this.priceData) return {}
      
      const cexVol = this.priceData.cex.map(d => [d.t, d.v])
      const dexVol = this.priceData.dex.map(d => [d.t, d.v])
      
      return {
        legend: { data: ['CEX Volume', 'DEX Volume'], textStyle: { color: '#E6EAF2' } },
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'time', axisLabel: { color: '#9BA5B8' } },
        yAxis: { type: 'value', axisLabel: { color: '#9BA5B8' } },
        series: [
          { name: 'CEX Volume', type: 'bar', data: cexVol, itemStyle: { color: '#00C2FF' } },
          { name: 'DEX Volume', type: 'bar', data: dexVol, itemStyle: { color: '#9A6BFF' } }
        ]
      }
    },
    
    volatilityOptions() {
      return {
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: ['CEX', 'DEX'], axisLabel: { color: '#9BA5B8' } },
        yAxis: { type: 'value', name: 'Volatility (%)', axisLabel: { color: '#9BA5B8' } },
        series: [{
          type: 'bar',
          data: [2.1, 2.5],
          itemStyle: {
            color: (params) => params.dataIndex === 0 ? '#00C2FF' : '#9A6BFF'
          }
        }]
      }
    }
  },
  
  methods: {
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
    }
  }
}
</script>

<style lang="scss" scoped>
.market-compare-page {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

