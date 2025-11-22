#!/usr/bin/env python3
"""
简单测试脚本：验证数据库连接、插入与查询（uniswap_swaps 与 binance_klines）。
运行方式（在工作区根或 SRE 目录）：
- 在 SRE 目录下运行： python test_db.py
- 在工作区根运行： python SRE/test_db.py
"""
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import sys

from dbMapper import DBMapper

def iso_now():
    return datetime.now(timezone.utc).replace(microsecond=0)


def main():
    db = DBMapper()
    print("Initializing DB (create tables if not exists)...")
    db.init_db()
    
    n = 10

    ts = iso_now()

    print("\n-- Testing Uniswap swap insert --")
    for i in range(n):
        swap = {
            "id": f"test-swap-{i}",
            "pool_address": "0x" + "1" * 40,
            "timestamp": int(ts.timestamp()),
            "ts": ts,
            "amount0": Decimal("0.123456789012345678"),
            "amount1": Decimal("1.234567890123456789"),
            "sqrtPriceX96": "0xabc",
            "tick": 123,
            "tx_hash": "0x" + "a" * 64,
            "raw": {"note": "test swap"},
        }
        ok = db.store_uniswap_swap(swap)
        print("store_uniswap_swap returned:", ok)
    rows = db.get_uniswap_swaps()
    print(f"Queried uniswap swaps -> found {len(rows)} rows")
    if rows:
        for r in rows:
            print(r)

    print("\n-- Testing Binance kline insert --")
    for i in range(n):
        kline = {
            "symbol": "TESTUSDT",
            "open_time_ms": int(ts.timestamp() * 1000),
            "open_time": ts,
            "open": Decimal("100.1"),
            "high": Decimal("101.2"),
            "low": Decimal("99.9"),
            "close": Decimal("100.5"),
            "volume": Decimal("12345.6"),
            "quote_av": Decimal("1234567.8"),
        "trades": 12,
        "raw": {"note": "test kline"},
        }
        ok2 = db.store_binance_kline(kline)
        print("store_binance_kline returned:", ok2)

    klines = db.get_binance_klines()
    print(f"Queried klines -> found {len(klines)} rows")
    if klines:
        print(klines[0])

    print("\nTest finished.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error during test:", e)
        sys.exit(1)
