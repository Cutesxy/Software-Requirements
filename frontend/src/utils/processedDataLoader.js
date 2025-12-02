/**
 * 处理后的数据加载器
 * 从 processed_data.json 加载并转换数据为前端需要的格式
 * 使用 Web Worker 进行后台处理，避免阻塞主线程
 */

import workerManager from './workerManager'

class ProcessedDataLoader {
  constructor() {
    this.data = null
    this.loaded = false
    this.useWorker = true // 是否使用 Worker（可以通过环境变量控制）
    this.candlestickData = null // 预处理的K线数据
    this.candlestickLoaded = false
  }

  /**
   * 异步加载processed_data.json文件
   */
  async loadData() {
    if (this.loaded && this.data) {
      return this.data
    }

    try {
      const response = await fetch('/processed_data.json')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      this.data = await response.json()
      this.loaded = true

      // 允许全部数据，但提供性能警告
      if (this.data.data && this.data.data.length > 10000) {
        console.warn(`Large dataset detected: ${this.data.data.length} points. This may affect performance.`)
      }

      return this.data
    } catch (error) {
      console.error('Failed to load processed data:', error)
      // 返回空数据结构
      this.data = {
        meta: { total: 0, start: 0, end: 0, columns: [], u_columns: [], b_columns: [] },
        data: []
      }
      this.loaded = true
      return this.data
    }
  }

  /**
   * 获取时间范围内的原始数据（价格和价差）
   * 用于Overview页面的图表展示
   */
  async getRawData(startTime, endTime) {
    const data = await this.loadData()

    // 过滤时间范围内的数据
    // 扩大范围1小时以确保包含边界数据
    const extendedStartTime = startTime - 60 * 60 * 1000 // 前1小时
    const extendedEndTime = endTime + 60 * 60 * 1000 // 后1小时

    let filteredData

    // 尝试使用 Worker 过滤数据
    if (this.useWorker && workerManager.isAvailable()) {
      try {
        filteredData = await workerManager.postTask('FILTER_BY_TIME', {
          data: data.data,
          startTime: extendedStartTime,
          endTime: extendedEndTime
        })
      } catch (error) {
        console.warn('Worker filtering failed, using main thread:', error)
        filteredData = this.filterDataByTime(data.data, extendedStartTime, extendedEndTime)
      }
    } else {
      // 回退到主线程处理
      filteredData = this.filterDataByTime(data.data, extendedStartTime, extendedEndTime)
    }

    if (!filteredData || filteredData.length === 0) {
      // 返回空数据结构
      return {
        priceData: { cex: [], dex: [] },
        spreadData: []
      }
    }

    // 转换数据格式 - 使用 Worker 或主线程
    let priceData, spreadData

    if (this.useWorker && workerManager.isAvailable()) {
      try {
        // 并行处理价格和价差数据
        const [priceResult, spreadResult] = await Promise.all([
          workerManager.postTask('CONVERT_PRICE_DATA', { data: filteredData }),
          workerManager.postTask('CONVERT_SPREAD_DATA', { data: filteredData })
        ])

        priceData = priceResult || this.convertToPriceData(filteredData)
        spreadData = spreadResult || this.convertToSpreadData(filteredData)
      } catch (error) {
        console.warn('Worker conversion failed, using main thread:', error)
        priceData = this.convertToPriceData(filteredData)
        spreadData = this.convertToSpreadData(filteredData)
      }
    } else {
      // 回退到主线程处理
      priceData = this.convertToPriceData(filteredData)
      spreadData = this.convertToSpreadData(filteredData)
    }

    return {
      priceData,
      spreadData
    }
  }

