# K线图数据导出工具使用说明

## 功能说明

`candlestickDataExporter.js` 提供了将价格数据转换为K线图格式并导出为JSON的功能。

## 使用方法

### 1. 基本导出

```javascript
import candlestickDataExporter from '@/utils/candlestickDataExporter'

// 导出指定时间范围的K线数据
const startTime = new Date('2025-09-01').getTime()
const endTime = new Date('2025-09-30').getTime()

const data = await candlestickDataExporter.exportCandlestickData(startTime, endTime)
console.log(data)
```

### 2. 导出并下载为JSON文件

```javascript
// 自动下载JSON文件
await candlestickDataExporter.exportAndDownload(startTime, endTime)

// 自定义文件名
await candlestickDataExporter.exportAndDownload(
  startTime, 
  endTime, 
  60 * 60 * 1000, // 1小时间隔
  'my_candlestick_data.json'
)
```

### 3. 自定义时间间隔

```javascript
// 15分钟K线
const interval15m = 15 * 60 * 1000
await candlestickDataExporter.exportAndDownload(startTime, endTime, interval15m)

// 1小时K线（默认）
const interval1h = 60 * 60 * 1000
await candlestickDataExporter.exportAndDownload(startTime, endTime, interval1h)

// 1天K线
const interval1d = 24 * 60 * 60 * 1000
await candlestickDataExporter.exportAndDownload(startTime, endTime, interval1d)
```

## 导出数据格式

```json
{
  "meta": {
    "startTime": 1725120000000,
    "endTime": 1727712000000,
    "interval": 3600000,
    "intervalLabel": "1小时",
    "dexCount": 720,
    "cexCount": 720,
    "exportTime": "2025-09-15T10:30:00.000Z"
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

## 数据字段说明

- **time**: 时间戳（毫秒）
- **open**: 开盘价（该时间窗口的第一个价格）
- **close**: 收盘价（该时间窗口的最后一个价格）
- **high**: 最高价（该时间窗口内的最高价格）
- **low**: 最低价（该时间窗口内的最低价格）
- **volume**: 总成交量（该时间窗口内的成交量总和）

## 在Vue组件中使用

```vue
<script>
import candlestickDataExporter from '@/utils/candlestickDataExporter'

export default {
  methods: {
    async exportKLineData() {
      try {
        const startTime = this.$store.state.config.timeRange.start
        const endTime = this.$store.state.config.timeRange.end
        
        await candlestickDataExporter.exportAndDownload(
          startTime,
          endTime,
          60 * 60 * 1000, // 1小时
          `candlestick_${new Date(startTime).toISOString().split('T')[0]}.json`
        )
        
        alert('K线数据导出成功！')
      } catch (error) {
        console.error('导出失败:', error)
        alert('导出失败: ' + error.message)
      }
    }
  }
}
</script>
```

