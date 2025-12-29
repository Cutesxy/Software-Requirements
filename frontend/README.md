# 区块链非原子套利识别平台 | CEX-DEX Arbitrage Radar

> 简洁浅色风格的区块链套利交易可视化分析平台，基于 Vue2 构建

## 📋 项目概述

本项目是一个专注于**CEX（中心化交易所）与DEX（去中心化交易所）之间非原子套利识别**的Web应用平台。通过实时数据分析、可视化展示和智能检测算法，为研究者、量化工程师和风控人员提供全面的套利机会识别与分析工具。

### 核心特性

- 🎯 **实时价差监测** - 跨平台价格对比与价差热力图
- 🔍 **智能套利识别** - 基于Z-Score和多维度规则的套利信号检测
- 📊 **可视化分析** - 热力图、K线图、相关性分析等多种图表
- 🎨 **简洁UI设计** - 浅色主题，左右分栏布局，清晰明快
- 📈 **回测系统** - 策略回测与收益分析
- 💾 **数据导出** - 支持CSV、PNG等多种格式导出

## 🏗️ 技术架构

```
Vue 2.6.14
├── Vue Router 3.5.3      # 路由管理
├── Vuex 3.6.2            # 状态管理
├── ECharts 5.4.3         # 数据可视化
├── Axios 1.4.0           # HTTP客户端
├── Sass                  # CSS预处理器
└── Day.js                # 时间处理
```

## 📁 项目结构

```
frontend/
├── public/
│   └── index.html              # HTML模板
├── src/
│   ├── components/             # 可复用组件
│   │   ├── ChartCard.vue       # 图表卡片组件
│   │   ├── DataTable.vue       # 数据表格组件
│   │   └── StatCard.vue        # 统计卡片组件
│   ├── layout/
│   │   └── MainLayout.vue      # 主布局
│   ├── views/                  # 页面组件
│   │   ├── Overview.vue        # 总览页
│   │   ├── ArbRadar.vue        # 套利雷达（核心）
│   │   ├── MarketCompare.vue   # 市场对比
│   │   ├── CaseExplorer.vue    # 案例回放
│   │   ├── Backtest.vue        # 回测分析
│   │   ├── DataLab.vue         # 数据实验台
│   │   ├── Alerts.vue          # 告警中心
│   │   └── Report.vue          # 报告生成
│   ├── store/
│   │   └── index.js            # Vuex状态管理
│   ├── router/
│   │   └── index.js            # 路由配置
│   ├── utils/
│   │   └── mockData.js         # 模拟数据生成器
│   ├── styles/
│   │   ├── variables.scss      # SCSS变量
│   │   └── global.scss         # 全局样式
│   ├── App.vue                 # 根组件
│   └── main.js                 # 入口文件
├── package.json
├── vue.config.js
└── README.md
```

## 🚀 快速开始

### 安装依赖

```bash
cd frontend
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:8080

### 构建生产版本

```bash
npm run build
```

## 🎨 设计理念

### 配色方案（简洁浅色风格）

```scss
背景主色: #f9fafb (浅灰白)
卡片背景: #ffffff (纯白)

文本主色: #111827 (深黑)
文本次色: #6b7280 (灰色)

