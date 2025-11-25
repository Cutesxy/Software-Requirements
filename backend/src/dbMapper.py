from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, BigInteger, Numeric, JSON, text
from sqlalchemy.orm import declarative_base, sessionmaker
import pandas as pd
import config

Base = declarative_base()

class UniswapSwap(Base):
    __tablename__ = 'uniswap_swaps'
    
    id = Column(String(128), primary_key=True)
    pool_address = Column(String(66), nullable=False)
    timestamp = Column(Integer, nullable=False)           # epoch seconds
    ts = Column(DateTime, nullable=False)                  # DATETIME(6)
    amount0 = Column(Numeric(38,18), nullable=True)
    amount1 = Column(Numeric(38,18), nullable=True)
    sqrtPriceX96 = Column(String(80), nullable=True)
    tick = Column(Integer, nullable=True)
    tx_hash = Column(String(128), nullable=True)
    raw = Column(JSON, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "pool_address": self.pool_address,
            "timestamp": int(self.timestamp) if self.timestamp is not None else None,
            "ts": self.ts.isoformat() if self.ts is not None else None,
            "amount0": float(self.amount0) if self.amount0 is not None else None,
            "amount1": float(self.amount1) if self.amount1 is not None else None,
            "sqrtPriceX96": self.sqrtPriceX96,
            "tick": int(self.tick) if self.tick is not None else None,
            "tx_hash": self.tx_hash,
            "raw": self.raw,
        }


class BinanceKline(Base):
    __tablename__ = 'binance_klines'

    symbol = Column(String(32), primary_key=True)
    open_time_ms = Column(BigInteger, primary_key=True)
    open_time = Column(DateTime, nullable=False)
    open = Column(Numeric(38,18), nullable=True)
    high = Column(Numeric(38,18), nullable=True)
    low = Column(Numeric(38,18), nullable=True)
    close = Column(Numeric(38,18), nullable=True)
    volume = Column(Numeric(38,18), nullable=True)
    quote_av = Column(Numeric(38,18), nullable=True)
    trades = Column(Integer, nullable=True)
    raw = Column(JSON, nullable=True)

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "open_time_ms": int(self.open_time_ms) if self.open_time_ms is not None else None,
            "open_time": self.open_time.isoformat() if self.open_time is not None else None,
            "open": float(self.open) if self.open is not None else None,
            "high": float(self.high) if self.high is not None else None,
            "low": float(self.low) if self.low is not None else None,
            "close": float(self.close) if self.close is not None else None,
            "volume": float(self.volume) if self.volume is not None else None,
            "quote_av": float(self.quote_av) if self.quote_av is not None else None,
            "trades": int(self.trades) if self.trades is not None else None,
            "raw": self.raw,
        }


