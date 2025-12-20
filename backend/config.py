import os

# ==========================================
# 1. Web 服务配置 (api.py 必须)
# ==========================================
HOST = "0.0.0.0"  # 监听所有 IP，方便从局域网或 Docker 访问。若仅本机访问可改为 "127.0.0.1"
PORT = 5319       # Flask 默认端口
DEBUG = True      # 开发模式开启，生产环境请关闭

# ==========================================
# 2. 数据文件路径配置
# ==========================================
# 你的 service.py 会读取这些文件，定义在这里方便管理
DATA_CSV_PATH = "merged_trading_data.csv"
SIGNALS_CSV_PATH = "arbitrage_signals.csv"

# ==========================================
# 3. 默认时间范围
# ==========================================
# 对应 2025年9月的数据
START_DATE = "2025-09-01"
END_DATE = "2025-09-30"

# ==========================================
# 4. 业务分析参数 (用于回测和计算)
# ==========================================
ANALYSIS_PARAMS = {
    "spread_pct_threshold": 0.005,   # 价差阈值 0.5%
    "min_duration_min": 2,           # 最小持续时间
    "trade_size_usdt": 10000,        # 默认单笔交易金额 (USDT)
    "uniswap_fee_pct": 0.003,        # Uniswap V3 手续费 0.3%
    "binance_fee_pct": 0.001,        # Binance 手续费 0.1%
    "gas_cost_estimate": 50,         # 预估 Gas 费 (USDT)，用于简易净利润计算
    "profit_threshold_in_usdt": 100  # 最小利润阈值
}

# ==========================================
# 5. 区块链元数据 (保留作为参考)
# ==========================================
# 虽然目前读取 CSV，但保留这些信息有助于明确数据来源
POOL_ADDRESS = "0x11b815efb8f581194ae79006d24e0d814b7697f6"
USDT_CONTRACT = "0xdac17f958d2ee523a2206206994597c13d831ec7"
WETH_CONTRACT = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
BINANCE_SYMBOL = "ETHUSDT"

# 区块范围 (Sep 01 - Sep 30, 2025)
START_BLOCK = 23264568
END_BLOCK = 23479238

# API 配置 (如需重新爬取数据时使用)
# 注意：代码公开时请注意隐藏 API Key
ETHERSCAN_API_KEY = "9A48U71U42BMHG4841H6IV72UF2B1RIA3X"
UNISWAP_SUBGRAPH_URL = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"

# ==========================================
# 6. 数据库配置 (已弃用/备份)
# ==========================================
# 注意：当前项目已切换为 CSV 读取模式 (service.py/DataLoader)
# 下方配置暂时不生效，仅作归档。
# MYSQL_URI = "mysql+pymysql://root:Mysql19491001@127.0.0.1:3306/txdata?charset=utf8mb4"