主题色（蓝）: #3b82f6 - Binance
强调色（绿）: #10b981 - Uniswap
警告色（橙）: #f97316
危险色（红）: #ef4444
```

### 视觉特点

- **简洁明亮** - 浅色背景，清晰易读
- **卡片布局** - 左侧参数面板，右侧图表展示
- **微动效** - 平滑过渡，不干扰阅读
- **响应式** - 适配不同屏幕尺寸

## 📊 核心功能模块

### 1. Overview 总览

- ✅ 跨平台价差热力图
- ✅ 联动K线价格对比
- ✅ 滞后相关性分析
- ✅ 价差分布统计
- ✅ 关键指标概览

### 2. Arb Radar 套利雷达（核心）

- ✅ 可配置检测器（价差阈值、Z-Score、时间窗口等）
- ✅ 费用模型（CEX/DEX手续费、Gas、滑点）
- ✅ 套利信号列表（支持排序、筛选）
- ✅ 信号空间分布可视化
- ✅ 详细收益分解
- ✅ 预设策略方案

### 3. Market Compare 市场对比

- ✅ 价差时间序列
- ✅ 价差分布对比
- ✅ 成交量对比
- ✅ 波动率分析

### 4. Backtest 回测分析

- ✅ 策略回测引擎
- ✅ 权益曲线展示
- ✅ 关键指标统计（胜率、夏普比率、最大回撤等）

### 5. Case Explorer 案例回放

- ✅ 套利案例列表
- ⏳ 时间轴事件回放（开发中）
- ⏳ 证据链可视化（开发中）

### 6. 其他模块

- Data Lab: 数据查询与导出
- Alerts: 告警规则配置
- Report: 分析报告生成

## 📈 数据说明

### 模拟数据

项目使用 `mockData.js` 生成符合真实场景的模拟数据：

- **价格数据** - 基于布朗运动的价格序列
- **价差数据** - 计算CEX与DEX价差及Z-Score
- **套利信号** - 基于检测器参数自动识别
- **回测结果** - 策略回测统计指标

### 真实数据接入

要接入真实数据，需修改以下文件：

1. `src/store/index.js` - 修改 actions 中的数据获取逻辑
2. 替换 API 调用：
   - Binance API: https://api.binance.com/api/v3/klines
   - Uniswap V3: 通过 The Graph 或 Etherscan API

## 🔧 配置说明

### 全局配置

在 `src/store/index.js` 中修改：

```javascript
config: {
  pair: 'USDT/ETH',           // 交易对
  dex: 'Uniswap V3 (0.3%)',   // DEX池
  cex: 'Binance',             // CEX
  timeRange: { ... },         // 时间范围
  detector: { ... }           // 检测器参数
}
```

### 检测器参数

```javascript
detector: {
  priceThreshold: 0.8,      // 价差阈值（USDT）
  zScoreThreshold: 2.0,     // Z-Score阈值
  timeWindow: [1, 20],      // 时间窗口（秒）
  volumeMin: 1000,          // 最小成交量
  fees: {
    cex: 0.001,            // CEX手续费（0.1%）
    dex: 0.003,            // DEX手续费（0.3%）
    gas: 15,               // Gas费用（USDT）
    slippage: 0.002        // 滑点（0.2%）
  }
}
```

## 📖 使用指南

### 1. 查看市场总览

访问"总览"页面，查看：
- 平均价差、最大价差、套利机会数量等关键指标
- 价差热力图，识别高价差时段
- CEX与DEX价格走势对比
- 滞后相关性分析

### 2. 检测套利信号

1. 进入"套利雷达"页面
2. 在左侧配置检测参数（或选择预设方案）
3. 点击"检测信号"
4. 查看信号列表，按收益或置信度排序
5. 点击信号查看详细收益分解

### 3. 回测策略

1. 进入"回测分析"页面
2. 查看策略回测结果
3. 分析权益曲线、胜率、夏普比率等指标

### 4. 导出数据

- 图表：点击图表右上角的导出按钮
- 信号列表：点击"导出"按钮生成CSV文件

## 🎯 最佳实践

### 参数调优建议

**保守型策略**
```
价差阈值: 1.5 USDT
Z-Score: 3.0
最小成交量: 2000 USDT
```

**平衡型策略**
```
价差阈值: 0.8 USDT
Z-Score: 2.0
最小成交量: 1000 USDT
```

**激进型策略**
```
价差阈值: 0.5 USDT
Z-Score: 1.5
最小成交量: 500 USDT
```

## 🔍 性能优化

- **虚拟滚动** - 表格支持大数据量流畅渲染
- **图表抽稀** - 数据点过多时自动抽样
- **懒加载** - 路由组件按需加载
- **防抖节流** - 输入框、滚动事件优化

## 📝 待完成功能

- [ ] 实时数据流（WebSocket）
- [ ] 案例回放时间轴动画
- [ ] 3D可视化（WebGL）
- [ ] 多策略并行回测
- [ ] 告警规则引擎
- [ ] PDF报告导出

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

**注意**: 本项目仅用于研究和学习目的，不构成任何投资建议。