class DBMapper:
    def __init__(self, mysql_uri=None):
        self.mysql_uri = mysql_uri or config.MYSQL_URI
        # 使用 future=True 保持 2.0 风格
        self.engine = create_engine(self.mysql_uri, pool_pre_ping=True, future=True)
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)

    def init_db(self):
        """
        创建表结构（如果不存在）。在程序启动时调用一次。
        """
        Base.metadata.create_all(self.engine)
        print("数据库表结构初始化完成")

    def store_uniswap_swap(self, swap_data):
        """
        存储单条 uniswap_swaps 记录；如果主键已存在则使用 merge 执行 upsert。
        swap_data: dict
        """
        session = self.SessionLocal()
        try:
            obj = UniswapSwap(
                id=swap_data.get('id'),
                pool_address=swap_data.get('pool_address'),
                timestamp=swap_data.get('timestamp'),
                ts=swap_data.get('ts'),
                amount0=swap_data.get('amount0'),
                amount1=swap_data.get('amount1'),
                sqrtPriceX96=swap_data.get('sqrtPriceX96'),
                tick=swap_data.get('tick'),
                tx_hash=swap_data.get('tx_hash'),
                raw=swap_data.get('raw')
            )
            session.merge(obj)  # merge 可用于 upsert
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error storing uniswap swap: {e}")
            return False
        finally:
            session.close()

    def store_binance_kline(self, kline_data):
        """
        存储单条 binance_klines 记录；主键为 (symbol, open_time_ms)
        kline_data: dict
        """
        session = self.SessionLocal()
        try:
            obj = BinanceKline(
                symbol=kline_data.get('symbol'),
                open_time_ms=kline_data.get('open_time_ms'),
                open_time=kline_data.get('open_time'),
                open=kline_data.get('open'),
                high=kline_data.get('high'),
                low=kline_data.get('low'),
                close=kline_data.get('close'),
                volume=kline_data.get('volume'),
                quote_av=kline_data.get('quote_av'),
                trades=kline_data.get('trades'),
                raw=kline_data.get('raw')
            )
            session.merge(obj)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error storing binance kline: {e}")
            return False
        finally:
            session.close()

    def get_uniswap_swaps(self):
        session = self.SessionLocal()
        try:
            swaps = session.query(UniswapSwap).order_by(UniswapSwap.ts).all()
            return [s.to_dict() for s in swaps]
        except Exception as e:
            print(f"Error fetching uniswap swaps: {e}")
            return []
        finally:
            session.close()

    def get_binance_klines(self):
        session = self.SessionLocal()
        try:
            klines = session.query(BinanceKline).order_by(BinanceKline.open_time).all()
            return [k.to_dict() for k in klines]
        except Exception as e:
            print(f"Error fetching binance klines: {e}")
            return []
        finally:
            session.close()

    def create_merged_trading_data(self):
        """创建合并的交易数据"""
        try:
            with self.engine.connect() as connection:
                # 使用事务
                with connection.begin():
                    # 首先清空表
                    connection.execute(text("TRUNCATE TABLE merged_trading_data"))
                    
                    # 使用 SQL 进行时间对齐和聚合
                    merge_sql = text("""
                    INSERT INTO merged_trading_data (
                        time_bucket, timestamp,
                        uniswap_swap_count, uniswap_total_volume_eth, uniswap_total_volume_usdt,
                        uniswap_avg_price, uniswap_min_price, uniswap_max_price, uniswap_price_std,
                        binance_open, binance_high, binance_low, binance_close, 
                        binance_volume, binance_quote_volume, binance_trades,
                        price_difference, price_ratio
                    )
                    SELECT 
                        -- 时间桶（按分钟对齐）
                        FROM_UNIXTIME(FLOOR(COALESCE(us.timestamp, bk.open_time_ms / 1000) / 60) * 60) as time_bucket,
                        FLOOR(COALESCE(us.timestamp, bk.open_time_ms / 1000) / 60) * 60 as timestamp,
                        
                        -- Uniswap 数据聚合
                        COALESCE(us.swap_count, 0) as uniswap_swap_count,
                        COALESCE(us.total_volume_eth, 0) as uniswap_total_volume_eth,
                        COALESCE(us.total_volume_usdt, 0) as uniswap_total_volume_usdt,
                        us.avg_price as uniswap_avg_price,
                        us.min_price as uniswap_min_price,
                        us.max_price as uniswap_max_price,
                        us.price_std as uniswap_price_std,
                        
                        -- Binance 数据
                        bk.open as binance_open,
                        bk.high as binance_high,
                        bk.low as binance_low,
                        bk.close as binance_close,
                        bk.volume as binance_volume,
                        bk.quote_av as binance_quote_volume,
                        bk.trades as binance_trades,
                        
                        -- 价格差异指标
                        (us.avg_price - bk.close) as price_difference,
                        (us.avg_price / bk.close) as price_ratio
                        
                    FROM (
                        -- Binance K线数据（按分钟）
                        SELECT 
                            FROM_UNIXTIME(FLOOR(open_time_ms / 1000 / 60) * 60) as time_bucket,
                            FLOOR(open_time_ms / 1000 / 60) * 60 as timestamp,
                            open, high, low, close, volume, quote_av, trades
                        FROM binance_klines 
                        WHERE symbol = 'ETHUSDT'
                    ) bk
                    
                    LEFT JOIN (
                        -- Uniswap Swap 数据聚合（按分钟）
                        SELECT 
                            FROM_UNIXTIME(FLOOR(timestamp / 60) * 60) as time_bucket,
                            FLOOR(timestamp / 60) * 60 as timestamp,
                            COUNT(*) as swap_count,
                            SUM(CASE WHEN amount0 > 0 THEN amount0 ELSE -amount0 END) as total_volume_eth,
                            SUM(CASE WHEN amount1 > 0 THEN amount1 ELSE -amount1 END) as total_volume_usdt,
                            AVG(price) as avg_price,
                            MIN(price) as min_price,
                            MAX(price) as max_price,
                            STDDEV(price) as price_std
                        FROM uniswap_swaps 
                        WHERE pool_address = :pool_address
                        GROUP BY FLOOR(timestamp / 60) * 60
                    ) us ON bk.time_bucket = us.time_bucket
                    
                    ORDER BY time_bucket
                    """)
                    
                    connection.execute(merge_sql, {'pool_address': config.POOL_ADDRESS.lower()})
            
            print("合并交易数据创建完成")
            return True
            
        except Exception as e:
            print(f"创建合并交易数据时出错: {e}")
            return False

    def get_merged_data_stats(self):
        """获取合并数据的统计信息"""
        try:
            with self.engine.connect() as connection:
                stats_sql = text("""
                SELECT 
                    COUNT(*) as total_records,
                    MIN(time_bucket) as start_time,
                    MAX(time_bucket) as end_time,
                    AVG(uniswap_swap_count) as avg_swaps_per_minute,
                    AVG(price_difference) as avg_price_diff,
                    AVG(price_ratio) as avg_price_ratio
                FROM merged_trading_data
                """)
                
                result = connection.execute(stats_sql).fetchone()
                
                if result:
                    print(f"合并数据统计:")
                    print(f"  总记录数: {result[0]}")
                    print(f"  时间范围: {result[1]} 到 {result[2]}")
                    print(f"  每分钟平均swap数量: {float(result[3] or 0):.2f}")
                    print(f"  平均价格差异: {float(result[4] or 0):.4f}")
                    print(f"  平均价格比率: {float(result[5] or 0):.4f}")
                
                return result
                
        except Exception as e:
            print(f"获取合并数据统计时出错: {e}")
            return None