import Vue from 'vue'
import VueRouter from 'vue-router'
import Layout from '@/layout/MainLayout.vue'
import store from '@/store'

Vue.use(VueRouter)

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/overview',
    meta: { requiresAuth: true },
    children: [
      {
        path: '/overview',
        name: 'Overview',
        component: () => import('@/views/Overview.vue'),
        meta: { title: '总览', icon: 'dashboard' }
      },
      {
        path: '/compare',
        name: 'Compare',
        component: () => import('@/views/MarketCompare.vue'),
        meta: { title: '市场对比', icon: 'compare' }
      },
      {
        path: '/radar',
        name: 'Radar',
        component: () => import('@/views/ArbRadar.vue'),
        meta: { title: '套利雷达', icon: 'radar' }
      },
      {
        path: '/case',
        name: 'Case',
        component: () => import('@/views/CaseExplorer.vue'),
        meta: { title: '案例回放', icon: 'case' }
      },
      {
        path: '/backtest',
        name: 'Backtest',
        component: () => import('@/views/Backtest.vue'),
        meta: { title: '回测分析', icon: 'backtest' }
      },
      {
        path: '/lab',
        name: 'Lab',
        component: () => import('@/views/DataLab.vue'),
        meta: { title: '数据实验台', icon: 'lab' }
      },
      {
        path: '/alerts',
        name: 'Alerts',
        component: () => import('@/views/Alerts.vue'),
        meta: { title: '告警中心', icon: 'alerts' }
      },
      {
        path: '/report',
        name: 'Report',
        component: () => import('@/views/Report.vue'),
        meta: { title: '报告生成', icon: 'report' }
      }
    ]
  }
]

const router = new VueRouter({
  mode: 'hash',
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  // 检查是否需要认证
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 检查登录状态
    const isLoggedIn = store.getters.isLoggedIn
    
    if (!isLoggedIn) {
      // 尝试从服务器检查登录状态
      try {
        await store.dispatch('checkAuth')
        const stillNotLoggedIn = !store.getters.isLoggedIn
        
        if (stillNotLoggedIn) {
          // 未登录，跳转到登录页
          next({
            path: '/login',
            query: { redirect: to.fullPath }
          })
          return
        }
      } catch (error) {
        console.error('Auth check failed:', error)
        next({
          path: '/login',
          query: { redirect: to.fullPath }
        })
        return
      }
    }
  }
  
  // 如果已登录且访问登录页，重定向到首页
  if (to.path === '/login' && store.getters.isLoggedIn) {
    next('/overview')
    return
  }
  
  next()
})

export default router

