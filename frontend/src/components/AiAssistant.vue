<template>
  <div class="ai-assistant">
    <!-- 浮动按钮 -->
    <button 
      class="ai-assistant-btn"
      @click="toggleDrawer"
      :class="{ 'active': isOpen }"
    >
      <span class="ai-icon">🤖</span>
    </button>

    <!-- Drawer 侧边栏 -->
    <transition name="drawer">
      <div v-if="isOpen" class="drawer-overlay" @click="closeDrawer">
        <div class="drawer-content" @click.stop>
          <!-- 头部 -->
          <div class="drawer-header">
            <div class="header-title">
              <span class="ai-icon-large">🤖</span>
              <div>
                <h3>AI 助手</h3>
                <p class="header-subtitle">用自然语言筛选9月份套利信号数据</p>
              </div>
            </div>
            <button class="close-btn" @click="closeDrawer">✕</button>
          </div>

          <!-- 聊天消息列表 -->
          <div class="messages-container" ref="messagesContainer">
            <div 
              v-for="(msg, index) in messages" 
              :key="index"
              class="message"
              :class="msg.role"
            >
              <div class="message-avatar">
                <span v-if="msg.role === 'user'">👤</span>
                <span v-else>🤖</span>
              </div>
              <div class="message-content">
                <div class="message-text" v-html="formatMessage(msg.content)"></div>
                <div v-if="msg.loading" class="message-loading">
                  <span></span><span></span><span></span>
                </div>
                <!-- 显示筛选结果数据 -->
                <div v-if="msg.filteredData" class="filtered-data">
                  <div class="data-summary">
                    <strong>筛选结果：</strong>共找到 {{ msg.filteredData.length }} 条信号
                  </div>
                  <div class="data-table-container">
                    <table class="data-table">
                      <thead>
                        <tr>
                          <th>时间</th>
                          <th>方向</th>
                          <th>净利润</th>
                          <th>Z-Score</th>
                          <th>价差</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(item, idx) in msg.filteredData.slice(0, 10)" :key="idx">
                          <td>{{ formatTime(item.time) }}</td>
                          <td>{{ item.direction }}</td>
                          <td :class="item.netProfit >= 0 ? 'positive' : 'negative'">
                            {{ item.netProfit?.toFixed(2) || '-' }}
                          </td>
                          <td>{{ item.zScore?.toFixed(2) || '-' }}</td>
                          <td>{{ item.spread?.toFixed(2) || '-' }}</td>
                        </tr>
                      </tbody>
                    </table>
                    <div v-if="msg.filteredData.length > 10" class="data-more">
                      还有 {{ msg.filteredData.length - 10 }} 条数据...
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 输入框 -->
          <div class="input-container">
            <input
              v-model="inputText"
              @keyup.enter="sendMessage"
              placeholder="例如：把净利润>10、Z>2.5、只看 DEX→CEX 的信号筛出来"
              class="message-input"
              :disabled="loading"
            />
            <button 
              class="send-btn"
              @click="sendMessage"
              :disabled="loading || !inputText.trim()"
            >
              {{ loading ? '发送中...' : '发送' }}
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import apiClient from '@/utils/api'

export default {
  name: 'AiAssistant',
  data() {
    return {
      isOpen: false,
      messages: [],
      inputText: '',
      loading: false,
      currentPage: 'overview',
      pageContext: {}
    }
  },
  mounted() {
    // 监听路由变化，更新页面上下文
    this.updatePageContext()
    this.$router.afterEach(() => {
      this.updatePageContext()
    })
  },
  methods: {
    toggleDrawer() {
      this.isOpen = !this.isOpen
      if (this.isOpen) {
        this.updatePageContext()
        // 添加欢迎消息
        if (this.messages.length === 0) {
          this.messages.push({
            role: 'assistant',
            content: '你好！我是 AI 助手。\n\n**示例：**\n- "把净利润>10、Z>2.5、只看 DEX→CEX 的信号筛出来"\n- "筛选净利润大于20的信号"\n- "显示Z-Score大于3的所有信号"'
          })
        }
      }
    },
    closeDrawer() {
      this.isOpen = false
    },
    updatePageContext() {
      // 简化上下文收集，只需要基本信息
      const route = this.$route
      this.currentPage = route.name || 'overview'
      
      this.pageContext = {
        page: this.currentPage,
        route: route.path,
        timestamp: Date.now()
      }
    },
    async sendMessage() {
      if (!this.inputText.trim() || this.loading) return
      
      const userMessage = this.inputText.trim()
      this.inputText = ''
      
      // 添加用户消息
      this.messages.push({
        role: 'user',
        content: userMessage
      })
      
      // 添加加载中的助手消息
      const loadingMsg = {
        role: 'assistant',
        content: '',
        loading: true
      }
      this.messages.push(loadingMsg)
      
      this.loading = true
      this.scrollToBottom()
      
      try {
        // 更新页面上下文
        this.updatePageContext()
        
        // 调用后端 AI API
        const response = await apiClient.chatWithAI({
          message: userMessage,
          context: this.pageContext
        })
        
        // 移除加载消息
        this.messages.pop()
        
        // 添加助手回复
        const assistantMsg = {
          role: 'assistant',
          content: response.content || response.message || '抱歉，我无法理解您的问题。',
          filteredData: response.filteredData || null
        }
        this.messages.push(assistantMsg)
        
      } catch (error) {
        console.error('AI 助手错误:', error)
        this.messages.pop()
        this.messages.push({
          role: 'assistant',
          content: `❌ 抱歉，发生了错误：${error.message || '网络请求失败'}`
        })
      } finally {
        this.loading = false
        this.scrollToBottom()
      }
    },
    formatTime(timestamp) {
      if (!timestamp) return '-'
      const timeMs = (timestamp || 0) * 1000
      return new Date(timeMs).toLocaleString('zh-CN')
    },
    formatMessage(content) {
      // 简单的 Markdown 格式化
      if (!content) return ''
      
      return content
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>')
        .replace(/`(.+?)`/g, '<code>$1</code>')
    },
    formatTime(timestamp) {
      if (!timestamp) return '-'
      const timeMs = (timestamp || 0) * 1000
      return new Date(timeMs).toLocaleString('zh-CN')
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.ai-assistant {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1000;
}

.ai-assistant-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: linear-gradient(135deg, $color-primary 0%, $color-accent 100%);
  color: white;
  border: none;
  border-radius: 28px;
  box-shadow: $shadow-lg;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all $transition-normal;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 20px -3px rgba(59, 130, 246, 0.3);
  }
  
  &.active {
    background: linear-gradient(135deg, $color-accent 0%, $color-primary 100%);
  }
  
  .ai-icon {
    font-size: 20px;
  }
}

.drawer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1001;
  display: flex;
  justify-content: flex-end;
}

