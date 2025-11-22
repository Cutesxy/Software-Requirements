from datetime import datetime

# MySQL 连接字符串 (SQLAlchemy 格式)
# 示例: mysql+pymysql://username:password@127.0.0.1:3306/dbname
MYSQL_URI = "mysql+pymysql://root:Mysql19491001@127.0.0.1:3306/txdata?charset=utf8mb4"

# Uniswap 子图 API (The Graph)
UNISWAP_SUBGRAPH_URL = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"

# 请在此填入要分析的 Uniswap V3 池地址（小写 hex），例如 USDT/ETH 池地址
POOL_ADDRESS = "0x11b815efb8f581194ae79006d24e0d814b7697f6"

# Binance 交易对（symbol）
BINANCE_SYMBOL = "ETHUSDT"

# 默认时间范围（字符串 YYYY-MM-DD）
START_DATE = "2025-09-01"
END_DATE = "2025-09-05"

# 分析默认参数
ANALYSIS_PARAMS = {
    "spread_pct_threshold": 0.005,   # 0.5%
    "min_duration_min": 2,           # 最少持续 2 分钟
    "trade_size_usdt": 10000,
    "uniswap_fee_pct": 0.003,
    "binance_fee_pct": 0.001,
    "assumed_slippage_pct": 0.002,
}