# 区块链非原子套利交易识别系统

> 基于 Vue2 的 CEX-DEX 跨平台套利机会识别与分析平台

## 📖 项目简介

本项目是一个专注于**中心化交易所（CEX）与去中心化交易所（DEX）之间非原子套利识别**的 Web 应用。通过分析 Binance（CEX）和 Uniswap V3（DEX）的 USDT/ETH 交易对价格差异，自动识别潜在套利机会，并提供详细的收益分析和回测功能。

**适用对象**：区块链研究者、量化交易工程师、金融科技学习者

## ✨ 核心功能

### 1. 价格对比与可视化

- 📊 **实时价格对比图**：Uniswap V3 vs Binance 价格走势对比
- 🔥 **价差热力图**：按时间分布显示价差 Z-Score
- 🎯 **套利机会雷达图**：多维度评估套利指标（价差幅度、交易频率、潜在利润等）
- 📈 **交易方向饼图**：显示 CEX→DEX 和 DEX→CEX 的套利机会分布

### 2. 智能套利检测

- 🔍 **参数化检测器**：

  - 价差阈值设置
  - Z-Score 统计显著性判断
  - 时间窗口配置
  - 最小成交量过滤
- 💰 **完整费用模型**：

  - CEX 手续费（Binance：0.1%）
  - DEX 手续费（Uniswap V3：0.3%）
  - Gas 费用（以太坊网络）
  - 滑点成本估算
- 📋 **信号列表**：

  - 实时显示所有检测到的套利机会
  - 支持按时间/收益/置信度排序
  - 一键查看详细收益分解

### 3. 策略回测

- 📉 **权益曲线**：展示策略累计收益变化
- 📊 **关键指标**：
  - 总交易次数
  - 胜率
  - 总收益 / 平均收益
  - 夏普比率
  - 最大回撤

### 4. 预设策略

- **保守型**：高阈值、高置信度要求，适合稳健收益
- **平衡型**：中等参数，风险收益平衡（默认）
- **激进型**：低阈值，捕获更多机会，风险较高

### 5. 数据分析

- 价差时间序列分析
- 价差分布统计
- 成交量对比
- 波动率分析

## 🛠️ 技术栈

```
前端框架：Vue 2.6.14
状态管理：Vuex 3.6.2
路由管理：Vue Router 3.5.3
数据可视化：ECharts 5.4.3
样式处理：Sass/SCSS
工具库：Axios, Day.js, Lodash
```

## 📦 安装依赖

### 环境要求

- **Node.js**：14.x 或更高版本
- **npm**：6.x 或更高版本

### 安装步骤

```bash
# 1. 克隆项目（如果从 Git）
git clone <repository-url>
cd Software-Requirements

# 2. 进入前端目录
cd frontend

# 3. 安装依赖
npm install

# 如果安装较慢，可以使用淘宝镜像
npm config set registry https://registry.npmmirror.com
npm install
```

## 🚀 如何使用

### 1. 启动开发服务器

```bash
cd frontend
npm run dev
```

开发服务器将在 `http://localhost:8080` 启动，浏览器会自动打开。

### 2. 功能使用指南

#### 📊 首页 - 市场概览

**路径**：`/overview` 或 `/`

**操作步骤**：

1. **左侧参数面板**：

   - 选择时间范围（最近7天/9月全月）
   - 选择交易对（默认：USDT/ETH）
   - 选择 DEX 池和 CEX 交易所
   - 勾选要显示的图表（雷达图、饼图、热力图）
2. 点击 **"开始分析"** 按钮
3. **查看结果**：

   - 右上方：Uniswap vs Binance 价格对比图
   - 左下方：套利机会雷达图
   - 右下方：交易方向比例饼图
   - 底部：价差热力图
   - 左侧底部：实时统计（检测信号数、平均价差、潜在收益）

#### 🎯 套利识别 - 信号检测

**路径**：`/radar`

**操作步骤**：

1. **配置检测参数**（左侧面板）：

   ```
   价差阈值：0.8 USDT（建议范围：0.5-2.0）
   Z-Score：2.0（建议范围：1.5-3.0）
   最小成交量：1000 USDT
   时间窗口：1-20 秒
   ```
2. **调整费用模型**：

   - CEX 手续费：0.1%
   - DEX 手续费：0.3%
   - Gas 费用：15 USDT
   - 滑点：0.2%
3. 或选择 **预设方案**：

   - 保守型：高阈值、低风险
   - 平衡型：适中参数（推荐）
   - 激进型：低阈值、高机会
4. 点击 **"检测信号"** 按钮
5. **查看信号列表**：

   - 支持按时间/收益/置信度排序
   - 点击任意信号查看详细信息
   - 查看收益分解（毛收益、手续费、Gas、滑点、净收益）
6. **导出数据**：

   - 点击右上角导出按钮
   - 下载 CSV 格式的信号列表

#### 📈 回测分析

**路径**：`/backtest`

**操作步骤**：

1. 页面自动运行回测
2. 查看权益曲线图
3. 查看关键指标：
   - 总交易次数
   - 胜率
   - 总收益
   - 夏普比率

#### 📉 市场对比

**路径**：`/compare`

**功能**：

- 价差时间序列
- 价差分布对比
- 成交量对比
- 波动率分析

### 3. 构建生产版本

```bash
cd frontend
npm run build
```

构建产物将输出到 `frontend/dist` 目录，可以部署到任何静态服务器。

## 📂 项目结构

