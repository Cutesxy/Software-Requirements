/**
 * CSV数据加载器
 * 加载并解析arbitrage_signals.csv文件
 */

class CsvLoader {
  constructor() {
    this.signals = []
    this.loaded = false
  }

  /**
   * 异步加载CSV文件
   */
  async loadSignals() {
    if (this.loaded) {
      return this.signals
    }

    try {
      const response = await fetch('/arbitrage_signals.csv')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const csvText = await response.text()
      this.signals = this.parseCSV(csvText)
      this.loaded = true

      console.log(`Loaded ${this.signals.length} signals from CSV`)
      return this.signals
    } catch (error) {
      console.error('Failed to load CSV data:', error)
      throw error
    }
  }

  /**
   * 解析CSV文本
   */
  parseCSV(csvText) {
    const lines = csvText.trim().split('\n')
    if (lines.length < 2) {
      throw new Error('CSV file must have at least header and one data row')
    }

    // 解析表头
    const headers = lines[0].split(',').map(h => h.trim())

    // 解析数据行
    const signals = []
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(v => v.trim())
      if (values.length !== headers.length) {
        console.warn(`Skipping line ${i + 1}: expected ${headers.length} columns, got ${values.length}`)
        continue
      }

      const signal = this.convertToSignalFormat(headers, values)
      if (signal) {
        signals.push(signal)
      }
    }

    return signals
  }

  /**
   * 将CSV行转换为前端Signal格式
   */
  convertToSignalFormat(headers, values) {
    try {
      const row = {}
      headers.forEach((header, index) => {
        row[header] = values[index]
      })

      // 转换数据类型
      const signal = {
        id: `real_${row.id}`,
        time: parseInt(row.timestamp) * 1000, // 转换为毫秒
        direction: row.direction === 'sell' ? 'CEX->DEX' : 'DEX->CEX',
        spread: parseFloat(row.price_difference),
        spreadPct: Math.abs(parseFloat(row.price_difference)) / Math.max(parseFloat(row.binance_close_price), parseFloat(row.uniswap_avg_price)),
        zScore: 2.0, // CSV中没有zScore，使用默认值
        size: 1000, // CSV中没有交易规模，使用默认值
        grossProfit: parseFloat(row.gross_profit),
        totalCost: parseFloat(row.binance_fee) + parseFloat(row.uniswap_fee) + parseFloat(row.gas_cost),
        netProfit: parseFloat(row.net_profit),
        confidence: parseFloat(row.confidence),
        cexPrice: parseFloat(row.binance_close_price),
        dexPrice: parseFloat(row.uniswap_avg_price),
        params: {
          source: 'csv',
          originalId: row.id,
          timeBucket: row.time_bucket
        }
      }

      return signal
    } catch (error) {
      console.error('Error converting CSV row to signal format:', error, { headers, values })
      return null
    }
  }

  /**
   * 根据时间范围过滤信号
   */
  filterSignalsByTime(signals, startTime, endTime) {
    return signals.filter(signal =>
      signal.time >= startTime && signal.time <= endTime
    )
  }

  /**
   * 获取时间范围内的信号
   */
  async getSignalsInRange(startTime, endTime) {
    const allSignals = await this.loadSignals()
    return this.filterSignalsByTime(allSignals, startTime, endTime)
  }

  /**
   * 从信号中提取原始数据（价格和价差）
   * 用于Overview页面的图表展示
   */
  async getRawData(startTime, endTime) {
    const signals = await this.getSignalsInRange(startTime, endTime)
    
    // 按照时间排序
    signals.sort((a, b) => a.time - b.time)

    const cexPrices = []
    const dexPrices = []
    const spreadData = []

    signals.forEach(s => {
      // 构造价格数据点
      cexPrices.push({
        t: s.time,
        p: s.cexPrice,
        v: s.size, // 使用交易规模作为成交量近似值
        lat_ms: 100 // 默认延迟
      })

      dexPrices.push({
        t: s.time,
        p: s.dexPrice,
        v: s.size,
        lat_ms: 200
      })

      // 构造价差数据点
      spreadData.push({
        t: s.time,
        spread: s.spread,
        spreadPct: s.spreadPct,
        z: s.zScore,
        cexPrice: s.cexPrice,
        dexPrice: s.dexPrice,
        volume: s.size // 添加 volume 字段供 Overview 使用
      })
    })

    return {
      priceData: { cex: cexPrices, dex: dexPrices },
      spreadData: spreadData
    }
  }
}

export default new CsvLoader()
