import Vue from 'vue'
import Vuex from 'vuex'
import processedDataLoader from '@/utils/processedDataLoader'

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
        timeWindow: [1, 20],
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
        const rawData = await processedDataLoader.getRawData(
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
        const rawData = await processedDataLoader.getRawData(
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
        const signals = await processedDataLoader.getSignalsInRange(
          state.config.timeRange.start,
          state.config.timeRange.end,
          state.config.detector
        )

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