  /**
   * 获取时间范围内的套利信号
   */
  async getSignalsInRange(startTime, endTime, detectorParams = {}) {
    const data = await this.loadData()

    // 默认检测器参数
    const defaultParams = {
      priceThreshold: 0.8,
      zScoreThreshold: 2.0,
      volumeMin: 1000,
      fees: {
        cex: 0.001,
        dex: 0.003,
        gas: 15,
        slippage: 0.002
      }
    }

    const params = { ...defaultParams, ...detectorParams }

    // 过滤时间范围内的数据
    let filteredData

    if (this.useWorker && workerManager.isAvailable()) {
      try {
        filteredData = await workerManager.postTask('FILTER_BY_TIME', {
          data: data.data,
          startTime,
          endTime
        })
      } catch (error) {
        console.warn('Worker filtering failed, using main thread:', error)
        filteredData = this.filterDataByTime(data.data, startTime, endTime)
      }
    } else {
      filteredData = this.filterDataByTime(data.data, startTime, endTime)
    }

    // 生成套利信号 - 使用 Worker 或主线程
    let signals

    if (this.useWorker && workerManager.isAvailable()) {
      try {
        signals = await workerManager.postTask('GENERATE_SIGNALS', {
          data: filteredData,
          params
        })
        if (!signals) {
          signals = this.generateSignals(filteredData, params)
        }
      } catch (error) {
        console.warn('Worker signal generation failed, using main thread:', error)
        signals = this.generateSignals(filteredData, params)
      }
    } else {
      signals = this.generateSignals(filteredData, params)
    }

    return signals
  }

  /**
   * 将原始数据转换为价格数据格式
   */
  convertToPriceData(data) {
    const cexPrices = []
    const dexPrices = []

    data.forEach(item => {
      const [timestamp, uData, bData] = item

      // 时间戳转换为毫秒
      const time = timestamp * 1000

      // Uniswap 数据 (u): [sc, ve, vu, ap, mp, xp, sd]
      // 我们使用 ap (平均价格) 作为 DEX 价格
      const dexPrice = uData[3] // ap: 平均价格
      const dexVolume = uData[1] // ve: 成交量

      // Binance 数据 (b): [o, h, l, c, v, qv, t]
      const cexPrice = bData[3] // c: 收盘价
      const cexVolume = bData[4] // v: 成交量

      // CEX 数据点
      cexPrices.push({
        t: time,
        p: parseFloat(cexPrice.toFixed(2)),
        v: parseFloat(cexVolume.toFixed(2)),
        lat_ms: 100 // 默认延迟
      })

      // DEX 数据点
      dexPrices.push({
        t: time,
        p: parseFloat(dexPrice.toFixed(2)),
        v: parseFloat(dexVolume.toFixed(2)),
        lat_ms: 200
      })
    })

    return { cex: cexPrices, dex: dexPrices }
  }

  /**
   * 将原始数据转换为价差数据格式
   */
  convertToSpreadData(data) {
    const spreadData = []

    data.forEach(item => {
      const [timestamp, uData, bData, priceDiff] = item

      const time = timestamp * 1000
      const cexPrice = bData[3] // c: 收盘价
      const dexPrice = uData[3] // ap: 平均价格

      // 计算价差
      const spread = cexPrice - dexPrice
      const spreadPct = (spread / cexPrice) * 100

      // 计算 Z-Score (这里使用简单的标准化，实际应该使用滑动窗口)
      // 暂时使用价差绝对值的标准化近似
      const zScore = Math.abs(spread) > 0 ? (spread / Math.abs(spread)) * Math.log(Math.abs(spread) + 1) : 0

      spreadData.push({
        t: time,
        spread: parseFloat(spread.toFixed(2)),
        spreadPct: parseFloat(spreadPct.toFixed(4)),
        z: parseFloat(zScore.toFixed(2)),
        cexPrice: parseFloat(cexPrice.toFixed(2)),
        dexPrice: parseFloat(dexPrice.toFixed(2)),
        volume: parseFloat((bData[4] + uData[1]).toFixed(2)) // 总成交量
      })
    })

    return spreadData
  }

