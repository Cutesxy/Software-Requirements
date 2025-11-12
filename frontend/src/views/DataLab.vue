<template>
  <div class="data-lab-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">数据实验台 Data Lab</h1>
        <p class="page-desc">数据查询、质量检测与导出</p>
      </div>
    </div>
    
    <div class="card">
      <div class="card-header">
        <h3>数据预览</h3>
      </div>
      <p style="padding: 40px; text-align: center; color: #9BA5B8;">
        数据查询与导出功能开发中...
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DataLab'
}
</script>

<style lang="scss" scoped>
.data-lab-page {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>

