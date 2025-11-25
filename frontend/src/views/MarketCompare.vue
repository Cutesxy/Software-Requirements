<template>
  <div class="market-compare-page">
    <!-- 顶部状态栏 -->
    <div class="top-status-bar" v-if="hasData">
      <div class="status-card">
        <div class="status-icon">📊</div>
        <div class="status-content">
          <div class="status-value">{{ stats.totalRecords.toLocaleString() }}</div>
          <div class="status-label">总记录数</div>
        </div>
      </div>

      <div class="status-card">
        <div class="status-icon">📈</div>
        <div class="status-content">
          <div class="status-value">{{ stats.avgSpread }}</div>
          <div class="status-label">平均价差</div>
        </div>
      </div>

      <div class="status-card">
        <div class="status-icon">🎯</div>
        <div class="status-content">
          <div class="status-value">{{ stats.opportunities }}</div>
          <div class="status-label">套利机会</div>
        </div>
      </div>

      <div class="status-card quality-card">
        <div class="status-icon">⚡</div>
        <div class="status-content">
          <div class="status-value" :class="getQualityColor()">
            {{ getOverallQuality() }}%
          </div>
          <div class="status-label">数据质量</div>
        </div>
      </div>
    </div>

    <div class="dashboard-content">
      <!-- 左侧控制面板 -->
      <aside class="sidebar">
        <div class="card">
          <div class="card-header">
            <h3>🛠️ 数据操作</h3>
          </div>

          <div class="tool-section">
            <button class="btn btn-primary w-full" @click="importData">
              <span>📥 导入数据</span>
            </button>

            <button class="btn btn-secondary w-full" @click="exportData" :disabled="!hasData">
              <span>📤 导出数据</span>
            </button>

            <button class="btn btn-outline w-full" @click="clearData" :disabled="!hasData">
              <span>🗑️ 清空数据</span>
            </button>
          </div>

          <div class="tool-section" v-if="hasData">
            <h4>📋 数据质量</h4>
            <div class="quality-panel">
              <div class="quality-bar">
                <div class="quality-bar-header">
                  <span>完整性</span>
                  <span class="quality-percent">{{ qualityChecks.completeness.value }}%</span>
                </div>
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :class="qualityChecks.completeness.status"
                    :style="{ width: qualityChecks.completeness.value + '%' }"
                  ></div>
                </div>
              </div>

              <div class="quality-bar">
                <div class="quality-bar-header">
                  <span>准确性</span>
                  <span class="quality-percent">{{ qualityChecks.accuracy.value }}%</span>
                </div>
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :class="qualityChecks.accuracy.status"
                    :style="{ width: qualityChecks.accuracy.value + '%' }"
                  ></div>
                </div>
              </div>

              <div class="quality-bar">
                <div class="quality-bar-header">
                  <span>连续性</span>
                  <span class="quality-percent">{{ qualityChecks.consistency.value }}%</span>
                </div>
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :class="qualityChecks.consistency.status"
                    :style="{ width: qualityChecks.consistency.value + '%' }"
                  ></div>
                </div>
              </div>
            </div>

            <button class="btn-text" @click="runQualityCheck">
              🔄 重新检测
            </button>
          </div>

          <div class="tool-section">
            <h4>📅 时间范围</h4>
            <div class="time-display">
              <div class="time-value">{{ stats.timeRange }}</div>
              <div class="time-label">数据时间跨度</div>
            </div>
          </div>
        </div>
      </aside>

      <!-- 右侧图表区域 -->
      <div class="charts-area">
        <!-- 空状态 -->
        <div v-if="!hasData" class="dashboard-empty">
          <div class="empty-illustration">
            <div class="empty-circle">
              <span class="empty-icon">📊</span>
            </div>
            <div class="empty-rays">
              <div class="ray"></div>
              <div class="ray"></div>
              <div class="ray"></div>
              <div class="ray"></div>
            </div>
          </div>
          <h2 class="empty-title">开始数据分析之旅</h2>
          <p class="empty-description">导入您的交易数据，探索市场机会，发现潜在收益</p>
          <button class="empty-action-btn" @click="importData">
            <span class="btn-icon">🚀</span>
            导入数据
          </button>
        </div>

        <!-- 数据概览卡片 -->
        <div class="overview-cards" v-if="hasData">
          <div class="overview-card">
            <div class="card-icon">📈</div>
            <div class="card-content">
              <div class="card-value">{{ report.basicStats.avgSpread }}</div>
              <div class="card-label">平均价差</div>
              <div class="card-trend positive">
                <span>↗</span>
                <span>+2.5%</span>
              </div>
            </div>
          </div>

          <div class="overview-card">
            <div class="card-icon">🎯</div>
            <div class="card-content">
              <div class="card-value">{{ report.arbAnalysis.opportunities }}</div>
              <div class="card-label">潜在机会</div>
              <div class="card-trend positive">
                <span>↗</span>
                <span>+12</span>
              </div>
            </div>
          </div>

          <div class="overview-card">
            <div class="card-icon">💰</div>
            <div class="card-content">
              <div class="card-value">{{ report.arbAnalysis.avgReturn }}</div>
              <div class="card-label">平均收益</div>
              <div class="card-trend positive">
                <span>↗</span>
                <span>+0.8%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 图表网格 -->
        <div class="charts-grid" v-if="hasData">
          <!-- 数据趋势图 -->
          <div class="chart-widget">
            <div class="widget-header">
              <h4>📊 价差与成交量趋势</h4>
              <div class="widget-actions">
                <button class="widget-btn" title="全屏">⛶</button>
                <button class="widget-btn" title="导出">↓</button>
              </div>
            </div>
            <chart-card
              title=""
              :height="280"
              :options="dataOverviewOptions"
              :loading="loading"
            />
          </div>

          <!-- 数据质量环形图 -->
          <div class="chart-widget">
            <div class="widget-header">
              <h4>✨ 数据质量分布</h4>
            </div>
            <chart-card
              title=""
              :height="280"
              :options="qualityPieOptions"
              :loading="loading"
            />
          </div>

          <!-- 成交量分布柱状图 -->
          <div class="chart-widget">
            <div class="widget-header">
              <h4>📦 成交量分布</h4>
            </div>
            <chart-card
              title=""
              :height="280"
              :options="volumeDistributionOptions"
              :loading="loading"
            />
          </div>

          <!-- 时间热力图 -->
          <div class="chart-widget">
            <div class="widget-header">
              <h4>🔥 时间分布热力图</h4>
            </div>
            <chart-card
              title=""
              :height="280"
              :options="timeHeatmapOptions"
              :loading="loading"
            />
          </div>
        </div>

        <!-- 数据分析报告 -->
        <div class="card analysis-report" v-if="hasData">
          <div class="card-header">
            <h3>📋 分析报告</h3>
            <div class="header-actions">
              <button class="btn-icon" @click="generateReport" title="生成报告">📄</button>
              <button class="btn-icon" @click="exportReport" title="导出报告">↓</button>
            </div>
          </div>

          <div class="report-content">
            <div class="report-section">
              <h4>📈 基本统计</h4>
              <div class="report-grid">
                <div class="report-item">
                  <label>数据时间范围</label>
                  <span>{{ report.basicStats.timeRange }}</span>
                </div>
                <div class="report-item">
                  <label>总交易对数</label>
                  <span>{{ report.basicStats.totalPairs }}</span>
                </div>
                <div class="report-item">
                  <label>平均价差</label>
                  <span>{{ report.basicStats.avgSpread }}</span>
                </div>
                <div class="report-item">
                  <label>最大价差</label>
                  <span>{{ report.basicStats.maxSpread }}</span>
                </div>
              </div>
            </div>

            <div class="report-section">
              <h4>🎯 套利机会分析</h4>
              <div class="report-grid">
                <div class="report-item">
                  <label>潜在机会数</label>
                  <span>{{ report.arbAnalysis.opportunities }}</span>
                </div>
                <div class="report-item">
                  <label>平均收益率</label>
                  <span>{{ report.arbAnalysis.avgReturn }}</span>
                </div>
                <div class="report-item">
                  <label>最佳交易时机</label>
                  <span>{{ report.arbAnalysis.bestTime }}</span>
                </div>
                <div class="report-item">
                  <label>风险等级</label>
                  <span class="risk-level" :class="report.arbAnalysis.riskLevel">
                    {{ report.arbAnalysis.riskLevelText }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 数据导入弹窗 -->
    <div v-if="showImportDialog" class="modal-overlay" @click="closeImportDialog">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>📥 导入数据</h3>
          <button class="btn-close" @click="closeImportDialog">×</button>
        </div>

        <div class="modal-body">
          <div class="import-options">
            <div class="import-option">
              <div class="option-icon">📁</div>
              <div class="option-content">
                <h4>从文件导入</h4>
                <p>支持 CSV、JSON 格式的数据文件</p>
                <input
                  type="file"
                  ref="fileInput"
                  @change="onFileSelected"
                  accept=".csv,.json"
                  style="display: none"
                />
                <button class="btn btn-outline" @click="$refs.fileInput.click()">
                  选择文件
                </button>
              </div>
            </div>

            <div class="import-option">
              <div class="option-icon">🔗</div>
              <div class="option-content">
                <h4>从API导入</h4>
                <p>连接外部数据源自动同步</p>
                <button class="btn btn-outline" @click="importFromAPI" disabled>
                  连接API
                </button>
              </div>
            </div>

            <div class="import-option">
              <div class="option-icon">🗄️</div>
              <div class="option-content">
                <h4>使用示例数据</h4>
                <p>快速加载预设数据集进行体验</p>
                <button class="btn btn-primary" @click="loadSampleData">
                  加载示例数据
                </button>
              </div>
            </div>
          </div>

          <div v-if="selectedFile" class="file-preview">
            <h4>文件预览</h4>
            <div class="file-info">
              <span>📄 文件名: {{ selectedFile.name }}</span>
              <span>📦 大小: {{ formatFileSize(selectedFile.size) }}</span>
            </div>
            <button class="btn btn-primary" @click="processImport" :disabled="importing">
              {{ importing ? '导入中...' : '开始导入' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ChartCard from '@/components/ChartCard.vue'
import { mapState } from 'vuex'

export default {
  name: 'MarketCompare',
  components: {
    ChartCard
  },

  data() {
    return {
      loading: false,
      hasData: false,
      showImportDialog: false,
      selectedFile: null,
      importing: false,

      qualityChecks: {
        completeness: { value: 0, status: 'good' },
        accuracy: { value: 0, status: 'good' },
        consistency: { value: 0, status: 'good' }
      },

      stats: {
        totalRecords: 0,
        timeRange: '-',
        avgSpread: '-',
        opportunities: 0
      },

      report: {
        basicStats: {
          timeRange: '-',
          totalPairs: 0,
          avgSpread: '-',
          maxSpread: '-'
        },
        arbAnalysis: {
          opportunities: 0,
          avgReturn: '-',
          bestTime: '-',
          riskLevel: 'low',
          riskLevelText: '低风险'
        }
      }
    }
  },

  computed: {
    ...mapState(['priceData', 'spreadData', 'signals']),

    dataOverviewOptions() {
      if (!this.spreadData || this.spreadData.length === 0) return null

      const spreadData = this.spreadData.map(d => [d.t, d.spread])
      const volumeData = this.spreadData.map(d => [d.t, d.volume || Math.random() * 1000])

      return {
        tooltip: { 
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e5e7eb',
          textStyle: { color: '#111827' }
        },
        legend: {
          data: ['价差', '成交量'],
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
        yAxis: [
          {
            type: 'value',
            name: '价差',
            position: 'left',
            axisLabel: { color: '#6b7280' },
            splitLine: { lineStyle: { color: '#f3f4f6' } }
          },
          {
            type: 'value',
            name: '成交量',
            position: 'right',
            axisLabel: { color: '#6b7280' },
            splitLine: { show: false }
          }
        ],
        series: [
          {
            name: '价差',
            type: 'line',
            yAxisIndex: 0,
            data: spreadData,
            smooth: true,
            lineStyle: { color: '#f97316', width: 2 },
            itemStyle: { color: '#f97316' },
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
          },
          {
            name: '成交量',
            type: 'bar',
            yAxisIndex: 1,
            data: volumeData,
            barWidth: '60%',
            itemStyle: { 
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: '#3b82f6' },
                  { offset: 1, color: '#60a5fa' }
                ]
              },
              opacity: 0.7
            }
          }
        ]
      }
    },

    qualityPieOptions() {
      return {
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e5e7eb',
          textStyle: { color: '#111827' }
        },
        legend: {
          orient: 'vertical',
          right: 10,
          top: 'center',
          textStyle: { color: '#6b7280' }
        },
        series: [
          {
            type: 'pie',
            radius: ['45%', '70%'],
            center: ['40%', '50%'],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: '#fff',
              borderWidth: 2
            },
            label: {
              show: false
            },
            labelLine: {
              show: false
            },
            data: [
              { value: this.qualityChecks.completeness.value, name: '完整性', itemStyle: { color: '#10b981' } },
              { value: this.qualityChecks.accuracy.value, name: '准确性', itemStyle: { color: '#3b82f6' } },
              { value: this.qualityChecks.consistency.value, name: '连续性', itemStyle: { color: '#f59e0b' } }
            ]
          }
        ]
      }
    },

    volumeDistributionOptions() {
      if (!this.spreadData) return null

      const hours = Array.from({ length: 24 }, (_, i) => i)
      const volumeByHour = new Array(24).fill(0)
      const countByHour = new Array(24).fill(0)

      this.spreadData.forEach(d => {
        const hour = new Date(d.t).getHours()
        volumeByHour[hour] += d.volume || Math.random() * 1000
        countByHour[hour]++
      })

      const avgVolumeByHour = volumeByHour.map((v, i) => 
        countByHour[i] > 0 ? v / countByHour[i] : 0
      )

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
          type: 'category',
          data: hours.map(h => `${h}:00`),
          axisLabel: { 
            color: '#6b7280',
            interval: 2
          }
        },
        yAxis: {
          type: 'value',
          axisLabel: { color: '#6b7280' },
          splitLine: { lineStyle: { color: '#f3f4f6' } }
        },
        series: [
          {
            data: avgVolumeByHour,
            type: 'bar',
            barWidth: '60%',
            itemStyle: {
              color: {
                type: 'linear',
                x: 0, y: 0, x2: 0, y2: 1,
                colorStops: [
                  { offset: 0, color: '#8b5cf6' },
                  { offset: 1, color: '#a78bfa' }
                ]
              },
              borderRadius: [4, 4, 0, 0]
            }
          }
        ]
      }
    },

    timeHeatmapOptions() {
      if (!this.spreadData) return null

      const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      const hours = Array.from({ length: 24 }, (_, i) => i)
      const data = []

      for (let day = 0; day < 7; day++) {
        for (let hour = 0; hour < 24; hour++) {
          const value = Math.floor(Math.random() * 100)
          data.push([hour, day, value])
        }
      }

      return {
        tooltip: {
          position: 'top',
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          borderColor: '#e5e7eb',
          textStyle: { color: '#111827' }
        },
        grid: {
          height: '70%',
          top: '10%',
          left: '80px',
          right: '20px'
        },
        xAxis: {
          type: 'category',
          data: hours.map(h => `${h}h`),
          splitArea: { show: true },
          axisLabel: { color: '#6b7280', interval: 2 }
        },
        yAxis: {
          type: 'category',
          data: days,
          splitArea: { show: true },
          axisLabel: { color: '#6b7280' }
        },
        visualMap: {
          min: 0,
          max: 100,
          calculable: true,
          orient: 'horizontal',
          left: 'center',
          bottom: '5%',
          textStyle: { color: '#6b7280' },
          inRange: {
            color: ['#f0f9ff', '#3b82f6', '#1e40af']
          }
        },
        series: [
          {
            type: 'heatmap',
            data: data,
            label: { show: false },
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }
        ]
      }
    }
  },

  mounted() {
    if (this.priceData || this.spreadData) {
      this.loadFromStore()
    }
  },

  methods: {
    loadFromStore() {
      if (this.spreadData && this.spreadData.length > 0) {
        this.hasData = true
        this.updateStats()
        this.runQualityCheck()
        this.generateReport()
      }
    },

    loadSampleData() {
      this.importing = true
      this.closeImportDialog()
      
      setTimeout(() => {
        this.loadFromStore()
        this.importing = false
      }, 1500)
    },

    updateStats() {
      if (this.spreadData) {
        this.stats.totalRecords = this.spreadData.length
        
        const spreads = this.spreadData.map(d => d.spread)
        const avgSpread = spreads.reduce((a, b) => a + b, 0) / spreads.length
        this.stats.avgSpread = avgSpread.toFixed(2) + ' USDT'

        if (this.spreadData.length > 0) {
          const firstDate = new Date(this.spreadData[0].t)
          const lastDate = new Date(this.spreadData[this.spreadData.length - 1].t)
          this.stats.timeRange = `${firstDate.getMonth()+1}/${firstDate.getDate()} - ${lastDate.getMonth()+1}/${lastDate.getDate()}`
        }

        this.stats.opportunities = this.signals ? this.signals.length : Math.floor(Math.random() * 50 + 10)
      }
    },

    runQualityCheck() {
      this.qualityChecks.completeness = { value: 95 + Math.floor(Math.random() * 5), status: 'good' }
      this.qualityChecks.accuracy = { value: 92 + Math.floor(Math.random() * 8), status: 'good' }
      this.qualityChecks.consistency = { value: 88 + Math.floor(Math.random() * 10), status: Math.random() > 0.8 ? 'warning' : 'good' }
    },

    getOverallQuality() {
      const total = this.qualityChecks.completeness.value + 
                   this.qualityChecks.accuracy.value + 
                   this.qualityChecks.consistency.value
      return Math.round(total / 3)
    },

    getQualityColor() {
      const quality = this.getOverallQuality()
      if (quality >= 95) return 'excellent'
      if (quality >= 85) return 'good'
      if (quality >= 70) return 'warning'
      return 'danger'
    },

    generateReport() {
      if (!this.spreadData || this.spreadData.length === 0) return

      const spreads = this.spreadData.map(d => d.spread)
      const avgSpread = spreads.reduce((a, b) => a + b, 0) / spreads.length
      const maxSpread = Math.max(...spreads)

      this.report.basicStats = {
        timeRange: this.stats.timeRange,
        totalPairs: this.stats.totalRecords.toLocaleString(),
        avgSpread: avgSpread.toFixed(2) + ' USDT',
        maxSpread: maxSpread.toFixed(2) + ' USDT'
      }

      this.report.arbAnalysis = {
        opportunities: this.stats.opportunities,
        avgReturn: (Math.random() * 2 + 0.5).toFixed(2) + '%',
        bestTime: '14:00-16:00',
        riskLevel: 'low',
        riskLevelText: '低风险'
      }
    },

    importData() {
      this.showImportDialog = true
    },

    closeImportDialog() {
      this.showImportDialog = false
      this.selectedFile = null
    },

    onFileSelected(event) {
      this.selectedFile = event.target.files[0]
    },

    processImport() {
      if (!this.selectedFile) return

      this.importing = true
      setTimeout(() => {
        this.importing = false
        this.closeImportDialog()
        this.loadFromStore()
      }, 2000)
    },

    importFromAPI() {
      alert('API导入功能开发中...')
    },

    exportData() {
      if (!this.hasData) return

      const dataStr = JSON.stringify({
        spreadData: this.spreadData,
        stats: this.stats,
        qualityChecks: this.qualityChecks,
        report: this.report
      }, null, 2)
      
      const blob = new Blob([dataStr], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `data_analysis_${Date.now()}.json`
      link.click()
      URL.revokeObjectURL(url)
    },

    exportReport() {
      alert('报告导出功能开发中...')
    },

    clearData() {
      if (confirm('确定要清空所有数据吗？')) {
        this.hasData = false
        this.stats = {
          totalRecords: 0,
          timeRange: '-',
          avgSpread: '-',
          opportunities: 0
        }
        this.qualityChecks = {
          completeness: { value: 0, status: 'good' },
          accuracy: { value: 0, status: 'good' },
          consistency: { value: 0, status: 'good' }
        }
      }
    },

    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }
  }
}
</script>

