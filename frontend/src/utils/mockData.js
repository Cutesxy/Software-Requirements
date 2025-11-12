/**
 * 模拟数据生成器
 * 生成符合区块链套利场景的模拟数据
 */

class MockDataGenerator {
  constructor() {
    this.basePrice = 2580 // ETH/USDT 基准价格
    this.volatility = 0.02 // 波动率
  }
  
  /**
   * 生成时间序列
   */
  generateTimeRange(start, end, interval = '1m') {
    const times = []
    const intervalMs = this.parseInterval(interval)
    let current = start
    
    while (current <= end) {
      times.push(current)
      current += intervalMs
    }
    
    return times
  }
  
  /**
   * 解析时间间隔
   */
  parseInterval(interval) {
    const unit = interval.slice(-1)
    const value = parseInt(interval.slice(0, -1))
    
    const units = {
      's': 1000,
      'm': 60 * 1000,
      'h': 60 * 60 * 1000,
      'd': 24 * 60 * 60 * 1000
    }
    
    return value * (units[unit] || units['m'])
  }
  
  /**
   * 生成价格数据（带布朗运动）
   */
  generatePriceData(start, end, interval = '1m') {
    const times = this.generateTimeRange(start, end, interval)
    const cexPrices = []
    const dexPrices = []
    
    let cexPrice = this.basePrice
    let dexPrice = this.basePrice * (1 + Math.random() * 0.002 - 0.001) // DEX略有差异
    
    times.forEach((time, index) => {
      // 价格随机游走（布朗运动）
      const cexChange = (Math.random() - 0.5) * this.volatility * cexPrice
      const dexChange = (Math.random() - 0.5) * this.volatility * dexPrice
      
      cexPrice += cexChange
      dexPrice += dexChange
      
      // 添加周期性价差（套利机会）
      if (index % 300 === 0) {
        const spreadBoost = (Math.random() - 0.5) * 0.01 * dexPrice
        dexPrice += spreadBoost
      }
      
      // CEX数据
      cexPrices.push({
        t: time,
        p: parseFloat(cexPrice.toFixed(2)),
        v: Math.random() * 50 + 10, // 成交量
        lat_ms: Math.random() * 200 + 50 // 延迟
      })
      
      // DEX数据
      dexPrices.push({
        t: time,
        p: parseFloat(dexPrice.toFixed(2)),
        v: Math.random() * 20 + 5,
        lat_ms: Math.random() * 500 + 100
      })
    })
    
    return { cex: cexPrices, dex: dexPrices }
  }
  
  /**
   * 生成价差数据
   */
  generateSpreadData(start, end, interval = '1m') {
    const priceData = this.generatePriceData(start, end, interval)
    const spreadData = []
    
    const cex = priceData.cex
    const dex = priceData.dex
    
    // 计算滑动窗口均值和标准差
    const windowSize = 100
    
    for (let i = 0; i < cex.length; i++) {
      const spread = cex[i].p - dex[i].p
      
      // 计算Z-score
      let zScore = 0
      if (i >= windowSize) {
        const window = []
        for (let j = i - windowSize; j < i; j++) {
          window.push(cex[j].p - dex[j].p)
        }
        const mean = window.reduce((a, b) => a + b) / window.length
        const std = Math.sqrt(
          window.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / window.length
        )
        zScore = std > 0 ? (spread - mean) / std : 0
      }
      
      spreadData.push({
        t: cex[i].t,
        spread: parseFloat(spread.toFixed(2)),
        spreadPct: parseFloat((spread / cex[i].p * 100).toFixed(4)),
        z: parseFloat(zScore.toFixed(2)),
        cexPrice: cex[i].p,
        dexPrice: dex[i].p
      })
    }
    
    return spreadData
  }
  
