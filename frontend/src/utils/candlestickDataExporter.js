/**
 * K线图数据导出工具
 * 将价格数据转换为K线图格式并保存为JSON
 */

import processedDataLoader from './processedDataLoader'

class CandlestickDataExporter {
  /**
   * 将价格数据聚合为K线数据
   * @param {Array} priceData - 价格数据 [{t: timestamp, p: price}, ...]
   * @param {Number} interval - 时间间隔（毫秒），默认1小时
   * @returns {Array} K线数据 [{time, open, close, high, low, volume}, ...]
   */
  aggregateToCandles(priceData, interval = 60 * 60 * 1000) {
    if (!priceData || priceData.length === 0) return []

    // 按时间窗口分组
    const buckets = new Map()

    priceData.forEach(point => {
      const bucketTime = Math.floor(point.t / interval) * interval
      if (!buckets.has(bucketTime)) {
        buckets.set(bucketTime, {
          prices: [],
          volumes: []
        })
      }
      buckets.get(bucketTime).prices.push(point.p)
      if (point.v) {
        buckets.get(bucketTime).volumes.push(point.v)
      }
    })

    // 转换为K线格式
    const candles = []
    buckets.forEach((data, bucketTime) => {
      if (data.prices.length === 0) return

      const prices = data.prices
      const open = prices[0] // 开盘价：第一个价格
      const close = prices[prices.length - 1] // 收盘价：最后一个价格
      const high = Math.max(...prices) // 最高价
      const low = Math.min(...prices) // 最低价
      const volume = data.volumes.reduce((sum, v) => sum + v, 0) // 总成交量

      candles.push({
        time: bucketTime,
        open: parseFloat(open.toFixed(2)),
        close: parseFloat(close.toFixed(2)),
        high: parseFloat(high.toFixed(2)),
        low: parseFloat(low.toFixed(2)),
        volume: parseFloat(volume.toFixed(2))
      })
    })

    // 按时间排序
    candles.sort((a, b) => a.time - b.time)

    return candles
  }

  /**
   * 导出K线数据为JSON格式
   * @param {Number} startTime - 开始时间（毫秒时间戳）
   * @param {Number} endTime - 结束时间（毫秒时间戳）
   * @param {Number} interval - 时间间隔（毫秒），默认1小时
   * @returns {Promise<Object>} K线数据对象
   */
  async exportCandlestickData(startTime, endTime, interval = 60 * 60 * 1000) {
    try {
      // 获取原始数据
      const rawData = await processedDataLoader.getRawData(startTime, endTime)

      // 生成K线数据
      const dexCandles = this.aggregateToCandles(rawData.priceData.dex, interval)
      const cexCandles = this.aggregateToCandles(rawData.priceData.cex, interval)

      // 构建导出数据
      const exportData = {
        meta: {
          startTime,
          endTime,
          interval,
          intervalLabel: this.getIntervalLabel(interval),
          dexCount: dexCandles.length,
          cexCount: cexCandles.length,
          exportTime: new Date().toISOString()
        },
        dex: dexCandles,
        cex: cexCandles
      }

      return exportData
    } catch (error) {
      console.error('导出K线数据失败:', error)
      throw error
    }
  }

  /**
   * 导出K线数据并下载为JSON文件
   * @param {Number} startTime - 开始时间（毫秒时间戳）
   * @param {Number} endTime - 结束时间（毫秒时间戳）
   * @param {Number} interval - 时间间隔（毫秒），默认1小时
   * @param {String} filename - 文件名（可选）
   */
  async exportAndDownload(startTime, endTime, interval = 60 * 60 * 1000, filename = null) {
    try {
      const data = await this.exportCandlestickData(startTime, endTime, interval)

      // 生成文件名
      if (!filename) {
        const startDate = new Date(startTime).toISOString().split('T')[0]
        const endDate = new Date(endTime).toISOString().split('T')[0]
        filename = `candlestick_${startDate}_${endDate}.json`
      }

      // 转换为JSON字符串
      const jsonString = JSON.stringify(data, null, 2)

      // 创建Blob并下载
      const blob = new Blob([jsonString], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)

      console.log(`K线数据已导出: ${filename}`)
      return data
    } catch (error) {
      console.error('导出并下载K线数据失败:', error)
      throw error
    }
  }

  /**
   * 获取时间间隔标签
   * @param {Number} interval - 时间间隔（毫秒）
   * @returns {String} 间隔标签
   */
  getIntervalLabel(interval) {
    const minutes = interval / (60 * 1000)
    const hours = interval / (60 * 60 * 1000)
    const days = interval / (24 * 60 * 60 * 1000)

    if (days >= 1) {
      return `${days}天`
    } else if (hours >= 1) {
      return `${hours}小时`
    } else {
      return `${minutes}分钟`
    }
  }
}

export default new CandlestickDataExporter()