```
Software-Requirements/
├── frontend/                    # 前端项目
│   ├── public/                  # 静态资源
│   ├── src/
│   │   ├── components/          # 可复用组件
│   │   │   ├── ChartCard.vue    # 图表卡片
│   │   │   ├── DataTable.vue    # 数据表格
│   │   │   └── StatCard.vue     # 统计卡片
│   │   ├── layout/
│   │   │   └── MainLayout.vue   # 主布局（顶部导航）
│   │   ├── views/               # 页面组件
│   │   │   ├── Overview.vue     # 首页
│   │   │   ├── ArbRadar.vue     # 套利雷达
│   │   │   ├── MarketCompare.vue # 市场对比
│   │   │   ├── CaseExplorer.vue  # 案例回放
│   │   │   ├── Backtest.vue      # 回测分析
│   │   │   ├── DataLab.vue       # 数据实验台
│   │   │   ├── Alerts.vue        # 告警中心
│   │   │   └── Report.vue        # 报告生成
│   │   ├── store/
│   │   │   └── index.js         # Vuex 状态管理
│   │   ├── router/
│   │   │   └── index.js         # 路由配置
│   │   ├── utils/
│   │   │   └── mockData.js      # 模拟数据生成器
│   │   ├── styles/
│   │   │   ├── variables.scss   # SCSS 变量
│   │   │   └── global.scss      # 全局样式
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   ├── vue.config.js
│   └── README.md
└── README.md                    # 本文件
```

## 🎨 界面设计

### 配色方案（简洁浅色风格）

```
背景色：#f9fafb（浅灰白）
卡片色：#ffffff（纯白）
文本色：#111827（深黑）
主色调：#3b82f6（蓝色 - Binance）
强调色：#10b981（绿色 - Uniswap）
警告色：#f97316（橙色）
```

### 布局特点

- **左侧参数面板**（3列宽）：集中配置所有参数
- **右侧图表区域**（9列宽）：大型数据可视化展示
- **顶部导航栏**：简洁的横向导航
- **卡片式布局**：清晰的信息分组

## 📊 数据说明

### 当前数据源

本项目使用**智能模拟数据**，基于以下算法生成：

- **价格数据**：布朗运动（Brownian Motion）模拟真实市场波动
- **价差注入**：周期性注入套利机会
- **Z-Score 计算**：基于滑动窗口统计
- **信号识别**：根据检测器参数自动筛选

### 接入真实数据

要接入真实数据，需修改 `frontend/src/store/index.js`：

```javascript
// 示例：接入 Binance API
async loadPriceData({ commit, state }) {
  const cexData = await axios.get('https://api.binance.com/api/v3/klines', {
    params: {
      symbol: 'ETHUSDT',
      interval: '1m',
      startTime: state.config.timeRange.start,
      endTime: state.config.timeRange.end
    }
  })
  
  // 接入 Uniswap V3 数据（使用 The Graph）
  const dexData = await axios.post(
    'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3',
    { query: '...' }
  )
  
  commit('SET_PRICE_DATA', { cex: cexData, dex: dexData })
}
```

**数据源参考**：

- **Binance API**：https://github.com/binance/binance-spot-api-docs
- **Uniswap V3 合约**：0x11b815ef8Bf581194ae79006d24E0d814B7697f6
- **The Graph**：https://thegraph.com/docs/zh/

## 💡 使用技巧

### 参数调优建议

| 策略类型 | 价差阈值 | Z-Score | 最小成交量 | 适用场景                 |
| -------- | -------- | ------- | ---------- | ------------------------ |
| 保守型   | 1.5 USDT | 3.0     | 2000 USDT  | 追求稳定收益，容忍低频率 |
| 平衡型   | 0.8 USDT | 2.0     | 1000 USDT  | 日常套利，风险收益平衡   |
| 激进型   | 0.5 USDT | 1.5     | 500 USDT   | 捕获更多机会，容忍高风险 |

### 指标说明

**价差（Spread）**

```
价差 = CEX价格 - DEX价格
正值：可在 DEX 买入，CEX 卖出
负值：可在 CEX 买入，DEX 卖出
```

**Z-Score**

```
Z-Score = (当前价差 - 均值) / 标准差
|Z| > 2：显著价差，值得关注
|Z| > 3：极端价差，高收益机会
```

**净收益**

```
净收益 = 毛收益 - CEX手续费 - DEX手续费 - Gas费 - 滑点成本
```

## ⚠️ 风险提示

1. **价格延迟**：实际交易存在网络延迟和确认延迟
2. **滑点影响**：大额交易会产生显著滑点
3. **Gas 波动**：以太坊 Gas 费波动大，需实时监控
4. **市场变化**：价差可能在执行过程中消失
5. **仅供学习**：本项目仅用于研究学习，不构成投资建议

## 🔧 常见问题

### Q: 如何修改时间范围？

A: 在首页左侧参数面板的"时间范围"下拉菜单中选择。

### Q: 检测不到信号怎么办？

A: 尝试降低价差阈值和 Z-Score 阈值，或选择"激进型"预设。

### Q: 如何导出数据？

A: 点击图表右上角的导出按钮（↓），或在套利识别页面点击导出按钮下载 CSV。

### Q: 端口 8080 被占用？

A: 修改 `frontend/vue.config.js` 中的 `devServer.port` 为其他端口。

### Q: 依赖安装失败？

A: 尝试清除缓存：

```bash
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

## 📚 学术参考

本项目基于以下研究：

1. **Non-atomic arbitrage in decentralized finance (DeFi)**Heimbach I, et al.研究 DeFi 中的非原子套利机制
2. **Atomic vs Non-Atomic: Measuring CEX-DEX Extracted Value and Searcher Profitability**
   Wu F, et al.
   对比原子与非原子套利的价值提取

建议使用功能分支进行开发：

```bash
git checkout -b feature/your-feature-name
git push origin feature/your-feature-name
```
