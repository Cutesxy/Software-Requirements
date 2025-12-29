# 区块链非原子套利交易识别系统

软件需求工程课程项目 - 基于 CEX/DEX 价格差异的套利机会识别与分析平台

## 快速开始

### 前端

```bash
cd frontend
npm install
npm run dev
```

### 后端

```bash
cd backend
pip install -r base/requirements.txt
python api.py
```

> 注意：后端端口可在 `backend/config.py` 中配置

## 主要功能

- 📊 **数据分析中心** - 多维度数据可视化与 AI 智能总结
- 🎯 **套利识别** - 基于价差、Z-Score 等指标的信号检测
- 🔬 **回测分析** - 历史数据回测与策略评估
- 🤖 **AI 分析助手** - 自然语言交互与信号筛选

## 技术栈

**前端**: Vue.js 2.6 + ECharts + Vuex  
**后端**: Flask + Pandas  
**AI**: DeepSeek API

## 项目结构

```
Software-Requirements/
├── frontend/          # Vue.js 前端应用
├── backend/           # Flask 后端 API
└── README.md
```
