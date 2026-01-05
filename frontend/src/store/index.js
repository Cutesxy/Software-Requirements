import Vue from 'vue'
import Vuex from 'vuex'
import csvLoader from '@/utils/csvLoader'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    // 用户认证
    user: null,
    isLoggedIn: false,
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
    user: state => state.user,
    isLoggedIn: state => state.isLoggedIn,
    config: state => state.config,
    priceData: state => state.priceData,
    spreadData: state => state.spreadData,
    signals: state => state.signals,
    loading: state => state.loading
  },
  
  mutations: {
    SET_USER(state, user) {
      state.user = user
      state.isLoggedIn = !!user
    },
    
    CLEAR_USER(state) {
      state.user = null
      state.isLoggedIn = false
    },
    
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
      // 深度合并，特别是处理嵌套的 fees 对象
      const oldParams = { ...state.config.detector }
      state.config.detector = {
        ...state.config.detector,
        ...params,
        fees: {
          ...state.config.detector.fees,
          ...(params.fees || {})
        }
      }
      console.log('Updated detector params:', {
        old: { priceThreshold: oldParams.priceThreshold, zScoreThreshold: oldParams.zScoreThreshold, volumeMin: oldParams.volumeMin },
        new: { priceThreshold: state.config.detector.priceThreshold, zScoreThreshold: state.config.detector.zScoreThreshold, volumeMin: state.config.detector.volumeMin }
      })
    }
  },
  
  actions: {
    // 用户登录
    async login({ commit }, { username, password }) {
      const api = (await import('@/utils/api')).default
      const result = await api.login({ username, password })
      if (result.success) {
        commit('SET_USER', result.user)
      }
      return result
    },
    
    // 用户登出
    async logout({ commit }) {
      const api = (await import('@/utils/api')).default
      try {
        await api.logout()
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        commit('CLEAR_USER')
      }
    },
    
    // 检查登录状态
    async checkAuth({ commit }) {
      const api = (await import('@/utils/api')).default
      try {
        const result = await api.checkAuth()
        if (result.logged_in) {
          commit('SET_USER', result.user)
        } else {
          commit('CLEAR_USER')
        }
        return result
      } catch (error) {
        console.error('Check auth error:', error)
        commit('CLEAR_USER')
        return { logged_in: false, user: null }
      }
    },
    
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
        
        console.log('Filtering signals with params:', { priceThreshold, zScoreThreshold, volumeMin })
        console.log(`Before filtering: ${signals.length} signals`)
        
        // 统计各条件的过滤情况
        let priceFiltered = 0
        let zScoreFiltered = 0
        let volumeFiltered = 0
        let totalFiltered = 0
        
        // 先统计所有信号的分布情况
        const allSpreads = signals.map(s => Math.abs(s.spread || 0)).sort((a, b) => a - b)
        const minSpread = allSpreads[0] || 0
        const maxSpread = allSpreads[allSpreads.length - 1] || 0
        const medianSpread = allSpreads[Math.floor(allSpreads.length / 2)] || 0
        console.log(`Spread stats: min=${minSpread.toFixed(2)}, max=${maxSpread.toFixed(2)}, median=${medianSpread.toFixed(2)}`)
        console.log(`Signals below priceThreshold ${priceThreshold}: ${allSpreads.filter(s => s < priceThreshold).length}`)
        
        signals = signals.filter(s => {
          const spread = Math.abs(s.spread || 0)
          const zScore = Math.abs(s.zScore || 0)
          const volume = s.size || 0
          
          const passPrice = spread >= priceThreshold
          const passZScore = zScore >= zScoreThreshold
          const passVolume = volume >= volumeMin
          
          if (!passPrice) priceFiltered++
          if (!passZScore) zScoreFiltered++
          if (!passVolume) volumeFiltered++
          
          const pass = passPrice && passZScore && passVolume
          if (!pass) totalFiltered++
          
          return pass
        })

        console.log(`After filtering: ${signals.length} signals (filtered out: ${totalFiltered})`)
        console.log(`Filtered by price: ${priceFiltered}, by zScore: ${zScoreFiltered}, by volume: ${volumeFiltered}`)
        console.log(`Expected filtered by price: ${allSpreads.filter(s => s < priceThreshold).length} signals have spread < ${priceThreshold}`)
        
        // 采样检查前几个信号的 spread 值
        if (signals.length > 0) {
          const sampleSpreads = signals.slice(0, 5).map(s => Math.abs(s.spread || 0))
          console.log('Sample spreads (after filter):', sampleSpreads)
        } else {
          console.log('No signals passed the filter!')
        }
        
        // 强制创建新数组，确保 Vue 响应式更新
        commit('SET_SIGNALS', [...signals])
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

