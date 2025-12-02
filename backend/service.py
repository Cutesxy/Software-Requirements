import time
import random
import config 
import pandas as pd
from sqlalchemy import create_engine

# ==========================================
# 队友任务说明:
# 1. 请在此文件中实现从数据库/CSV 读取数据的逻辑
# 2. 可以使用 config.MYSQL_URI 连接数据库
# ==========================================

def get_price_data(start_ts, end_ts, interval=15):
    """
    获取 CEX 和 DEX 的价格数据
    """

    csv = pd.read_csv("merged_trading_data.csv")
    
    print(f"[后端日志] 获取价格: {start_ts}-{end_ts}, 粒度: {interval}")
    
    # --- Mock 数据 (根据时间范围动态生成) ---
    cex_mock_data = []
    dex_mock_data = []
    current_ts = start_ts
    step = interval * 60  # interval 以分钟为单位，转换为秒
    # 限制最大点数，防止前端卡死 (Mock用)
    max_points = 500
    count = 0
    
    # 将 DataFrame 转为记录列表并逐条处理（避免直接迭代 DataFrame 导致获取到列名）
    records = csv.to_dict(orient='records')
    for item in records:
        # 兼容字段名不同的情况，优先使用 timestamp 或 ts
        ts = int(item.get('timestamp'))
        if ts < current_ts:
            continue
        if ts > end_ts:
            break
        
        cex_mock_data.append({
            "t": ts,
            "p": item.get('binance_close'),
            "v": item.get('binance_volume'),
            "lat_ms": random.randint(10, 50)
        })
        if item.get('uniswap_avg_price') is None or item.get('uniswap_avg_price') == 0.0:
            continue
        dex_mock_data.append({
            "t": ts,
            "p": item.get('uniswap_avg_price'),
            "v": item.get('uniswap_total_volume_eth'),
            "lat_ms": random.randint(10, 50)
        })

        # interval 参数以分钟为单位，转换为秒
        current_ts += step
        count += 1
        if count >= max_points:
            break

    return { "cex": cex_mock_data, "dex": dex_mock_data }

def get_spread_data(start_ts, end_ts, interval=15):
    """
    获取价差数据
    """
    csv = pd.read_csv("merged_trading_data.csv")
    records = csv.to_dict(orient='records')

    current_ts = start_ts
    step = interval * 60  # interval 以分钟为单位，转换为秒
    # 限制最大点数，防止前端卡死 (Mock用)
    max_points = 500
    count = 0

    mock_data = []

    for item in records:
        # 兼容字段名不同的情况，优先使用 timestamp 或 ts
        ts = int(item.get('timestamp'))
        if ts < current_ts:
            continue
        uniswap_price = item.get('uniswap_avg_price')
        if uniswap_price is None or uniswap_price == 0.0:
            continue
        if ts > end_ts:
            break
        mock_data.append({
            "t": ts,
            "spread": item.get('price_difference'),
            "spreadPct": item.get('price_ratio'),
            "z": abs(item.get('price_difference') / item.get('uniswap_price_std')) if item.get('uniswap_price_std') else 0,
            "cexPrice": item.get('binance_close'),
            "dexPrice": uniswap_price
        })
        current_ts += step
        count += 1
        if count >= max_points:
            break
    return mock_data


def get_heatmap_data(start_ts, end_ts):
    signal_csv = pd.read_csv("arbitrage_signals.csv")
    signals_records = signal_csv.to_dict(orient='records')

    mock_data = []
    for item in signals_records:
        timestamp = int(item.get('timestamp'))
        if timestamp < start_ts:
            continue
        if timestamp > end_ts:
            break
        mock_data.append([random.randint(0, 20), random.randint(0, 20), round(random.random()*5, 2)])
    return mock_data

def get_correlation_data(start_ts, end_ts):
    signal_csv = pd.read_csv("arbitrage_signals.csv")
    signals_records = signal_csv.to_dict(orient='records')
    
    mock_data = []
    for item in signals_records:
        ts = int(item.get('timestamp'))
        if ts < start_ts:
            continue
        if ts > end_ts:
            break
        mock_data.append({
            "lag": random.randint(0, 10),
            "correlation": round(0.9 - random.random()*0.1, 3)
        })
    return mock_data

def run_backtest(start_ts, end_ts, z_threshold, trade_size_usdt):
    """
    执行回测
    :param trade_size_usdt: 每次交易的 USDT 金额 (对应 config.ANALYSIS_PARAMS['trade_size_usdt'])
    """
    signal_csv = pd.read_csv("arbitrage_signals.csv")
    signals_records = signal_csv.to_dict(orient='records')
    data_csv = pd.read_csv("merged_trading_data.csv")
    data_records = data_csv.to_dict(orient='records')

    print(f"[后端日志] 回测: Z阈值={z_threshold}, 单笔金额={trade_size_usdt} USDT")

    signals = []
    total_trades = 0
    winning_trades = 0
    total_profit = 0.0

    for item in data_records:
        timestamp = item.get('timestamp')
        if timestamp < start_ts:
            continue
        if timestamp > end_ts:
            break
        total_trades += item.get('uniswap_swap_count', 0)

    for item in signals_records:
        timestamp = item.get('timestamp')
        if timestamp < start_ts:
            continue
        if timestamp > end_ts:
            break
        net_profit = item.get('net_profit')
        z = abs(item.get('zscore'))
        if z < z_threshold:
            continue
        signals.append({
            "id": item.get('id'),
            "timestamp": timestamp,
            "direction": item.get('direction'),
            "spread": item.get('price_difference'),
            "spreadPct": item.get('uniswap_avg_price') / item.get('binance_close_price'),
            "zScore": z,
            "swapCount": item.get('swap_count'),
            "size": item.get('size'),
            "grossProfit": item.get('gross_profit'),
            "totalCost": item.get('binance_fee') + item.get('uniswap_fee') + item.get('gas_cost'),
            "netProfit": net_profit,
            "confidence": item.get('confidence'),
            "cexPrice": item.get('binance_close_price'),
            "dexPrice": item.get('uniswap_avg_price'),
            "params": {"zThreshold": z_threshold, "sizeUSDT": trade_size_usdt}
        })
        winning_trades += item.get('swap_count', 0)

    # 6. 构造统计结果
    stats = {
        "totalTrades": total_trades,
        "winningTrades": winning_trades,
        "winRate": winning_trades / total_trades if total_trades > 0 else 0,
        "totalProfit": total_profit,
        "avgProfit": total_profit / winning_trades if winning_trades > 0 else 0,
        "equity": [
            {"time": start_ts, "equity": 10000}, 
            {"time": start_ts+3600, "equity": 10000 + total_profit}
        ]
    }
    
    return signals, stats



### 测试代码 ###
def main():
    start_ts = 1756684931
    end_ts =  1756700000
    interval = 15

    price_data = get_price_data(start_ts, end_ts, interval)
    spread_data_df = get_spread_data(start_ts, end_ts, interval)
    heatmap_data = get_heatmap_data(start_ts, end_ts)
    correlation_data = get_correlation_data(start_ts, end_ts)
    backtest_signals, backtest_stats = run_backtest(start_ts, end_ts, z_threshold=2.0, trade_size_usdt=100)

    print("cex_df:", price_data["cex"])
    print("dex_df:", price_data["dex"])
    print("spread_data_df:", spread_data_df)
    print("heatmap_data:", heatmap_data)
    print("correlation_data:", correlation_data)
    print("backtest_signals:", backtest_signals)
    print("backtest_stats:", backtest_stats)

if __name__ == "__main__":
    main()
    