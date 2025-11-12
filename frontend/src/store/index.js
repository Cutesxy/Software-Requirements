import Vue from 'vue'
import Vuex from 'vuex'
import mockData from '@/utils/mockData'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    // 全局配置
    config: {
      pair: 'USDT/ETH',
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
        const data = mockData.generatePriceData(
          state.config.timeRange.start,
          state.config.timeRange.end,
          state.config.interval
        )
        commit('SET_PRICE_DATA', data)
        return data
      } catch (error) {
        console.error('加载价格数据失败:', error)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    // 加载价差数据
    async loadSpreadData({ commit, state }) {
      commit('SET_LOADING', true)
      try {
        const data = mockData.generateSpreadData(
          state.config.timeRange.start,
          state.config.timeRange.end,
          state.config.interval
        )
        commit('SET_SPREAD_DATA', data)
        return data
      } catch (error) {
        console.error('加载价差数据失败:', error)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    // 检测套利信号
    async detectSignals({ commit, state }) {
      commit('SET_LOADING', true)
      try {
        const signals = mockData.generateSignals(
          state.config.timeRange.start,
          state.config.timeRange.end,
          state.config.detector
        )
        commit('SET_SIGNALS', signals)
        return signals
      } catch (error) {
        console.error('检测套利信号失败:', error)
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

