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
  `sqrtPriceX96` VARCHAR(80) DEFAULT NULL,
  `tick` INT DEFAULT NULL,
  `tx_hash` VARCHAR(128) DEFAULT NULL,
  `raw` JSON DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `idx_pool_ts` (`pool_address`, `ts`)
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
  INDEX `idx_symbol_open_time` (`symbol`, `open_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- End of init.sql