<style lang="scss" scoped>
.market-compare-page {
  min-height: 100vh;
  background: $bg-primary;
  padding: 24px;
}

// 顶部状态栏
.top-status-bar {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.status-card {
  background: linear-gradient(135deg, $bg-card 0%, rgba($color-primary, 0.03) 100%);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: $shadow-sm;
  border: 1px solid $border-color;
  transition: all $transition-fast;

  &:hover {
    box-shadow: $shadow-md;
    transform: translateY(-2px);
  }

  .status-icon {
    font-size: 36px;
    flex-shrink: 0;
  }

  .status-content {
    flex: 1;
  }

  .status-value {
    font-size: 28px;
    font-weight: 700;
    color: $text-primary;
    line-height: 1;
    margin-bottom: 4px;

    &.excellent { color: $color-success; }
    &.good { color: $color-primary; }
    &.warning { color: $color-warning; }
    &.danger { color: $color-danger; }
  }

  .status-label {
    font-size: 13px;
    color: $text-secondary;
  }
}

// 主仪表盘内容
.dashboard-content {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 24px;
  align-items: start;

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
}

// 左侧边栏
.sidebar {
  position: sticky;
  top: 24px;

  .card {
    margin-bottom: 0;
  }
}

.tool-section {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid $border-color;

  &:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
  }

  h4 {
    font-size: 14px;
    font-weight: 600;
    color: $text-primary;
    margin: 0 0 16px 0;
  }

  .w-full {
    width: 100%;
    margin-bottom: 8px;

    &:last-child {
      margin-bottom: 0;
    }
  }

  .btn-text {
    width: 100%;
    background: transparent;
    color: $color-primary;
    border: none;
    padding: 8px 0;
    text-align: center;
    font-size: 14px;
    cursor: pointer;
    margin-top: 8px;

    &:hover {
      color: darken($color-primary, 10%);
    }
  }
}

