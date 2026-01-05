<template>
  <div class="documentation-page">
    <!-- 顶部横幅 -->
    <div class="hero-banner">
      <div class="hero-content">
        <div class="hero-icon">🔍</div>
        <h1 class="hero-title">区块链非原子套利交易识别系统</h1>
        <p class="hero-subtitle">Blockchain Non-Atomic Arbitrage Detection Platform</p>
        <div class="hero-badges">
          <span class="badge-item">实时监控</span>
          <span class="badge-item">智能分析</span>
          <span class="badge-item">精准识别</span>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="doc-container">
      <!-- 快速导航 -->
      <aside class="doc-nav">
        <div class="nav-section">
          <h4>快速导航</h4>
          <ul>
            <li><a href="#overview" @click.prevent="scrollTo('overview')">📖 系统概述</a></li>
            <li><a href="#features" @click.prevent="scrollTo('features')">✨ 核心功能</a></li>
            <li><a href="#architecture" @click.prevent="scrollTo('architecture')">🏗️ 系统架构</a></li>
            <li><a href="#usage" @click.prevent="scrollTo('usage')">🚀 使用指南</a></li>
            <li><a href="#tech" @click.prevent="scrollTo('tech')">🛠️ 技术栈</a></li>
            <li><a href="#api" @click.prevent="scrollTo('api')">🔌 API 接口</a></li>
          </ul>
        </div>
      </aside>

      <!-- 文档内容 -->
      <main class="doc-content">
        <!-- 系统概述 -->
        <section id="overview" class="doc-section">
          <h2>📖 系统概述</h2>
          <div class="content-card">
            <p>
              本系统是一个专注于区块链非原子套利交易识别的综合分析平台。通过监控中心化交易所(CEX)和去中心化交易所(DEX)之间的价格差异，系统能够智能识别潜在的套利机会，并提供全方位的数据分析、可视化和 AI 驱动的智能分析支持。
            </p>
            <div class="highlight-box">
              <h4>💡 核心价值</h4>
              <ul>
                <li><strong>智能识别</strong>：基于价差阈值、Z-Score、成交量等多维度指标的套利机会检测</li>
                <li><strong>数据可视化</strong>：丰富的交互式图表展示与趋势分析</li>
                <li><strong>AI 分析助手</strong>：基于大语言模型的自然语言交互和智能数据筛选</li>
                <li><strong>回测验证</strong>：历史数据回测，评估策略有效性和收益潜力</li>
                <li><strong>灵活配置</strong>：支持预设方案和自定义参数，满足不同分析需求</li>
              </ul>
            </div>
          </div>
        </section>

        <!-- 核心功能 -->
        <section id="features" class="doc-section">
          <h2>✨ 核心功能</h2>
          
          <div class="features-grid">
            <div class="feature-card">
              <div class="feature-icon">📊</div>
              <h3>数据分析中心</h3>
              <p>全面的数据分析页面，支持多维度数据探索和 AI 智能总结。</p>
              <ul>
                <li>价格对比与价差趋势</li>
                <li>信号时间分布折线图</li>
                <li>可配置价差分布（去极值、对数坐标）</li>
                <li>信号明细表与钻取分析</li>
                <li>AI 自动生成分析总结</li>
              </ul>
            </div>

            <div class="feature-card">
              <div class="feature-icon">🎯</div>
              <h3>套利机会识别</h3>
              <p>基于价差阈值、Z-Score、成交量等多维度指标，智能识别并筛选优质套利机会。</p>
              <ul>
                <li>实时信号检测</li>
                <li>预设方案（激进型/平衡型/保守型）</li>
                <li>信号空间分布可视化</li>
                <li>参数实时调整与响应</li>
              </ul>
            </div>

            <div class="feature-card">
              <div class="feature-icon">📈</div>
              <h3>多维度可视化</h3>
              <p>提供丰富的图表类型，全方位展示市场数据和分析结果。</p>
              <ul>
                <li>折线图、柱状图</li>
                <li>散点图、饼图</li>
                <li>交互式图表</li>
                <li>图表联动与筛选</li>
              </ul>
            </div>

            <div class="feature-card">
              <div class="feature-icon">🔬</div>
              <h3>回测分析</h3>
              <p>历史数据回测功能，评估策略有效性和收益潜力。</p>
              <ul>
                <li>历史数据回放</li>
                <li>策略模拟</li>
                <li>收益计算与统计</li>
                <li>权益曲线可视化</li>
              </ul>
            </div>

            <div class="feature-card">
              <div class="feature-icon">🤖</div>
              <h3>AI 分析助手</h3>
              <p>基于大语言模型的智能分析助手，支持自然语言交互和信号筛选。</p>
              <ul>
                <li>自然语言信号筛选</li>
                <li>智能数据查询</li>
                <li>结构化数据输出</li>
              </ul>
            </div>

            <div class="feature-card">
              <div class="feature-icon">📊</div>
              <h3>高级数据分析</h3>
              <p>多维度数据分析，包含 AI 总结、信号明细表和可配置的可视化。</p>
              <ul>
                <li>AI 自动总结</li>
                <li>信号明细表与钻取</li>
                <li>可配置价差分布</li>
              </ul>
            </div>

            <div class="feature-card">
              <div class="feature-icon">⚙️</div>
              <h3>灵活配置</h3>
              <p>丰富的参数配置选项，满足不同场景的分析需求。</p>
              <ul>
                <li>检测器参数调整</li>
                <li>时间范围设置</li>
                <li>预设方案快速切换</li>
              </ul>
            </div>
          </div>
        </section>

        <!-- 系统架构 -->
        <section id="architecture" class="doc-section">
          <h2>🏗️ 系统架构</h2>
          <div class="content-card">
            <div class="architecture-diagram">
              <div class="arch-layer">
                <div class="layer-title">展示层</div>
                <div class="layer-content">
                  <span class="arch-component">Vue.js 前端</span>
                  <span class="arch-component">ECharts 可视化</span>
                  <span class="arch-component">Vuex 状态管理</span>
                </div>
              </div>

              <div class="arch-arrow">↓</div>

              <div class="arch-layer">
                <div class="layer-title">业务层</div>
                <div class="layer-content">
                  <span class="arch-component">数据分析引擎</span>
                  <span class="arch-component">套利检测器</span>
                  <span class="arch-component">回测系统</span>
                  <span class="arch-component">AI 服务 (DeepSeek)</span>
                </div>
              </div>

              <div class="arch-arrow">↓</div>

              <div class="arch-layer">
                <div class="layer-title">数据层</div>
                <div class="layer-content">
                  <span class="arch-component">CSV 数据文件</span>
                  <span class="arch-component">价格数据源</span>
                  <span class="arch-component">交易数据</span>
                  <span class="arch-component">历史记录</span>
                </div>
              </div>
            </div>

            <div class="tech-note">
              <strong>📌 技术亮点：</strong>
              <ul>
                <li>组件化设计，模块解耦，易于维护和扩展</li>
                <li>响应式数据流，实时更新，用户体验流畅</li>
                <li>数据驱动的可视化，图表自动适应数据变化</li>
              </ul>
            </div>
          </div>
        </section>

        <!-- 使用指南 -->
        <section id="usage" class="doc-section">
          <h2>🚀 使用指南</h2>
          
          <div class="usage-steps">
            <div class="step-card">
              <div class="step-number">1</div>
              <div class="step-content">
                <h4>选择分析参数</h4>
                <p>在首页设置时间范围、交易对、DEX池等基本参数。支持预设时间段和自定义日历选择。</p>
              </div>
            </div>

            <div class="step-card">
              <div class="step-number">2</div>
              <div class="step-content">
                <h4>查看实时数据</h4>
                <p>通过价格对比图、价差分布等图表，实时监控市场动态和价格波动。</p>
              </div>
            </div>

            <div class="step-card">
              <div class="step-number">3</div>
              <div class="step-content">
                <h4>套利机会识别</h4>
                <p>进入"套利识别"模块，调整检测参数，系统自动识别潜在套利机会。</p>
              </div>
            </div>

            <div class="step-card">
              <div class="step-number">4</div>
              <div class="step-content">
                <h4>数据分析</h4>
                <p>在"数据分析"页面查看详细的统计报告、AI 自动总结、信号明细表和可配置的可视化图表。点击"生成 AI 总结"获取智能分析建议。</p>
              </div>
            </div>

            <div class="step-card">
              <div class="step-number">5</div>
              <div class="step-content">
                <h4>回测验证</h4>
                <p>使用历史数据进行策略回测，评估收益潜力和风险水平。查看回测统计、权益曲线和交易明细。</p>
              </div>
            </div>

            <div class="step-card">
              <div class="step-number">6</div>
              <div class="step-content">
                <h4>AI 助手交互</h4>
                <p>使用右下角的 AI 分析助手，通过自然语言查询和筛选信号。例如："把净利润>10、Z>2.5、只看 DEX→CEX 的信号筛出来"。</p>
              </div>
            </div>
          </div>
        </section>

        <!-- 技术栈 -->
        <section id="tech" class="doc-section">
          <h2>🛠️ 技术栈</h2>
          
          <div class="tech-stack">
            <div class="tech-category">
              <h4>前端框架</h4>
              <div class="tech-tags">
                <span class="tech-tag">Vue.js 2.6</span>
                <span class="tech-tag">Vue Router</span>
                <span class="tech-tag">Vuex</span>
              </div>
            </div>

            <div class="tech-category">
              <h4>后端框架</h4>
              <div class="tech-tags">
                <span class="tech-tag">Flask</span>
                <span class="tech-tag">Flask-CORS</span>
                <span class="tech-tag">Pandas</span>
              </div>
            </div>

            <div class="tech-category">
              <h4>数据可视化</h4>
              <div class="tech-tags">
                <span class="tech-tag">ECharts 5.4</span>
                <span class="tech-tag">自定义图表</span>
                <span class="tech-tag">交互式图表</span>
              </div>
            </div>

            <div class="tech-category">
              <h4>AI 服务</h4>
              <div class="tech-tags">
                <span class="tech-tag">DeepSeek API</span>
                <span class="tech-tag">Function Calling</span>
                <span class="tech-tag">自然语言处理</span>
              </div>
            </div>

            <div class="tech-category">
              <h4>样式方案</h4>
              <div class="tech-tags">
                <span class="tech-tag">SCSS</span>
                <span class="tech-tag">响应式设计</span>
                <span class="tech-tag">CSS Grid</span>
              </div>
            </div>

            <div class="tech-category">
              <h4>工具库</h4>
              <div class="tech-tags">
                <span class="tech-tag">Axios</span>
                <span class="tech-tag">Day.js</span>
                <span class="tech-tag">Lodash</span>
              </div>
            </div>
          </div>
        </section>

        <!-- API 接口 -->
        <section id="api" class="doc-section">
          <h2>🔌 API 接口</h2>
          
          <div class="api-docs">
            <div class="api-endpoint">
              <div class="endpoint-header">
                <span class="method get">GET</span>
                <code class="endpoint-path">/app/getdata</code>
              </div>
              <p class="endpoint-desc">获取图表可视化数据</p>
              <div class="endpoint-params">
                <strong>参数：</strong>
                <ul>
                  <li><code>type</code>: price | spread | heatmap | correlation</li>
                  <li><code>start</code>: 开始时间戳（秒）</li>
                  <li><code>end</code>: 结束时间戳（秒）</li>
                  <li><code>interval</code>: 时间间隔（如 15m）</li>
                </ul>
              </div>
            </div>

            <div class="api-endpoint">
              <div class="endpoint-header">
                <span class="method get">GET</span>
                <code class="endpoint-path">/app/getresult</code>
              </div>
              <p class="endpoint-desc">获取回测结果或信号数据</p>
              <div class="endpoint-params">
                <strong>参数：</strong>
                <ul>
                  <li><code>type</code>: backtest | signals</li>
                  <li><code>start</code>: 开始时间戳（秒）</li>
                  <li><code>end</code>: 结束时间戳（秒）</li>
                  <li><code>zThreshold</code>: Z-Score 阈值（默认 2.0）</li>
                  <li><code>tradeSize</code>: 交易规模 USDT（默认 10000）</li>
                </ul>
              </div>
            </div>

            <div class="api-endpoint">
              <div class="endpoint-header">
                <span class="method post">POST</span>
                <code class="endpoint-path">/app/ai/chat</code>
              </div>
              <p class="endpoint-desc">AI 分析助手聊天接口</p>
              <div class="endpoint-params">
                <strong>请求体：</strong>
                <pre class="code-block">{
  "message": "用户消息",
  "context": {
    "page": "当前页面",
    "params": { "参数对象" }
  }
}</pre>
                <strong>响应：</strong>
                <pre class="code-block">{
  "content": "AI 回复内容",
  "functionCall": { "函数调用结果（如有）" }
}</pre>
              </div>
            </div>
          </div>
        </section>

        
      </main>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DataLab',

  methods: {
    scrollTo(id) {
      const element = document.getElementById(id)
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.documentation-page {
  min-height: 100vh;
  background: $bg-primary;
}

// 顶部横幅
.hero-banner {
  background: linear-gradient(135deg, $color-primary 0%, $color-accent 100%);
  color: white;
  padding: 80px 24px;
  text-align: center;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.hero-icon {
  font-size: 72px;
  margin-bottom: 24px;
  animation: float 3s ease-in-out infinite;
}

.hero-title {
  font-size: 42px;
  font-weight: 700;
  margin: 0 0 16px 0;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.hero-subtitle {
  font-size: 18px;
  margin: 0 0 32px 0;
  opacity: 0.95;
}

.hero-badges {
  display: flex;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.badge-item {
  padding: 8px 20px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

// 文档容器
.doc-container {
  max-width: 1200px;
  margin: -40px auto 0;
  padding: 0 24px 80px;
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 40px;

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
}

// 侧边导航
.doc-nav {
  position: sticky;
  top: 24px;
  height: fit-content;

  @media (max-width: 1024px) {
    position: relative;
    top: 0;
  }
}

.nav-section {
  background: $bg-card;
  border-radius: 12px;
  padding: 24px;
  box-shadow: $shadow-sm;
  border: 1px solid $border-color;

  h4 {
    font-size: 14px;
    font-weight: 600;
    color: $text-primary;
    margin: 0 0 16px 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  ul {
    list-style: none;
    padding: 0;
    margin: 0;

    li {
      margin-bottom: 8px;

      &:last-child {
        margin-bottom: 0;
      }

      a {
        display: block;
        padding: 8px 12px;
        color: $text-secondary;
        text-decoration: none;
        border-radius: 6px;
        transition: all $transition-fast;
        font-size: 14px;

        &:hover {
          background: rgba($color-primary, 0.05);
          color: $color-primary;
          transform: translateX(4px);
        }
      }
    }
  }
}

// 文档内容
.doc-content {
  background: $bg-card;
  border-radius: 12px;
  padding: 40px;
  box-shadow: $shadow-sm;
  border: 1px solid $border-color;

  @media (max-width: 768px) {
    padding: 24px;
  }
}

.doc-section {
  margin-bottom: 60px;

  &:last-child {
    margin-bottom: 0;
  }

  h2 {
    font-size: 32px;
    font-weight: 700;
    color: $text-primary;
    margin: 0 0 24px 0;
    padding-bottom: 16px;
    border-bottom: 2px solid $border-color;
  }

  h3 {
    font-size: 20px;
    font-weight: 600;
    color: $text-primary;
    margin: 0 0 16px 0;
  }

  h4 {
    font-size: 16px;
    font-weight: 600;
    color: $text-primary;
    margin: 0 0 12px 0;
  }

  p {
    font-size: 15px;
    line-height: 1.8;
    color: $text-secondary;
    margin: 0 0 16px 0;
  }

  ul {
    padding-left: 24px;
    margin: 0 0 16px 0;

    li {
      font-size: 15px;
      line-height: 1.8;
      color: $text-secondary;
      margin-bottom: 8px;
    }
  }
}

.content-card {
  background: $bg-primary;
  border-radius: 8px;
  padding: 24px;
  border: 1px solid $border-color;
}

.highlight-box {
  background: rgba($color-primary, 0.05);
  border-left: 4px solid $color-primary;
  padding: 20px;
  border-radius: 0 8px 8px 0;
  margin-top: 24px;

  h4 {
    color: $color-primary;
    margin: 0 0 16px 0;
  }

  ul {
    margin: 0;

    li {
      margin-bottom: 12px;

      &:last-child {
        margin-bottom: 0;
      }

      strong {
        color: $text-primary;
      }
    }
  }
}

// 功能网格
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 24px;
}

.feature-card {
  background: $bg-primary;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid $border-color;
  transition: all $transition-fast;

  &:hover {
    box-shadow: $shadow-md;
    transform: translateY(-4px);
    border-color: $color-primary;
  }

  .feature-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }

  h3 {
    font-size: 18px;
    font-weight: 600;
    color: $text-primary;
    margin: 0 0 12px 0;
  }

  p {
    font-size: 14px;
    color: $text-secondary;
    margin: 0 0 16px 0;
  }

  ul {
    padding-left: 20px;
    margin: 0;

    li {
      font-size: 13px;
      color: $text-tertiary;
      margin-bottom: 6px;

      &:last-child {
        margin-bottom: 0;
      }
    }
  }
}

// 架构图
.architecture-diagram {
  margin: 32px 0;
}

.arch-layer {
  background: $bg-primary;
  border: 2px solid $border-color;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 16px;

  .layer-title {
    background: linear-gradient(135deg, $color-primary 0%, $color-accent 100%);
    color: white;
    padding: 12px 20px;
    font-weight: 600;
    text-align: center;
  }

  .layer-content {
    padding: 20px;
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    justify-content: center;
  }
}

.arch-component {
  padding: 8px 16px;
  background: white;
  border: 1px solid $border-color;
  border-radius: 6px;
  font-size: 13px;
  color: $text-primary;
}

.arch-arrow {
  text-align: center;
  font-size: 24px;
  color: $color-primary;
  margin: 8px 0;
}

.tech-note {
  background: rgba($color-success, 0.05);
  border-left: 4px solid $color-success;
  padding: 20px;
  border-radius: 0 8px 8px 0;
  margin-top: 24px;

  strong {
    color: $color-success;
  }

  ul {
    margin: 12px 0 0 0;
  }
}

// 使用步骤
.usage-steps {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.step-card {
  background: $bg-primary;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid $border-color;
  display: flex;
  gap: 20px;
  align-items: flex-start;
  transition: all $transition-fast;

  &:hover {
    box-shadow: $shadow-md;
    border-color: $color-primary;
  }
}

.step-number {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, $color-primary 0%, $color-accent 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
  flex-shrink: 0;
}

.step-content {
  flex: 1;

  h4 {
    font-size: 18px;
    font-weight: 600;
    color: $text-primary;
    margin: 0 0 8px 0;
  }

  p {
    font-size: 14px;
    color: $text-secondary;
    margin: 0;
  }
}

// 技术栈
.tech-stack {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
}

.tech-category {
  background: $bg-primary;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid $border-color;

  h4 {
    font-size: 16px;
    font-weight: 600;
    color: $text-primary;
    margin: 0 0 16px 0;
  }
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tech-tag {
  padding: 6px 14px;
  background: rgba($color-primary, 0.1);
  color: $color-primary;
  border-radius: 16px;
  font-size: 13px;
  font-weight: 500;
}

// 支持卡片
.support-card {
  background: linear-gradient(135deg, rgba($color-primary, 0.05) 0%, rgba($color-accent, 0.05) 100%);
  border-radius: 12px;
  padding: 32px;
  text-align: center;
  border: 1px solid $border-color;

  h3 {
    color: $text-primary;
    margin: 0 0 16px 0;
  }

  p {
    color: $text-secondary;
    margin: 0 0 24px 0;
  }
}

.support-links {
  display: flex;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.support-link {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px 32px;
  background: white;
  border: 1px solid $border-color;
  border-radius: 12px;
  text-decoration: none;
  color: $text-primary;
  transition: all $transition-fast;

  &:hover {
    border-color: $color-primary;
    box-shadow: $shadow-md;
    transform: translateY(-2px);
  }

  span:first-child {
    font-size: 32px;
  }

  span:last-child {
    font-size: 14px;
    font-weight: 500;
  }
}

// API 文档样式
.api-docs {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.api-endpoint {
  background: $bg-primary;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid $border-color;
  transition: all $transition-fast;

  &:hover {
    box-shadow: $shadow-md;
    border-color: $color-primary;
  }
}

.endpoint-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.method {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;

  &.get {
    background: rgba($color-success, 0.1);
    color: $color-success;
  }

  &.post {
    background: rgba($color-primary, 0.1);
    color: $color-primary;
  }
}

.endpoint-path {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  color: $text-primary;
  background: rgba($text-primary, 0.05);
  padding: 4px 8px;
  border-radius: 4px;
}

.endpoint-desc {
  color: $text-secondary;
  margin: 0 0 16px 0;
  font-size: 14px;
}

.endpoint-params {
  strong {
    color: $text-primary;
    font-size: 14px;
    display: block;
    margin-bottom: 8px;
  }

  ul {
    margin: 8px 0 0 0;
    padding-left: 24px;

    li {
      font-size: 13px;
      color: $text-secondary;
      margin-bottom: 6px;
      line-height: 1.6;

      code {
        background: rgba($color-primary, 0.1);
        color: $color-primary;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 12px;
      }
    }
  }
}

.code-block {
  background: rgba($text-primary, 0.05);
  border: 1px solid $border-color;
  border-radius: 6px;
  padding: 16px;
  margin: 12px 0;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: $text-primary;
  overflow-x: auto;
  line-height: 1.6;
  white-space: pre;
}

// 动画
@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}
</style>
