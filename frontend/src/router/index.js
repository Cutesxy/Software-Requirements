import Vue from 'vue'
import VueRouter from 'vue-router'
import Layout from '@/layout/MainLayout.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/overview',
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

export default router

