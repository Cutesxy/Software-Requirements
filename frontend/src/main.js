import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import './styles/global.scss'

Vue.config.productionTip = false

// 全局过滤器
Vue.filter('formatNumber', function(value, decimals = 2) {
  if (!value && value !== 0) return '-'
  return Number(value).toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  })
})

Vue.filter('formatPercent', function(value, decimals = 2) {
  if (!value && value !== 0) return '-'
  return (value * 100).toFixed(decimals) + '%'
})

Vue.filter('formatTime', function(timestamp, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
})

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')

