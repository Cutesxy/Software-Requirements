## 数据类型 (Data Types)

- PriceData: { cex: Array<{ t: number, p: number, v: number, lat_ms: number }>, dex: Array<{ t: number, p: number, v: number, lat_ms: number }> }
  - CEX/DEX价格数据：时间戳、价格、成交量、延迟

- SpreadData: Array<{ t: number, spread: number, spreadPct: number, z: number, cexPrice: number, dexPrice: number }>
  - 价差数据：时间戳、价差值、百分比价差、Z-score、CEX价格、DEX价格

- Signal: Array<{ id: string, time: number, direction: string, spread: number, spreadPct: number, zScore: number, size: number, grossProfit: number, totalCost: number, netProfit: number, confidence: number, cexPrice: number, dexPrice: number, params: object }>
  - 套利信号：ID、时间、交易方向、价差、收益计算、置信度等

- BacktestResult: { totalTrades: number, winningTrades: number, winRate: number, totalProfit: number, avgProfit: number, maxDrawdown: number, sharpeRatio: number, equity: Array<{ time: number, equity: number }>, signals: Signal[] }
  - 回测结果：交易统计、收益指标、夏普比率、权益曲线

- HeatmapData: Array<[number, number, number]>
  - 热力图数据：小时、区间、平均Z-score值

- CorrelationData: Array<{ lag: number, correlation: number }>
  - 相关性数据：滞后时间、相关系数

## 函数接口 (Function Interfaces)

- generatePriceData(start: number, end: number, interval: string) => PriceData
  - 获取价格数据：开始时间、结束时间、时间间隔 → 返回价格数据

- generateSpreadData(start: number, end: number, interval: string) => SpreadData
  - 获取价差数据：时间范围、间隔 → 返回价差数据

- generateSignals(start: number, end: number, detectorParams: object) => Signal
  - 生成套利信号：时间范围、检测参数 → 返回信号数组

- generateBacktestResults(params: object) => BacktestResult
  - 生成回测结果：检测参数 → 返回回测统计

- generateHeatmapData(start: number, end: number) => HeatmapData
  - 生成热力图数据：时间范围 → 返回热力图数据

- generateCorrelationData(start: number, end: number) => CorrelationData
  - 生成相关性数据：时间范围 → 返回相关性分析