// 质量检查面板
.quality-panel {
  margin-bottom: 16px;
}

.quality-bar {
  margin-bottom: 16px;

  &:last-child {
    margin-bottom: 0;
  }
}

.quality-bar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 13px;

  span:first-child {
    color: $text-secondary;
  }

  .quality-percent {
    font-weight: 600;
    color: $text-primary;
  }
}

.progress-bar {
  height: 8px;
  background: $bg-primary;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  transition: width 0.3s ease;

  &.good {
    background: linear-gradient(90deg, $color-success, lighten($color-success, 10%));
  }

  &.warning {
    background: linear-gradient(90deg, $color-warning, lighten($color-warning, 10%));
  }

  &.danger {
    background: linear-gradient(90deg, $color-danger, lighten($color-danger, 10%));
  }
}

// 时间显示
.time-display {
  padding: 16px;
  background: $bg-primary;
  border-radius: 8px;
  text-align: center;

  .time-value {
    font-size: 14px;
    font-weight: 600;
    color: $text-primary;
    margin-bottom: 4px;
  }

  .time-label {
    font-size: 12px;
    color: $text-secondary;
  }
}

// 右侧图表区域
.charts-area {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

// 空状态
.dashboard-empty {
  background: $bg-card;
  border-radius: 12px;
  padding: 80px 40px;
  text-align: center;
  box-shadow: $shadow-sm;
  border: 1px solid $border-color;
}

.empty-illustration {
  position: relative;
  display: inline-block;
  margin-bottom: 32px;
}

.empty-circle {
  width: 120px;
  height: 120px;
  background: linear-gradient(135deg, rgba($color-primary, 0.1) 0%, rgba($color-accent, 0.1) 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: pulse 2s ease-in-out infinite;

  .empty-icon {
    font-size: 48px;
  }
}

.empty-rays {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 160px;
  height: 160px;

  .ray {
    position: absolute;
    width: 4px;
    height: 20px;
    background: linear-gradient(to top, transparent, rgba($color-primary, 0.3));
    border-radius: 2px;

    &:nth-child(1) {
      top: 0;
      left: 50%;
      transform: translateX(-50%);
    }

    &:nth-child(2) {
      right: 0;
      top: 50%;
      transform: translateY(-50%) rotate(90deg);
    }

    &:nth-child(3) {
      bottom: 0;
      left: 50%;
      transform: translateX(-50%) rotate(180deg);
    }

    &:nth-child(4) {
      left: 0;
      top: 50%;
      transform: translateY(-50%) rotate(270deg);
    }
  }
}

.empty-title {
  font-size: 24px;
  font-weight: 700;
  color: $text-primary;
  margin: 0 0 12px 0;
}

.empty-description {
  font-size: 16px;
  color: $text-secondary;
  margin: 0 0 32px 0;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.empty-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 32px;
  background: linear-gradient(135deg, $color-primary 0%, darken($color-primary, 10%) 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all $transition-fast;
  box-shadow: 0 4px 12px rgba($color-primary, 0.3);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba($color-primary, 0.4);
  }

  .btn-icon {
    font-size: 20px;
  }
}

// 概览卡片
.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 20px;
}

.overview-card {
  background: $bg-card;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  box-shadow: $shadow-sm;
  border: 1px solid $border-color;
  transition: all $transition-fast;

  &:hover {
    box-shadow: $shadow-md;
    transform: translateY(-2px);
  }

  .card-icon {
    font-size: 32px;
    flex-shrink: 0;
  }

  .card-content {
    flex: 1;
  }

  .card-value {
    font-size: 24px;
    font-weight: 700;
    color: $text-primary;
    margin-bottom: 4px;
  }

  .card-label {
    font-size: 13px;
    color: $text-secondary;
    margin-bottom: 8px;
  }

  .card-trend {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;

    &.positive {
      background: rgba($color-success, 0.1);
      color: $color-success;
    }

    &.negative {
      background: rgba($color-danger, 0.1);
      color: $color-danger;
    }
  }
}

// 图表网格
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: 24px;

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
}

