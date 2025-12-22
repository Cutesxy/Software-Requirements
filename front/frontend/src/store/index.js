import Vue from 'vue'
import Vuex from 'vuex'
import csvLoader from '@/utils/csvLoader'
import axios from 'axios' 

Vue.use(Vuex)

// 创建axios实例，用于调用后端API
const apiClient = axios.create({
  baseURL: '/api'  // 通过代理连接到后端
})

export default new Vuex.Store({
  state: {
    // 全局配置 - 保持不变
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
    // 数据缓存 - 保持不变
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
    // 所有mutations保持不变
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
    // 从后端API加载价格数据
    async loadPriceData({ commit, state }) {
      commit('SET_LOADING', true)
      try {
        // 调用后端API获取价格数据
        const response = await apiClient.get('/app/getdata', {
          params: {
            start: Math.floor(state.config.timeRange.start / 1000), // 毫秒转秒
            end: Math.floor(state.config.timeRange.end / 1000),
            type: 'price',
            interval: state.config.interval
          }
        })
        
        const backendData = response.data
        
        // 将后端数据格式转换为前端期望的格式
        const priceData = {
          cex: backendData.cex.map(item => ({
            t: item.t * 1000, // 秒转毫秒
            p: item.p,
            v: item.v || 0,
            lat_ms: item.lat_ms || 0
          })),
          dex: backendData.dex.map(item => ({
            t: item.t * 1000, // 秒转毫秒
            p: item.p,
            v: item.v || 0,
            lat_ms: item.lat_ms || 0
          }))
        }
        
        commit('SET_PRICE_DATA', priceData)
        return priceData
      } catch (error) {
        console.error('从后端加载价格数据失败，回退到CSV数据:', error)
        
        // 如果后端失败，回退到CSV数据
        try {
          const rawData = await csvLoader.getRawData(
            state.config.timeRange.start,
            state.config.timeRange.end
          )
          commit('SET_PRICE_DATA', rawData.priceData)
          return rawData.priceData
        } catch (csvError) {
          console.error('CSV数据也加载失败:', csvError)
          commit('SET_PRICE_DATA', null)
          throw error
        }
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    // 从后端API加载价差数据
    async loadSpreadData({ commit, state }) {
      commit('SET_LOADING', true)
      try {
        // 调用后端API获取价差数据
        const response = await apiClient.get('/app/getdata', {
          params: {
            start: Math.floor(state.config.timeRange.start / 1000), // 毫秒转秒
            end: Math.floor(state.config.timeRange.end / 1000),
            type: 'spread'
          }
        })
        
        const backendData = response.data
        
        // 将后端数据格式转换为前端期望的格式
        const spreadData = backendData.map(item => ({
          t: item.t * 1000, // 秒转毫秒
          spread: item.spread,
          spreadPct: item.spreadPct,
          z: item.z,
          cexPrice: item.cexPrice,
          dexPrice: item.dexPrice,
          volume: item.v || 0 // 如果有成交量字段
        }))
        
        commit('SET_SPREAD_DATA', spreadData)
        return spreadData
      } catch (error) {
        console.error('从后端加载价差数据失败，回退到CSV数据:', error)
        
        // 如果后端失败，回退到CSV数据
        try {
          const rawData = await csvLoader.getRawData(
            state.config.timeRange.start,
            state.config.timeRange.end
          )
          commit('SET_SPREAD_DATA', rawData.spreadData)
          return rawData.spreadData
        } catch (csvError) {
          console.error('CSV数据也加载失败:', csvError)
          commit('SET_SPREAD_DATA', null)
          throw error
        }
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    // 从后端API检测套利信号
    async detectSignals({ commit, state }) {
      commit('SET_LOADING', true)
      try {
        // 调用后端API获取信号数据
        const response = await apiClient.get('/app/getresult', {
          params: {
            start: Math.floor(state.config.timeRange.start / 1000), // 毫秒转秒
            end: Math.floor(state.config.timeRange.end / 1000),
            type: 'signals',
            zThreshold: state.config.detector.zScoreThreshold,
            tradeSize: state.config.detector.volumeMin
          }
        })
        
        // 直接使用后端数据，只进行时间戳转换
        let signals = response.data.map(s => ({
          ...s,
          time: s.time * 1000, // 秒转毫秒
        }))
        
        // 根据前端检测器参数过滤信号
        const { priceThreshold, zScoreThreshold, volumeMin } = state.config.detector
        
        signals = signals.filter(s => {
          return Math.abs(s.spread) >= priceThreshold &&
                 Math.abs(s.zScore) >= zScoreThreshold &&
                 s.size >= volumeMin
        })
        
        console.log(`从后端获取到 ${signals.length} 个套利信号`)
        commit('SET_SIGNALS', signals)
        return signals
      } catch (error) {
        console.error('从后端检测套利信号失败，回退到CSV数据:', error)
        
        // 如果后端失败，回退到CSV数据
        try {
          let signals = await csvLoader.getSignalsInRange(
            state.config.timeRange.start,
            state.config.timeRange.end
          )
          
          // CSV数据使用前端费用计算逻辑
          const { fees } = state.config.detector
          signals = signals.map(s => {
            const cexFee = s.cexPrice * s.size * fees.cex
            const dexFee = s.dexPrice * s.size * fees.dex
            const slippageCost = ((s.cexPrice + s.dexPrice) / 2) * s.size * fees.slippage
            const totalCost = cexFee + dexFee + fees.gas + slippageCost
            const netProfit = s.grossProfit - totalCost
            
            // 动态计算 Z-Score
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
          
          console.log(`从CSV加载 ${signals.length} 个信号`)
          commit('SET_SIGNALS', signals)
          return signals
        } catch (csvError) {
          console.error('CSV数据也加载失败:', csvError)
          commit('SET_SIGNALS', [])
          throw error
        }
      } finally {
        commit('SET_LOADING', false)
      }
    },
    
    updateConfig({ commit }, config) {
      commit('SET_CONFIG', config)
    },
    
    updateDetectorParams({ commit }, params) {
      commit('UPDATE_DETECTOR_PARAMS', params)
    }
  }
})
