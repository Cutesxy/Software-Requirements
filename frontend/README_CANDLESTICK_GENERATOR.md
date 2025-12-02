# K线图数据生成脚本使用说明

## 功能说明

`generate_candlestick_data.py` 脚本用于预处理原始数据，生成按天聚合的K线图数据，保存为JSON格式。这样前端在切换到时间范围模式时，可以直接读取预处理好的数据，无需实时计算。

## 使用方法

### 1. 运行脚本

```bash
# 在项目根目录运行
python generate_candlestick_data.py
```

### 2. 输出文件

脚本会生成 `public/candlestick_daily.json` 文件，包含按天聚合的K线数据。

## 数据格式

生成的JSON文件格式：

```json
{
  "meta": {
    "generatedAt": "2025-09-15T10:30:00.000000",
    "sourceFile": "public/processed_data.json",
    "totalDataPoints": 30000,
    "dexCandleCount": 30,
    "cexCandleCount": 30,
    "interval": "1day",
    "description": "按天聚合的K线数据，每天包含开盘、收盘、最高、最低价格和总成交量"
  },
  "dex": [
    {
      "time": 1725120000000,
      "open": 4200.50,
      "close": 4210.30,
      "high": 4220.00,
      "low": 4195.20,
      "volume": 125000.50
    },
    ...
  ],
  "cex": [
    {
      "time": 1725120000000,
      "open": 4201.00,
      "close": 4211.50,
      "high": 4218.00,
      "low": 4198.00,
      "volume": 150000.00
    },
    ...
  ]
}
```

## 数据说明

- **time**: 当天开始时间（毫秒时间戳，当天 00:00:00）
- **open**: 开盘价（当天第一个数据点的价格）
- **close**: 收盘价（当天最后一个数据点的价格）
- **high**: 最高价（当天所有数据点中的最高价格）
- **low**: 最低价（当天所有数据点中的最低价格）
- **volume**: 总成交量（当天所有数据点的成交量总和）

## 在前端使用

修改 `processedDataLoader.js` 或创建新的加载器来读取预处理好的K线数据：

```javascript
// 加载预处理好的K线数据
async loadCandlestickData() {
  const response = await fetch('/candlestick_daily.json')
  const data = await response.json()
  return data
}
```

## 注意事项

1. 确保 `public/processed_data.json` 文件存在
2. 运行脚本前确保已安装 Python 3
3. 生成的数据文件会保存在 `public/` 目录，可以直接被前端访问
4. 如果原始数据更新，需要重新运行脚本生成新的K线数据

