from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, BigInteger, Numeric, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
import pandas as pd
import config

Base = declarative_base()

# 新增 ORM 映射，匹配 init.sql 中的表结构
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
        # 清空两张表
        session = self.SessionLocal()
        try:
            session.query(UniswapSwap).delete()
            session.query(BinanceKline).delete()
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error clearing tables during init_db: {e}")
        finally:
            session.close()

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