.drawer-content {
  width: 480px;
  max-width: 90vw;
  height: 100vh;
  background: $bg-card;
  display: flex;
  flex-direction: column;
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.1);
}

.drawer-header {
  padding: 20px;
  border-bottom: 1px solid $border-color;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  
  .header-title {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    
    .ai-icon-large {
      font-size: 32px;
    }
    
    h3 {
      margin: 0 0 4px 0;
      font-size: 18px;
      font-weight: 700;
      color: $text-primary;
    }
    
    .header-subtitle {
      margin: 0;
      font-size: 12px;
      color: $text-secondary;
    }
  }
  
  .close-btn {
    background: none;
    border: none;
    font-size: 24px;
    color: $text-secondary;
    cursor: pointer;
    padding: 0;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    transition: all $transition-fast;
    
    &:hover {
      background: $bg-card-hover;
      color: $text-primary;
    }
  }
}


.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message {
  display: flex;
  gap: 12px;
  
  &.user {
    flex-direction: row-reverse;
    
    .message-content {
      background: $color-primary;
      color: white;
      border-radius: 16px 16px 4px 16px;
    }
  }
  
  &.assistant {
    .message-content {
      background: $bg-secondary;
      color: $text-primary;
      border-radius: 16px 16px 16px 4px;
    }
  }
}

.message-avatar {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.message-content {
  max-width: 75%;
  padding: 12px 16px;
  line-height: 1.5;
  font-size: 14px;
  
  .message-text {
    word-wrap: break-word;
    
    ::v-deep strong {
      font-weight: 600;
    }
    
    ::v-deep code {
      background: rgba(0, 0, 0, 0.1);
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 12px;
      font-family: 'Courier New', monospace;
    }
  }
}

.message-loading {
  display: flex;
  gap: 4px;
  padding: 8px 0;
  
  span {
    width: 6px;
    height: 6px;
    background: currentColor;
    border-radius: 50%;
    animation: bounce 1.4s infinite ease-in-out;
    
    &:nth-child(1) {
      animation-delay: -0.32s;
    }
    
    &:nth-child(2) {
      animation-delay: -0.16s;
    }
  }
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.function-call-badge {
  margin-top: 8px;
  padding: 4px 8px;
  background: rgba(139, 92, 246, 0.1);
  color: $color-accent;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
}

.filtered-data {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid $border-color;
}

.data-summary {
  margin-bottom: 12px;
  font-size: 14px;
  color: $text-primary;
}

.data-table-container {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid $border-color;
  border-radius: 8px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  
  thead {
    background: $bg-card-hover;
    position: sticky;
    top: 0;
    z-index: 1;
    
    th {
      padding: 8px 12px;
      text-align: left;
      font-weight: 600;
      color: $text-secondary;
      border-bottom: 1px solid $border-color;
    }
  }
  
  tbody {
    tr {
      border-bottom: 1px solid $border-color;
      transition: background $transition-fast;
      
      &:hover {
        background: $bg-card-hover;
      }
      
      &:last-child {
        border-bottom: none;
      }
    }
    
    td {
      padding: 8px 12px;
      color: $text-primary;
      
      &.positive {
        color: $color-success;
        font-weight: 600;
      }
      
      &.negative {
        color: $color-danger;
        font-weight: 600;
      }
    }
  }
}

.data-more {
  padding: 8px 12px;
  text-align: center;
  color: $text-secondary;
  font-size: 12px;
  background: $bg-card-hover;
}

.input-container {
  padding: 16px 20px;
  border-top: 1px solid $border-color;
  display: flex;
  gap: 8px;
}

.message-input {
  flex: 1;
  padding: 10px 16px;
  border: 1px solid $border-color;
  border-radius: 20px;
  font-size: 14px;
  outline: none;
  transition: all $transition-fast;
  
  &:focus {
    border-color: $color-primary;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
  
  &:disabled {
    background: $bg-card-hover;
    cursor: not-allowed;
  }
}

.send-btn {
  padding: 10px 20px;
  background: $color-primary;
  color: white;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all $transition-fast;
  
  &:hover:not(:disabled) {
    background: darken($color-primary, 10%);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

// Drawer 动画
.drawer-enter-active,
.drawer-leave-active {
  transition: opacity $transition-normal;
  
  .drawer-content {
    transition: transform $transition-normal;
  }
}

.drawer-enter,
.drawer-leave-to {
  opacity: 0;
  
  .drawer-content {
    transform: translateX(100%);
  }
}
</style>

