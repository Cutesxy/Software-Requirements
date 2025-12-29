<template>
  <div class="main-layout">
    <!-- 顶部导航栏 -->
    <header class="layout-header">
      <div class="header-content">
        <h1 class="logo">区块链非原子套利交易识别</h1>
        <nav class="nav-menu">
          <router-link to="/overview" class="nav-link">首页</router-link>
          <router-link to="/compare" class="nav-link">数据分析</router-link>
          <router-link to="/radar" class="nav-link">套利识别</router-link>
          <router-link to="/backtest" class="nav-link">回测分析</router-link>
          <router-link to="/lab" class="nav-link">文档</router-link>
        </nav>
      </div>
    </header>
    
    <!-- 主内容区 -->
    <main class="layout-content">
      <transition name="fade" mode="out-in">
        <router-view />
      </transition>
    </main>

    <!-- AI 助手 -->
    <ai-assistant />
  </div>
</template>

<script>
import AiAssistant from '@/components/AiAssistant.vue'

export default {
  name: 'MainLayout',
  components: {
    AiAssistant
  }
}
</script>

<style lang="scss" scoped>
.main-layout {
  min-height: 100vh;
  background: $bg-primary;
}

.layout-header {
  background: $bg-secondary;
  border-bottom: 1px solid $border-color;
  box-shadow: $shadow-sm;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1920px;
  margin: 0 auto;
  padding: 0 32px;
  height: 64px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 20px;
  font-weight: 700;
  color: $text-primary;
  margin: 0;
}

.nav-menu {
  display: flex;
  gap: 24px;
}

.nav-link {
  color: $text-secondary;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  padding: 8px 0;
  border-bottom: 2px solid transparent;
  transition: all $transition-fast;
  
  &:hover {
    color: $color-primary;
  }
  
  &.router-link-active {
    color: $color-primary;
    border-bottom-color: $color-primary;
  }
}

.layout-content {
  max-width: 1920px;
  margin: 0 auto;
  padding: 32px;
}

// 路由过渡动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter,
.fade-leave-to {
  opacity: 0;
}
</style>
