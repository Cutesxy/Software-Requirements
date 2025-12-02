/**
 * Web Worker 用于后台处理大量数据
 * 避免阻塞主线程，保持 UI 响应性
 */

// 监听主线程发送的消息
self.onmessage = function(e) {
  const { type, payload } = e.data

  try {
    let result

    switch (type) {
      case 'CONVERT_PRICE_DATA':
        result = convertToPriceData(payload.data)
        break
      
      case 'CONVERT_SPREAD_DATA':
        result = convertToSpreadData(payload.data)
        break
      
      case 'GENERATE_SIGNALS':
        result = generateSignals(payload.data, payload.params)
        break
      
      case 'FILTER_BY_TIME':
        result = filterDataByTime(payload.data, payload.startTime, payload.endTime)
        break
      
      case 'BATCH_PROCESS':
        // 批量处理多个任务
        result = batchProcess(payload.tasks)
        break
      
      default:
        throw new Error(`Unknown message type: ${type}`)
    }

    // 发送处理结果回主线程
    self.postMessage({
      success: true,
      type,
      result,
      taskId: payload.taskId
    })
  } catch (error) {
    // 发送错误信息回主线程
    self.postMessage({
      success: false,
      type,
      error: error.message,
      taskId: payload.taskId
    })
  }
}

/**
 * 将原始数据转换为价格数据格式
 */
function convertToPriceData(data) {
  const cexPrices = []
  const dexPrices = []

  for (let i = 0; i < data.length; i++) {
    const item = data[i]
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
  }

  return { cex: cexPrices, dex: dexPrices }
}

/**
 * 将原始数据转换为价差数据格式
 */
function convertToSpreadData(data) {
  const spreadData = []

  for (let i = 0; i < data.length; i++) {
    const item = data[i]
    const [timestamp, uData, bData, priceDiff] = item

    const time = timestamp * 1000
    const cexPrice = bData[3] // c: 收盘价
    const dexPrice = uData[3] // ap: 平均价格

    // 计算价差
    const spread = cexPrice - dexPrice
    const spreadPct = (spread / cexPrice) * 100

    // 计算 Z-Score (这里使用简单的标准化，实际应该使用滑动窗口)
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
  }

  return spreadData
}

/**
 * 从数据生成套利信号
 */
function generateSignals(data, detectorParams) {
  const { priceThreshold, zScoreThreshold, volumeMin, fees } = detectorParams
  const signals = []

  for (let i = 0; i < data.length; i++) {
    const item = data[i]
    const [timestamp, uData, bData, priceDiff] = item

    const time = timestamp * 1000
    const cexPrice = bData[3] // c: 收盘价
    const dexPrice = uData[3] // ap: 平均价格
    const spread = cexPrice - dexPrice
    const volume = bData[4] + uData[1] // 总成交量

    // 检查是否满足最小成交量要求
    if (volume < volumeMin) continue

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
  }

  return signals
}

/**
 * 根据时间范围过滤数据
 */
function filterDataByTime(data, startTime, endTime) {
  const extendedStartTime = startTime - 60 * 60 * 1000 // 前1小时
  const extendedEndTime = endTime + 60 * 60 * 1000 // 后1小时

  const filtered = []
  for (let i = 0; i < data.length; i++) {
    const item = data[i]
    const timestamp = item[0] * 1000 // 转换为毫秒
    if (timestamp >= extendedStartTime && timestamp <= extendedEndTime) {
      filtered.push(item)
    }
  }

  return filtered
}

/**
 * 批量处理多个任务
 */
function batchProcess(tasks) {
  const results = {}
  
  for (let i = 0; i < tasks.length; i++) {
    const task = tasks[i]
    try {
      let result
      
      switch (task.type) {
        case 'CONVERT_PRICE_DATA':
          result = convertToPriceData(task.data)
          break
        case 'CONVERT_SPREAD_DATA':
          result = convertToSpreadData(task.data)
          break
        case 'GENERATE_SIGNALS':
          result = generateSignals(task.data, task.params)
          break
        case 'FILTER_BY_TIME':
          result = filterDataByTime(task.data, task.startTime, task.endTime)
          break
        default:
          throw new Error(`Unknown task type: ${task.type}`)
      }
      
      results[task.id] = { success: true, result }
    } catch (error) {
      results[task.id] = { success: false, error: error.message }
    }
  }
  
  return results
}

