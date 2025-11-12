<template>
  <div class="chart-card">
    <div v-if="title" class="chart-header">
      <h3>{{ title }}</h3>
      <div class="header-actions">
        <slot name="actions"></slot>
        <button v-if="exportable" class="btn-icon-sm" @click="onExport" title="导出">
          ↓
        </button>
      </div>
    </div>
    
    <div class="chart-body" :style="{ height: height + 'px' }">
      <div ref="chart" class="chart-container" :style="{ height: '100%' }"></div>
      <div v-if="loading" class="chart-loading">
        <div class="spinner"></div>
        <span>加载中...</span>
      </div>
    </div>
    
    <div v-if="$slots.footer" class="chart-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  name: 'ChartCard',
  
  props: {
    title: {
      type: String,
      default: ''
    },
    height: {
      type: Number,
      default: 400
    },
    options: {
      type: Object,
      default: () => ({})
    },
    loading: {
      type: Boolean,
      default: false
    },
    exportable: {
      type: Boolean,
      default: true
    }
  },
  
  data() {
    return {
      chart: null
    }
  },
  
  watch: {
    options: {
      handler(newOptions) {
        if (this.chart && newOptions) {
          this.chart.setOption(newOptions, true)
        }
      },
      deep: true
    }
  },
  
  mounted() {
    this.initChart()
    window.addEventListener('resize', this.handleResize)
  },
  
  beforeDestroy() {
    if (this.chart) {
      this.chart.dispose()
      this.chart = null
    }
    window.removeEventListener('resize', this.handleResize)
  },
  
  methods: {
    initChart() {
      if (!this.$refs.chart) return
      
      this.chart = echarts.init(this.$refs.chart)
      
      if (this.options) {
        this.chart.setOption(this.getDefaultOptions())
        this.chart.setOption(this.options)
      }
      
      this.$emit('chart-ready', this.chart)
    },
    
    getDefaultOptions() {
      return {
        backgroundColor: 'transparent',
        textStyle: {
          color: '#111827'
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '10%',
          containLabel: true
        },
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e5e7eb',
          textStyle: {
            color: '#111827'
          }
        }
      }
    },
    
    handleResize() {
      if (this.chart) {
        this.chart.resize()
      }
    },
    
    onExport() {
      if (!this.chart) return
      
      const url = this.chart.getDataURL({
        type: 'png',
        pixelRatio: 2,
        backgroundColor: '#ffffff'
      })
      
      const link = document.createElement('a')
      link.download = `${this.title || 'chart'}_${Date.now()}.png`
      link.href = url
      link.click()
      
      this.$emit('export', url)
    }
  }
}
</script>

<style lang="scss" scoped>
.chart-card {
  position: relative;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  
  h3 {
    font-size: 16px;
    font-weight: 600;
    color: $text-primary;
    margin: 0;
  }
  
  .header-actions {
    display: flex;
    gap: 8px;
    align-items: center;
  }
}

.chart-body {
  position: relative;
}

.chart-container {
  width: 100%;
}

.chart-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  background: rgba($bg-card, 0.95);
  backdrop-filter: blur(4px);
  
  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid $border-color;
    border-top-color: $color-primary;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  span {
    color: $text-secondary;
    font-size: 14px;
  }
}

.btn-icon-sm {
  width: 28px;
  height: 28px;
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

.chart-footer {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid $border-color;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