  /**
   * 生成套利信号
   */
  generateSignals(start, end, detectorParams) {
    const spreadData = this.generateSpreadData(start, end, '1m')
    const signals = []
    
    const { priceThreshold, zScoreThreshold, timeWindow, volumeMin, fees } = detectorParams
    
    spreadData.forEach((data, index) => {
      // 检测套利机会
      const absSpread = Math.abs(data.spread)
      const absZ = Math.abs(data.z)
      
      if (absSpread >= priceThreshold && absZ >= zScoreThreshold) {
        // 计算预期收益
        const direction = data.spread > 0 ? 'CEX->DEX' : 'DEX->CEX'
        const size = Math.random() * 5000 + volumeMin
        const grossProfit = absSpread * size
        
        // 扣除费用
        const cexFee = size * data.cexPrice * fees.cex
        const dexFee = size * data.dexPrice * fees.dex
        const gasFee = fees.gas
        const slippageCost = size * data.cexPrice * fees.slippage
        
        const totalCost = cexFee + dexFee + gasFee + slippageCost
        const netProfit = grossProfit - totalCost
        
        // 只保留盈利的信号
        if (netProfit > 0) {
          signals.push({
            id: `sig_${data.t}`,
            time: data.t,
            direction,
            spread: data.spread,
            spreadPct: data.spreadPct,
            zScore: data.z,
            size: parseFloat(size.toFixed(2)),
            grossProfit: parseFloat(grossProfit.toFixed(2)),
            totalCost: parseFloat(totalCost.toFixed(2)),
            netProfit: parseFloat(netProfit.toFixed(2)),
            confidence: Math.min(absZ / 5, 1), // 基于Z-score的置信度
            cexPrice: data.cexPrice,
            dexPrice: data.dexPrice,
            params: { ...detectorParams }
          })
        }
      }
    })
    
    return signals
  }
  
  /**
   * 生成热力图数据
   */
  generateHeatmapData(start, end) {
    const spreadData = this.generateSpreadData(start, end, '5s')
    const heatmap = []
    
    // 按小时分组
    const grouped = {}
    spreadData.forEach(d => {
      const hour = new Date(d.t).getHours()
      if (!grouped[hour]) grouped[hour] = []
      grouped[hour].push(d.z)
    })
    
    // 生成热力图数据
    Object.keys(grouped).forEach(hour => {
      const values = grouped[hour]
      const bins = 20 // 分成20个bin
      const binSize = values.length / bins
      
      for (let i = 0; i < bins; i++) {
        const binValues = values.slice(i * binSize, (i + 1) * binSize)
        const avgZ = binValues.reduce((a, b) => a + b, 0) / binValues.length
        
        heatmap.push([
          parseInt(hour),
          i,
          parseFloat(avgZ.toFixed(2))
        ])
      }
    })
    
    return heatmap
  }
  
  /**
   * 生成相关性数据
   */
  generateCorrelationData(start, end) {
    const priceData = this.generatePriceData(start, end, '1m')
    const cex = priceData.cex.map(d => d.p)
    const dex = priceData.dex.map(d => d.p)
    
    // 计算不同滞后的相关系数
    const maxLag = 60 // 最大滞后60个时间点
    const correlations = []
    
    for (let lag = -maxLag; lag <= maxLag; lag++) {
      const corr = this.calculateCorrelation(cex, dex, lag)
      correlations.push({ lag, correlation: corr })
    }
    
    return correlations
  }
  
  /**
   * 计算相关系数
   */
  calculateCorrelation(arr1, arr2, lag) {
    const n = Math.min(arr1.length, arr2.length) - Math.abs(lag)
    if (n <= 0) return 0
    
    const start1 = lag >= 0 ? lag : 0
    const start2 = lag >= 0 ? 0 : -lag
    
    let sum1 = 0, sum2 = 0, sum1Sq = 0, sum2Sq = 0, pSum = 0
    
    for (let i = 0; i < n; i++) {
      const val1 = arr1[start1 + i]
      const val2 = arr2[start2 + i]
      
      sum1 += val1
      sum2 += val2
      sum1Sq += val1 * val1
      sum2Sq += val2 * val2
      pSum += val1 * val2
    }
    
    const num = pSum - (sum1 * sum2 / n)
    const den = Math.sqrt((sum1Sq - sum1 * sum1 / n) * (sum2Sq - sum2 * sum2 / n))
    
    return den === 0 ? 0 : num / den
  }
  
  /**
   * 生成回测结果
   */
  generateBacktestResults(params) {
    const signals = this.generateSignals(
      new Date('2025-09-01').getTime(),
      new Date('2025-09-30').getTime(),
      params
    )
    
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
}

export default new MockDataGenerator()