  /**
   * 从数据生成套利信号
   */
  generateSignals(data, detectorParams) {
    const { priceThreshold, zScoreThreshold, volumeMin, fees } = detectorParams
    const signals = []

    data.forEach(item => {
      const [timestamp, uData, bData, priceDiff] = item

      const time = timestamp * 1000
      const cexPrice = bData[3] // c: 收盘价
      const dexPrice = uData[3] // ap: 平均价格
      const spread = cexPrice - dexPrice
      const volume = bData[4] + uData[1] // 总成交量

      // 检查是否满足最小成交量要求
      if (volume < volumeMin) return

      // 计算Z-score (简化版)
      const zScore = Math.abs(spread) > 0 ? (spread / Math.abs(spread)) * Math.log(Math.abs(spread) + 1) : 0

      // 检查阈值条件
      if (Math.abs(spread) >= priceThreshold && Math.abs(zScore) >= zScoreThreshold) {
        // 计算收益
        const direction = spread > 0 ? 'CEX->DEX' : 'DEX->CEX'
        const size = Math.min(volume, 5000) // 限制最大交易规模

        const grossProfit = Math.abs(spread) * size

        // 计算成本
        const cexFee = size * cexPrice * fees.cex
        const dexFee = size * dexPrice * fees.dex
        const gasFee = fees.gas
        const slippageCost = size * Math.max(cexPrice, dexPrice) * fees.slippage

        const totalCost = cexFee + dexFee + gasFee + slippageCost
        const netProfit = grossProfit - totalCost

        // 只保留盈利的信号
        if (netProfit > 0) {
          signals.push({
            id: `real_${timestamp}`,
            time,
            direction,
            spread: parseFloat(spread.toFixed(2)),
            spreadPct: parseFloat(((spread / cexPrice) * 100).toFixed(4)),
            zScore: parseFloat(zScore.toFixed(2)),
            size: parseFloat(size.toFixed(2)),
            grossProfit: parseFloat(grossProfit.toFixed(2)),
            totalCost: parseFloat(totalCost.toFixed(2)),
            netProfit: parseFloat(netProfit.toFixed(2)),
            confidence: Math.min(Math.abs(zScore) / 5, 1), // 基于Z-score的置信度
            cexPrice: parseFloat(cexPrice.toFixed(2)),
            dexPrice: parseFloat(dexPrice.toFixed(2)),
            params: { ...detectorParams }
          })
        }
      }
    })

    return signals
  }

  /**
   * 根据时间范围过滤数据
   */
  filterDataByTime(data, startTime, endTime) {
    return data.filter(item => {
      const timestamp = item[0] * 1000
      return timestamp >= startTime && timestamp <= endTime
    })
  }

  /**
   * 加载预处理的K线数据（按天聚合）
   */
  async loadCandlestickData() {
    if (this.candlestickLoaded && this.candlestickData) {
      return this.candlestickData
    }

    try {
      const response = await fetch('/candlestick_daily.json')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      this.candlestickData = await response.json()
      this.candlestickLoaded = true

      console.log('K线数据加载成功:', {
        dexCount: this.candlestickData.dex?.length || 0,
        cexCount: this.candlestickData.cex?.length || 0
      })

      return this.candlestickData
    } catch (error) {
      console.warn('加载预处理K线数据失败，将使用实时计算:', error)
      this.candlestickData = null
      this.candlestickLoaded = true
      return null
    }
  }

  /**
   * 获取时间范围内的K线数据（使用预处理数据）
   */
  async getCandlestickDataInRange(startTime, endTime) {
    // 尝试加载预处理数据
    const candlestickData = await this.loadCandlestickData()

    if (!candlestickData || !candlestickData.dex || !candlestickData.cex) {
      // 如果没有预处理数据，返回null，让前端使用实时计算
      return null
    }

    // 过滤时间范围内的K线数据
    const filterCandles = (candles) => {
      return candles.filter(candle => {
        // candle.time 是当天开始时间（00:00:00）
        // 需要检查是否在时间范围内
        const dayStart = candle.time
        const dayEnd = dayStart + 24 * 60 * 60 * 1000 - 1 // 当天结束时间（23:59:59.999）
        
        // 如果K线的日期与时间范围有重叠，就包含它
        return (dayStart <= endTime && dayEnd >= startTime)
      })
    }

    return {
      dex: filterCandles(candlestickData.dex),
      cex: filterCandles(candlestickData.cex)
    }
  }
}

export default new ProcessedDataLoader()
