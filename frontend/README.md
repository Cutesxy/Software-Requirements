# 区块链非原子套利交易识别系统 - 前端

> 一个专注于 CEX（中心化交易所）与 DEX（去中心化交易所）之间非原子套利机会识别的专业 Web 分析平台

[![Vue](https://img.shields.io/badge/Vue-2.6.14-4FC08D?logo=vue.js)](https://vuejs.org/)
[![ECharts](https://img.shields.io/badge/ECharts-5.4.3-AA344D?logo=apache-echarts)](https://echarts.apache.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## 📋 项目概述

本系统是一个专注于**区块链非原子套利交易识别**的综合分析平台。通过实时监控中心化交易所（Binance）和去中心化交易所（Uniswap V3）之间的价格差异，系统能够智能识别潜在的套利机会，并提供全方位的数据分析和可视化支持。

### 核心价值

- 🔍 **实时监控**：毫秒级价格数据采集与分析
- 🎯 **智能识别**：基于多维度指标的套利机会检测
- 📊 **数据可视化**：直观的图表展示与趋势分析
- 💰 **风险评估**：综合考虑交易成本与市场波动

## ✨ 核心功能

### 1. Overview（概览页）
- ✅ **时间范围选择**：支持全月、上半月、下半月、自定义日历选择（2025年9月）
- ✅ **参数配置**：交易对（ETH/USDT）、DEX池（Uniswap V3 不同费率）、CEX交易所（Binance 不同手续费等级）
- ✅ **多维度图表**：
  - 📈 价格对比图：Uniswap vs Binance 价格走势对比
  - 🎯 雷达图：套利机会多维度指标
  - 🥧 饼图：交易方向比例
  - 🔥 热力图：价差在不同时间段的Z-Score分布
  - 📊 成交量对比：CEX与DEX成交量柱状图
  - 📉 价差分布：价差频率直方图
  - 🔗 价格相关性：CEX与DEX价格散点图
- ✅ **实时统计面板**：检测信号数、平均价差、潜在收益

### 2. ArbRadar（套利雷达）
- ✅ **检测器配置**：价差阈值、Z-Score阈值、最小成交量、时间窗口、费用设置
- ✅ **预设方案**：保守型、平衡型、激进型三种策略模板
- ✅ **信号列表**：支持按时间/收益/置信度排序
- ✅ **信号空间分布图**：散点图展示信号在时间-价差维度的分布
- ✅ **信号详情弹窗**：查看单个信号的详细信息和收益分解
- ✅ **导出功能**：支持导出信号为CSV文件

### 3. Backtest（回测分析）
- ✅ **统计指标**：总交易次数、胜率、总收益、夏普比率
- ✅ **权益曲线图**：展示回测期间的权益变化走势
- ✅ **一键回测**：基于设定参数运行回测模拟

### 4. MarketCompare（市场对比/数据分析）
- ✅ **数据操作**：导入数据（文件/API/示例数据）、导出数据、清空数据
- ✅ **数据质量检测**：完整性、准确性、连续性三维度评估
- ✅ **概览卡片**：平均价差、潜在机会、平均收益及趋势
- ✅ **图表网格**：价差与成交量趋势、数据质量分布、成交量分布、时间分布热力图
- ✅ **分析报告**：基本统计、套利机会分析

### 5. CaseExplorer（案例回放）
- ✅ **案例列表表格**：展示历史套利案例（ID、时间、方向、收益、状态）
- ✅ **案例详情查看**：点击行可查看具体案例信息

### 6. DataLab（数据实验室/文档页）
- ✅ **系统文档**：系统概述、核心功能、系统架构、使用指南、技术栈
- ✅ **使用指南**：5步操作流程
- ✅ **联系支持**：Email、在线客服、API文档入口

### 7. Alerts（告警中心）
- 🚧 告警规则配置（开发中）

### 8. Report（报告生成）
- 🚧 报告生成与导出（开发中）

## 🏗️ 技术架构

### 技术栈

```
Vue 2.6.14
├── Vue Router 3.5.3      # 路由管理
├── Vuex 3.6.2            # 状态管理
├── ECharts 5.4.3         # 数据可视化
├── Axios 1.4.0           # HTTP客户端
├── Day.js 1.11.9         # 时间处理
├── Lodash 4.17.21        # 工具库
└── Sass                  # CSS预处理器
```

### 项目结构

```
frontend/
├── public/
│   ├── index.html              # HTML模板
│   ├── candlestick_daily.json  # K线数据
│   └── processed_data.json     # 处理后的数据
├── src/
│   ├── components/             # 可复用组件
│   │   ├── ChartCard.vue       # 图表卡片组件
│   │   ├── DataTable.vue       # 数据表格组件
│   │   └── StatCard.vue        # 统计卡片组件
│   ├── layout/
│   │   └── MainLayout.vue      # 主布局组件
│   ├── views/                  # 页面组件
│   │   ├── Overview.vue        # 概览页（主页）
│   │   ├── ArbRadar.vue        # 套利雷达
│   │   ├── Backtest.vue        # 回测分析
│   │   ├── MarketCompare.vue   # 市场对比
│   │   ├── CaseExplorer.vue    # 案例回放
│   │   ├── DataLab.vue         # 数据实验室/文档
│   │   ├── Alerts.vue          # 告警中心
│   │   └── Report.vue          # 报告生成
│   ├── store/
│   │   └── index.js            # Vuex状态管理
│   ├── router/
│   │   └── index.js            # 路由配置
│   ├── utils/                  # 工具函数
│   │   ├── mockData.js         # 模拟数据生成器
│   │   ├── csvLoader.js        # CSV数据加载器
│   │   ├── processedDataLoader.js  # 处理后数据加载器
│   │   └── workerManager.js   # Web Worker管理器
│   ├── styles/                 # 样式文件
│   │   ├── variables.scss      # SCSS变量
│   │   └── global.scss         # 全局样式
│   ├── App.vue                 # 根组件
│   └── main.js                 # 入口文件
├── package.json
├── vue.config.js               # Vue CLI配置
├── babel.config.js            # Babel配置
└── README.md
```

## 🚀 快速开始

### 环境要求

- Node.js >= 14.0.0
- npm >= 6.0.0 或 yarn >= 1.22.0

### 安装依赖

```bash
cd frontend
npm install
# 或
yarn install
```

### 开发模式

```bash
npm run serve
# 或
yarn serve
```

访问 http://localhost:8080

### 构建生产版本

```bash
npm run build
# 或
yarn build
```

构建产物将输出到 `dist/` 目录

### 代码检查

```bash
npm run lint
# 或
yarn lint
```

## 🎨 设计理念

### 配色方案

```scss
// 主色调
$color-primary: #3b82f6;      // 蓝色 - Binance
$color-success: #10b981;       // 绿色 - Uniswap
$color-warning: #f97316;       // 橙色
$color-danger: #ef4444;       // 红色

// 背景色
$bg-primary: #f9fafb;         // 浅灰白
$bg-card: #ffffff;            // 纯白

// 文本色
$text-primary: #111827;       // 深黑
$text-secondary: #6b7280;     // 灰色
$text-tertiary: #9ba5b8;      // 浅灰
```

### 视觉特点

- **简洁明亮**：浅色背景，清晰易读
- **卡片布局**：左侧参数面板，右侧图表展示
- **响应式设计**：适配不同屏幕尺寸
- **微动效**：平滑过渡，提升用户体验

## 📊 数据说明

### 模拟数据

项目使用 `src/utils/mockData.js` 生成符合真实场景的模拟数据：

- **价格数据**：基于布朗运动的价格序列，基准价格 2580 USDT（ETH）
- **价差数据**：计算CEX与DEX价差及Z-Score（滑动窗口统计）
- **套利信号**：基于检测器参数自动识别，包含收益分解
- **回测结果**：策略回测统计指标（胜率、夏普比率等）

### 真实数据接入

要接入真实数据，需修改以下文件：

1. **`src/store/index.js`** - 修改 actions 中的数据获取逻辑
   ```javascript
   async loadPriceData({ commit, state }) {
     // 替换为真实API调用
     const response = await axios.get('/api/price-data', {
       params: {
         start: state.config.timeRange.start,
         end: state.config.timeRange.end
       }
     })
     commit('SET_PRICE_DATA', response.data)
   }
   ```

2. **API端点**：
   - Binance API: `https://api.binance.com/api/v3/klines`
   - Uniswap V3: 通过 The Graph Subgraph 或直接查询以太坊节点

## 🔧 配置说明

### 全局配置

在 `src/store/index.js` 中修改：

```javascript
config: {
  pair: 'ETH/USDT',              // 交易对
  dex: 'Uniswap V3 (0.3%)',     // DEX池
  cex: 'Binance (0.1%)',        // CEX交易所
  timeRange: {
    start: new Date('2025-09-01').getTime(),
    end: new Date('2025-09-30').getTime()
  },
  detector: {
    priceThreshold: 0.8,        // 价差阈值（USDT）
    zScoreThreshold: 2.0,       // Z-Score阈值
    timeWindow: [1, 20],        // 时间窗口（秒）
    volumeMin: 1000,            // 最小成交量（USDT）
    fees: {
      cex: 0.001,              // CEX手续费（0.1%）
      dex: 0.003,              // DEX手续费（0.3%）
      gas: 15,                 // Gas费用（USDT）
      slippage: 0.002          // 滑点（0.2%）
    }
  }
}
```

### 检测器参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `priceThreshold` | 检测套利机会时所需的最小价差幅度 | 0.8 USDT |
| `zScoreThreshold` | 标准化后的价差统计值，值越大表示偏离均值越远 | 2.0 |
| `timeWindow` | 计算统计指标的时间范围 | [1, 20] 秒 |
| `volumeMin` | 参与套利所需的最小交易量 | 1000 USDT |
| `fees.cex` | 中心化交易所的交易手续费率 | 0.1% |
| `fees.dex` | 去中心化交易所的交易手续费率 | 0.3% |
| `fees.gas` | 以太坊网络的交易Gas费用 | 15 USDT |
| `fees.slippage` | 交易时的预期价格滑点 | 0.2% |

## 📖 使用指南

### 1. 查看市场概览

访问"概览"页面（Overview），你可以：

- 选择时间范围（全月/上半月/下半月/自定义日历）
- 选择DEX池和CEX交易所的手续费等级
- 查看价格对比图、雷达图、热力图等多种可视化图表
- 查看实时统计：检测信号数、平均价差、潜在收益

### 2. 检测套利信号

1. 进入"套利雷达"页面（ArbRadar）
2. 在左侧配置检测参数：
   - 价差阈值、Z-Score阈值
   - 最小成交量、时间窗口
   - 费用设置（手续费、Gas费、滑点）
3. 或选择预设方案：保守型/平衡型/激进型
4. 点击"检测信号"按钮
5. 查看信号列表，支持按时间/收益/置信度排序
6. 点击信号查看详细收益分解（毛收益、总成本、净收益）
7. 查看信号空间分布图，了解机会分布规律

### 3. 回测策略

1. 进入"回测分析"页面（Backtest）
2. 点击"运行回测"按钮
3. 查看统计指标：总交易次数、胜率、总收益、夏普比率
4. 分析权益曲线，评估策略表现

### 4. 数据分析

1. 进入"市场对比"页面（MarketCompare）
2. 导入数据（文件/API/示例数据）
3. 查看数据质量检测结果
4. 查看价差与成交量趋势、数据质量分布等图表
5. 查看分析报告：基本统计、套利机会分析

### 5. 导出数据

- **图表导出**：点击图表右上角的导出按钮（开发中）
- **信号列表导出**：在套利雷达页面点击"导出"按钮，生成CSV文件

## 🎯 最佳实践

### 参数调优建议

**保守型策略**（适合稳健投资者）
```
价差阈值: 1.5 USDT
Z-Score: 3.0
最小成交量: 2000 USDT
Gas费用: 20 USDT
滑点: 0.3%
```

**平衡型策略**（推荐）
```
价差阈值: 0.8 USDT
Z-Score: 2.0
最小成交量: 1000 USDT
Gas费用: 15 USDT
滑点: 0.2%
```

**激进型策略**（适合高频交易）
```
价差阈值: 0.5 USDT
Z-Score: 1.5
最小成交量: 500 USDT
Gas费用: 10 USDT
滑点: 0.1%
```

### 置信度解读

- **置信度 0-40%**：价差偏离均值较小，机会一般
- **置信度 40-60%**：价差偏离均值2-3个标准差，机会较好
- **置信度 60-80%**：价差偏离均值3-4个标准差，机会很好
- **置信度 80-100%**：价差偏离均值5个标准差以上，极佳机会

## 🔍 核心算法

### 套利信号检测流程

1. **数据对齐**：获取并对齐Uniswap和Binance的价格数据
2. **价差计算**：计算CEX与DEX之间的价格差异
3. **Z-Score计算**：基于滑动窗口计算价差的Z-Score（标准化统计值）
4. **毛利润评估**：基于价差和交易规模计算毛利润
5. **成本扣除**：
   - CEX手续费 = 交易量 × CEX价格 × CEX手续费率
   - DEX手续费 = 交易量 × DEX价格 × DEX手续费率
   - Gas费用 = 固定值
   - 滑点成本 = 交易量 × 价格 × 滑点率
6. **净利润计算**：净利润 = 毛利润 - 总成本
7. **阈值过滤**：只保留净利润 > 0 且满足价差阈值和Z-Score阈值的信号

### 置信度计算

```javascript
confidence = Math.min(absZ / 5, 1)
```

- 基于Z-Score计算，最大值为1（100%）
- Z-Score越大，置信度越高，套利机会越可靠

## 🐛 常见问题

### Q: 为什么图表显示"数据加载中"？

A: 检查以下几点：
1. 确认时间范围选择正确
2. 检查浏览器控制台是否有错误
3. 确认 `src/store/index.js` 中的数据加载逻辑正常

### Q: 如何修改交易对？

A: 在 `src/store/index.js` 中修改 `config.pair`，并在 `Overview.vue` 中更新显示文本。

### Q: 如何接入真实数据？

A: 参考"真实数据接入"章节，修改 `src/store/index.js` 中的 actions，替换为真实API调用。

### Q: 图表性能如何优化？

A: 
- 数据点过多时，系统会自动抽样（最多2000个数据点）
- 使用Web Worker处理大数据量计算
- 图表支持按需渲染

## 📝 开发计划

### 已完成 ✅

- [x] 前端基础框架搭建
- [x] 8个核心页面实现
- [x] 模拟数据生成器
- [x] 多维度数据可视化
- [x] 套利信号检测算法
- [x] 回测分析功能
- [x] 数据导入导出

### 进行中 🚧

- [ ] 告警规则配置
- [ ] 报告生成与导出
- [ ] 案例回放时间轴动画

### 计划中 📋

- [ ] 实时数据流（WebSocket）
- [ ] 真实数据API接入
- [ ] 3D可视化（WebGL）
- [ ] 多策略并行回测
- [ ] PDF报告导出
- [ ] 用户认证与权限管理

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发流程

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- 使用 ESLint 进行代码检查
- 遵循 Vue 官方风格指南
- 组件命名使用 PascalCase
- 文件命名使用 kebab-case

## 📄 许可证

MIT License

## ⚠️ 免责声明

本项目仅用于研究和学习目的，不构成任何投资建议。使用本系统进行实际交易的风险由用户自行承担。

---

**项目地址**: [GitHub Repository](https://github.com/your-username/Software-Requirements)

**问题反馈**: [Issues](https://github.com/your-username/Software-Requirements/issues)

**文档更新**: 2025年1月
