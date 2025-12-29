<template>
  <div class="alerts-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">告警中心 Alerts</h1>
        <p class="page-desc">套利信号告警与通知管理</p>
      </div>
    </div>
    
    <div class="card">
      <div class="card-header">
        <h3>告警规则</h3>
      </div>
      <p style="padding: 40px; text-align: center; color: #9BA5B8;">
        告警配置功能开发中...
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Alerts'
}
</script>

<style lang="scss" scoped>
.alerts-page {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>

