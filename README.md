# 区块链非原子套利交易识别系统

> 软件需求工程课程项目 - CEX/DEX 套利机会识别与分析平台

## 技术栈

- **前端**: Vue 2 + ECharts 5 + Web Worker
- **后端**: Python 3 + Flask + Pandas/NumPy
- **数据存储**: CSV + JSON + MySQL

## 快速开始

### 前端

```bash
cd frontend
npm install
npm run serve
```

访问 http://localhost:8080

### 后端

```bash
cd backend/Software-Requirements/backend
pip install -r requirements.txt
python api.py
```

## 登录

访问 http://localhost:8080/login

**默认账号密码**:
- 用户名: `admin`
- 密码: `123456`

## 项目结构

```
Software-Requirements/
├── frontend/          # Vue 前端应用
└── backend/           # Python 后端服务
```

## 功能

- 📊 价格对比可视化
- 🔍 套利信号检测
- 📈 回测分析
- 📋 数据分析报告
