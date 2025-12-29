import Vue from 'vue'
import Vuex from 'vuex'
import csvLoader from '@/utils/csvLoader'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    // 全局配置
    config: {
      pair: 'ETH/USDT',
      dex: 'Uniswap V3 (0.3%)',
      cex: 'Binance',
      timeRange: {
        start: new Date('2025-09-01').getTime(),
        end: new Date('2025-09-30').getTime()
      },
      timezone: 'Asia/Shanghai',
      interval: '1m',
      // 检测器参数
      detector: {
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
    },
    // 数据缓存
    priceData: null,
    spreadData: null,
    signals: null,
    loading: false
  },
  
  getters: {
    config: state => state.config,
    priceData: state => state.priceData,
    spreadData: state => state.spreadData,
    signals: state => state.signals,
    loading: state => state.loading
  },
  
  mutations: {
    SET_CONFIG(state, config) {
      state.config = { ...state.config, ...config }
    },
    
    SET_PRICE_DATA(state, data) {
      state.priceData = data
    },
    
    SET_SPREAD_DATA(state, data) {
      state.spreadData = data
    },
    
    SET_SIGNALS(state, signals) {
      state.signals = signals
    },
    
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    
    UPDATE_DETECTOR_PARAMS(state, params) {
      state.config.detector = { ...state.config.detector, ...params }
    }
  },
  
  actions: {
    // 加载价格数据
    async loadPriceData({ commit, state }) {
      commit('SET_LOADING', true)
      try {
        const rawData = await csvLoader.getRawData(
          state.config.timeRange.start,
          state.config.timeRange.end
        )
        commit('SET_PRICE_DATA', rawData.priceData)
        return rawData.priceData
      } catch (error) {
        console.error('加载价格数据失败:', error)
        commit('SET_PRICE_DATA', null)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    // 加载价差数据
    async loadSpreadData({ commit, state }) {
      commit('SET_LOADING', true)
      try {
        const rawData = await csvLoader.getRawData(
          state.config.timeRange.start,
          state.config.timeRange.end
        )
        commit('SET_SPREAD_DATA', rawData.spreadData)
        return rawData.spreadData
      } catch (error) {
        console.error('加载价差数据失败:', error)
        commit('SET_SPREAD_DATA', null)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    // 检测套利信号
    async detectSignals({ commit, state }) {
      commit('SET_LOADING', true)
      try {
        let signals = await csvLoader.getSignalsInRange(
          state.config.timeRange.start,
          state.config.timeRange.end
        )
        
        // 获取当前费率配置
        const { fees } = state.config.detector
        
        // 重新计算信号的净利润和Z-Score (基于当前费率参数)
        signals = signals.map(s => {
          // 1. 计算新的交易成本
          // 注意：这里为了简化，假设Size是ETH数量，Price是USDT
          // CEX费用 = 交易额 * CEX费率
          const cexFee = s.cexPrice * s.size * fees.cex
          
          // DEX费用 = 交易额 * DEX费率
          const dexFee = s.dexPrice * s.size * fees.dex
          
          // 滑点成本 = 交易额 * 滑点率
          const slippageCost = ((s.cexPrice + s.dexPrice) / 2) * s.size * fees.slippage
          
          // 总成本 = CEX费用 + DEX费用 + Gas费 + 滑点成本
          const totalCost = cexFee + dexFee + fees.gas + slippageCost
          
          // 2. 计算净利润
          const netProfit = s.grossProfit - totalCost
          
          // 3. 动态计算 Z-Score
          // 使用价差百分比 * 100 作为 Z-Score 的近似值
          // 例如 1% 价差 -> Z-Score = 1.0; 5% 价差 -> Z-Score = 5.0
          const zScore = (Math.abs(s.spread) / ((s.cexPrice + s.dexPrice) / 2)) * 100
          
          return {
            ...s,
            totalCost,
            netProfit,
            zScore
          }
        })

        // 根据检测器参数过滤信号
        const { priceThreshold, zScoreThreshold, volumeMin } = state.config.detector
        
        signals = signals.filter(s => {
          return Math.abs(s.spread) >= priceThreshold &&
                 Math.abs(s.zScore) >= zScoreThreshold &&
                 s.size >= volumeMin
        })

        console.log(`Loaded ${signals.length} real signals from CSV (filtered with dynamic params)`)
        commit('SET_SIGNALS', signals)
        return signals
      } catch (error) {
        console.error('检测套利信号失败:', error)
        commit('SET_SIGNALS', [])
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    // 更新配置
    updateConfig({ commit }, config) {
      commit('SET_CONFIG', config)
    },
    
    // 更新检测器参数
    updateDetectorParams({ commit }, params) {
      commit('UPDATE_DETECTOR_PARAMS', params)
    }
  }
})

