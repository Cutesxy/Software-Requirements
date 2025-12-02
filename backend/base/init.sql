-- init.sql
-- Initialize database 'txdata' and create necessary tables for the project.
-- Run: mysql -u root -p < init.sql

CREATE DATABASE IF NOT EXISTS `txdata`
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;
USE `txdata`;

-- ------------------------------------------------------------
-- Table: uniswap_swaps
-- Store raw swap records fetched from The Graph for auditing
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `uniswap_swaps`;
CREATE TABLE IF NOT EXISTS `uniswap_swaps` (
  `id` VARCHAR(128) NOT NULL,               /* swap id (graph id) */
  `pool_address` VARCHAR(66) NOT NULL,      /* pool contract address (0x...) */
  `timestamp` INT UNSIGNED NOT NULL,        /* epoch seconds */
  `ts` DATETIME(6) NOT NULL,                /* timestamp as datetime (UTC) */
  `amount0` DECIMAL(38,18) DEFAULT NULL,
  `amount1` DECIMAL(38,18) DEFAULT NULL,
  `price` DECIMAL(38,18) DEFAULT NULL,      /* 计算出的价格 (USDT per ETH) */
  `sqrtPriceX96` VARCHAR(80) DEFAULT NULL,
  `tick` INT DEFAULT NULL,
  `tx_hash` VARCHAR(128) DEFAULT NULL,
  `raw` JSON DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `idx_pool_ts` (`pool_address`, `ts`),
  INDEX `idx_timestamp` (`timestamp`),
  INDEX `idx_price` (`price`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- Table: binance_klines
-- Store raw Binance kline/candle data
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `binance_klines`;
CREATE TABLE IF NOT EXISTS `binance_klines` (
  `symbol` VARCHAR(32) NOT NULL,
  `open_time_ms` BIGINT NOT NULL,
  `open_time` DATETIME(6) NOT NULL,
  `open` DECIMAL(38,18) DEFAULT NULL,
  `high` DECIMAL(38,18) DEFAULT NULL,
  `low` DECIMAL(38,18) DEFAULT NULL,
  `close` DECIMAL(38,18) DEFAULT NULL,
  `volume` DECIMAL(38,18) DEFAULT NULL,
  `quote_av` DECIMAL(38,18) DEFAULT NULL,
  `trades` INT DEFAULT NULL,
  `raw` JSON DEFAULT NULL,
  PRIMARY KEY (`symbol`, `open_time_ms`),
  INDEX `idx_symbol_open_time` (`symbol`, `open_time`),
  INDEX `idx_open_time_ms` (`open_time_ms`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- Table: merged_trading_data
-- 合并的分钟级交易数据，时间戳对齐
-- ------------------------------------------------------------
DROP TABLE IF EXISTS `merged_trading_data`;
CREATE TABLE IF NOT EXISTS `merged_trading_data` (
  `time_bucket` DATETIME NOT NULL,           /* 分钟级时间桶，例如: 2024-01-01 10:00:00 */
  `timestamp` INT UNSIGNED NOT NULL,         /* 对应的 Unix 时间戳 */
  /* Uniswap 数据 */
  `uniswap_swap_count` INT DEFAULT 0,        /* 该分钟内的 swap 数量 */
  `uniswap_total_volume_eth` DECIMAL(38,18) DEFAULT 0,  /* 该分钟内 ETH 总交易量 */
  `uniswap_total_volume_usdt` DECIMAL(38,18) DEFAULT 0, /* 该分钟内 USDT 总交易量 */
  `uniswap_avg_price` DECIMAL(38,18) DEFAULT NULL,      /* 该分钟内平均价格 */
  `uniswap_min_price` DECIMAL(38,18) DEFAULT NULL,      /* 该分钟内最低价格 */
  `uniswap_max_price` DECIMAL(38,18) DEFAULT NULL,      /* 该分钟内最高价格 */
  `uniswap_price_std` DECIMAL(38,18) DEFAULT NULL,      /* 价格标准差 */
  /* Binance 数据 */
  `binance_open` DECIMAL(38,18) DEFAULT NULL,           /* Binance 开盘价 */
  `binance_high` DECIMAL(38,18) DEFAULT NULL,           /* Binance 最高价 */
  `binance_low` DECIMAL(38,18) DEFAULT NULL,            /* Binance 最低价 */
  `binance_close` DECIMAL(38,18) DEFAULT NULL,          /* Binance 收盘价 */
  `binance_volume` DECIMAL(38,18) DEFAULT NULL,         /* Binance 成交量 */
  `binance_quote_volume` DECIMAL(38,18) DEFAULT NULL,   /* Binance 报价资产成交量 */
  `binance_trades` INT DEFAULT NULL,                    /* Binance 成交笔数 */
  /* 价格差异指标 */
  `price_difference` DECIMAL(38,18) DEFAULT NULL,       /* Uniswap平均价 - Binance收盘价 */
  `price_ratio` DECIMAL(38,18) DEFAULT NULL,            /* Uniswap平均价 / Binance收盘价 */
  PRIMARY KEY (`time_bucket`),
  INDEX `idx_timestamp` (`timestamp`),
  INDEX `idx_time_bucket` (`time_bucket`),
  INDEX `idx_uniswap_swap_count` (`uniswap_swap_count`),
  INDEX `idx_price_difference` (`price_difference`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `signal`;
CREATE TABLE IF NOT EXISTS `signal` (
  `id` INT AUTO_INCREMENT,
  `time_bucket` DATETIME NOT NULL,
  `timestamp` INT UNSIGNED NOT NULL,
  `direction` VARCHAR(16) NOT NULL,  /* 'buy' or 'sell' */
  `swap_count` INT DEFAULT 0,
  `size` DECIMAL(38,18) DEFAULT NULL,
  `zscore` DECIMAL(10,6) DEFAULT NULL,
  `gross_profit` DECIMAL(38,18) DEFAULT NULL,
  `binance_fee` DECIMAL(38,18) DEFAULT NULL,
  `uniswap_fee` DECIMAL(38,18) DEFAULT NULL,
  `gas_cost` DECIMAL(38,18) DEFAULT NULL,
  `net_profit` DECIMAL(38,18) DEFAULT NULL,
  `uniswap_avg_price` DECIMAL(38,18) DEFAULT NULL,      /* 该分钟内平均价格 */
  `binance_close_price` DECIMAL(38,18) DEFAULT NULL,    /* Binance 收盘价 */
  `price_difference` DECIMAL(38,18) DEFAULT NULL,       /* Uniswap平均价 - Binance收盘价 */
  `confidence` DECIMAL(10,6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `idx_time_bucket` (`time_bucket`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 创建用于数据质量检查的视图
CREATE OR REPLACE VIEW data_quality_view AS
SELECT 
    'uniswap_swaps' as table_name,
    COUNT(*) as record_count,
    MIN(ts) as min_timestamp,
    MAX(ts) as max_timestamp,
    COUNT(DISTINCT DATE(ts)) as active_days,
    AVG(ABS(amount0)) as avg_eth_volume,
    AVG(ABS(amount1)) as avg_usdt_volume,
    AVG(price) as avg_price
FROM uniswap_swaps
UNION ALL
SELECT 
    'binance_klines' as table_name,
    COUNT(*) as record_count,
    MIN(open_time) as min_timestamp,
    MAX(open_time) as max_timestamp,
    COUNT(DISTINCT DATE(open_time)) as active_days,
    NULL as avg_eth_volume,
    NULL as avg_usdt_volume,
    AVG(close) as avg_price
FROM binance_klines
UNION ALL
SELECT 
    'merged_trading_data' as table_name,
    COUNT(*) as record_count,
    MIN(time_bucket) as min_timestamp,
    MAX(time_bucket) as max_timestamp,
    COUNT(DISTINCT DATE(time_bucket)) as active_days,
    AVG(uniswap_total_volume_eth) as avg_eth_volume,
    AVG(uniswap_total_volume_usdt) as avg_usdt_volume,
    AVG(uniswap_avg_price) as avg_price
FROM merged_trading_data;

-- End of init.sql