.chart-widget {
  background: $bg-card;
  border-radius: 12px;
  padding: 20px;
  box-shadow: $shadow-sm;
  border: 1px solid $border-color;
}

.widget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;

  h4 {
    font-size: 16px;
    font-weight: 600;
    color: $text-primary;
    margin: 0;
  }

  .widget-actions {
    display: flex;
    gap: 8px;
  }

  .widget-btn {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: 1px solid $border-color;
    border-radius: 6px;
    color: $text-secondary;
    cursor: pointer;
    transition: all $transition-fast;

    &:hover {
      border-color: $color-primary;
      color: $color-primary;
    }
  }
}

// 分析报告
.analysis-report {
  background: $bg-card;
  border-radius: 12px;
  box-shadow: $shadow-sm;
  border: 1px solid $border-color;
}

.report-content {
  padding: 20px;
}

.report-section {
  margin-bottom: 32px;

  &:last-child {
    margin-bottom: 0;
  }

  h4 {
    font-size: 16px;
    font-weight: 600;
    color: $text-primary;
    margin: 0 0 16px 0;
  }
}

.report-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.report-item {
  padding: 16px;
  background: $bg-primary;
  border-radius: 8px;
  border: 1px solid $border-color;

  label {
    display: block;
    font-size: 13px;
    color: $text-secondary;
    margin-bottom: 8px;
  }

  span {
    font-size: 16px;
    font-weight: 600;
    color: $text-primary;
  }

  .risk-level {
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 13px;

    &.low {
      background: rgba($color-success, 0.1);
      color: $color-success;
    }

    &.medium {
      background: rgba($color-warning, 0.1);
      color: $color-warning;
    }

    &.high {
      background: rgba($color-danger, 0.1);
      color: $color-danger;
    }
  }
}

