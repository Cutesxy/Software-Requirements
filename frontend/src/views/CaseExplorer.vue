<template>
  <div class="case-explorer-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">案例回放 Case Explorer</h1>
        <p class="page-desc">套利事件时间轴与证据链回溯</p>
      </div>
    </div>
    
    <div class="card">
      <div class="card-header">
        <h3>案例列表</h3>
      </div>
      
      <data-table
        :columns="caseColumns"
        :data="cases"
        :clickable="true"
        @row-click="viewCase"
      >
        <template #col-status="{ value }">
          <span class="badge" :class="`badge-${value}`">
            {{ value === 'success' ? '成功' : '失败' }}
          </span>
        </template>
      </data-table>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import DataTable from '@/components/DataTable.vue'

export default {
  name: 'CaseExplorer',
  components: { DataTable },
  
  data() {
    return {
      caseColumns: [
        { key: 'id', label: 'ID', width: '200px' },
        { key: 'time', label: '时间', type: 'time' },
        { key: 'direction', label: '方向' },
        { key: 'profit', label: '收益', type: 'number', decimals: 2 },
        { key: 'status', label: '状态' }
      ]
    }
  },
  
  computed: {
    ...mapState(['signals']),
    
    cases() {
      if (!this.signals) return []
      return this.signals.slice(0, 20).map(s => ({
        id: s.id,
        time: s.time,
        direction: s.direction,
        profit: s.netProfit,
        status: s.netProfit > 0 ? 'success' : 'fail'
      }))
    }
  },
  
  methods: {
    viewCase(c) {
      alert(`查看案例: ${c.id}`)
    }
  }
}
</script>

<style lang="scss" scoped>
.case-explorer-page {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>

