/**
 * 后端API调用工具类
 * 统一管理所有后端API请求
 */

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:5319'

class ApiClient {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL
  }

  /**
   * 通用请求方法
   */
  async request(endpoint, params = {}) {
    try {
      const url = new URL(`${this.baseURL}${endpoint}`)
      Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
          url.searchParams.append(key, params[key])
        }
      })

      const response = await fetch(url.toString(), {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return data
    } catch (error) {
      console.error(`API Request Error [${endpoint}]:`, error)
      throw error
    }
  }

  /**
   * 获取图表数据
   * @param {string} type - 数据类型: price | spread | heatmap | correlation
   * @param {number} start - 开始时间戳(秒)
   * @param {number} end - 结束时间戳(秒)
   * @param {string} interval - 时间间隔，默认15m
   */
  async getData(type, start, end, interval = '15m') {
    return this.request('/app/getdata', {
      type,
      start,
      end,
      interval
    })
  }

  /**
   * 获取价格数据
   */
  async getPriceData(start, end, interval = '15m') {
    return this.getData('price', start, end, interval)
  }

  /**
   * 获取价差数据
   */
  async getSpreadData(start, end, interval = '15m') {
    return this.getData('spread', start, end, interval)
  }

  /**
   * 获取热力图数据
   */
  async getHeatmapData(start, end) {
    return this.getData('heatmap', start, end)
  }

  /**
   * 获取相关性数据
   */
  async getCorrelationData(start, end) {
    return this.getData('correlation', start, end)
  }

  /**
   * 获取回测结果或信号
   * @param {string} type - 结果类型: signals | backtest
   * @param {number} start - 开始时间戳(秒)
   * @param {number} end - 结束时间戳(秒)
   * @param {number} zThreshold - Z-Score阈值，默认2.0
   * @param {number} tradeSize - 交易规模(USDT)，默认10000
   */
  async getResult(type, start, end, zThreshold = 2.0, tradeSize = 10000) {
    return this.request('/app/getresult', {
      type,
      start,
      end,
      zThreshold,
      tradeSize
    })
  }

  /**
   * 获取信号列表
   */
  async getSignals(start, end, zThreshold = 2.0, tradeSize = 10000) {
    return this.getResult('signals', start, end, zThreshold, tradeSize)
  }

  /**
   * 获取回测统计
   */
  async getBacktestStats(start, end, zThreshold = 2.0, tradeSize = 10000) {
    return this.getResult('backtest', start, end, zThreshold, tradeSize)
  }
}

export default new ApiClient()