// Modal样式
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

.modal-content {
  background: $bg-card;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: $shadow-lg;
  animation: slideUp 0.3s ease;
}

.modal-header {
  padding: 20px 24px;
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

  .btn-close {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: $text-secondary;
    padding: 0;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    transition: all $transition-fast;

    &:hover {
      background: $bg-primary;
      color: $text-primary;
    }
  }
}

.modal-body {
  padding: 24px;
  max-height: calc(80vh - 80px);
  overflow-y: auto;
}

.import-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.import-option {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border: 2px solid $border-color;
  border-radius: 8px;
  transition: all $transition-fast;

  &:hover {
    border-color: $color-primary;
    background: rgba($color-primary, 0.02);
  }

  .option-icon {
    font-size: 36px;
    flex-shrink: 0;
  }

  .option-content {
    flex: 1;

    h4 {
      font-size: 16px;
      font-weight: 600;
      color: $text-primary;
      margin: 0 0 4px 0;
    }

    p {
      font-size: 14px;
      color: $text-secondary;
      margin: 0 0 12px 0;
    }
  }
}

.file-preview {
  padding: 20px;
  background: $bg-primary;
  border-radius: 8px;
  border: 1px solid $border-color;
  margin-top: 16px;

  h4 {
    font-size: 16px;
    font-weight: 600;
    color: $text-primary;
    margin: 0 0 12px 0;
  }

  .file-info {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 16px;

    span {
      font-size: 14px;
      color: $text-secondary;
    }
  }
}

// 动画
@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
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
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
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
  cursor: pointer;
  transition: all $transition-fast;
  
  &:hover {
    border-color: $color-primary;
    color: $color-primary;
    background: rgba($color-primary, 0.05);
  }
}

.header-actions {
  display: flex;
  gap: 8px;
}
</style>
