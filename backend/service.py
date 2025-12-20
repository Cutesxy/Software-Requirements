import pandas as pd
import numpy as np
import random
import config

class DataLoader:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            print("[System] Loading CSV data into memory...")
            cls._instance = super(DataLoader, cls).__new__(cls)
            try:
                cls._instance.df_data = pd.read_csv(config.DATA_CSV_PATH)
                cls._instance.df_signals = pd.read_csv(config.SIGNALS_CSV_PATH)
            except Exception as e:
                print(f"[Error] Failed to load CSV: {e}")
                cls._instance.df_data = pd.DataFrame()
                cls._instance.df_signals = pd.DataFrame()
        return cls._instance

data_loader = DataLoader()

def _filter_df(df, start_ts, end_ts):
    if df.empty: return df
    mask = (df['timestamp'] >= start_ts) & (df['timestamp'] <= end_ts)
    return df.loc[mask]

def _safe_float(val):
    """辅助函数：处理 NaN，转为 None 以便前端 JSON 解析"""
    if pd.isna(val) or np.isnan(val) or np.isinf(val):
        return None
    return float(val)

def get_price_data(start_ts, end_ts, interval='15m'):
    df = _filter_df(data_loader.df_data, start_ts, end_ts)
    if df.empty: return { "cex": [], "dex": [] }

    total_points = len(df)
    limit = 1000 
    step = max(1, total_points // limit)
    sampled_df = df.iloc[::step]
    
    cex_data = []
    dex_data = []
    
    for _, row in sampled_df.iterrows():
        ts = int(row['timestamp'])
        cex_p = _safe_float(row.get('binance_close'))
        dex_p = _safe_float(row.get('uniswap_avg_price'))
        
        if cex_p is not None:
            cex_data.append({
                "t": ts, "p": cex_p, 
                "v": _safe_float(row.get('binance_volume')), 
                "lat_ms": random.randint(10, 50)
            })
        
        if dex_p is not None and dex_p > 0:
            dex_data.append({
                "t": ts, "p": dex_p, 
                "v": _safe_float(row.get('uniswap_total_volume_eth')), 
                "lat_ms": random.randint(10, 50)
            })

    return { "cex": cex_data, "dex": dex_data }

def get_spread_data(start_ts, end_ts, interval='15m'):
    df = _filter_df(data_loader.df_data, start_ts, end_ts)
    limit = 1000
    step = max(1, len(df) // limit)
    sampled_df = df.iloc[::step]

    mock_data = []
    for _, row in sampled_df.iterrows():
        ts = int(row['timestamp'])
        dex_p = row.get('uniswap_avg_price')
        
        # 严格过滤 NaN
        if pd.isna(dex_p) or dex_p == 0: continue

        std = row.get('uniswap_price_std', 0)
        diff = row.get('price_difference', 0)
        z_val = abs(diff / std) if std and std != 0 and not pd.isna(std) else 0

        mock_data.append({
            "t": ts,
            "spread": _safe_float(diff),
            "spreadPct": _safe_float(row.get('price_ratio')),
            "z": _safe_float(z_val),
            "cexPrice": _safe_float(row.get('binance_close')),
            "dexPrice": _safe_float(dex_p)
        })
        
    return mock_data

def get_heatmap_data(start_ts, end_ts):
    mock_data = []
    for hour in range(24):
        for day in range(7):
            mock_data.append([day, hour, round(random.random() * 5, 2)])
    return mock_data

def get_correlation_data(start_ts, end_ts):
    mock_data = []
    for lag in range(20):
        mock_data.append({
            "lag": lag,
            "correlation": round(0.95 * (0.9 ** lag), 3)
        })
    return mock_data

def run_backtest(start_ts, end_ts, z_threshold, trade_size_usdt):
    df_sig = _filter_df(data_loader.df_signals, start_ts, end_ts)
    signals = []
    
    capital = 10000.0 
    current_equity = capital
    equity_curve = [{"time": start_ts, "equity": capital}]
    
    winning_trades = 0
    total_trades_count = 0
    total_profit = 0.0
    
    # 费率配置
    FEE_RATE = 0.003 + 0.001 # 0.4%
    GAS_COST = 50.0 # 假设每次 Gas 50U

    for _, item in df_sig.iterrows():
        z = abs(item.get('zscore', 0))
        if pd.isna(z) or z < z_threshold: continue
            
        total_trades_count += 1
        
        # --- 收益核心计算逻辑 ---
        spread_pct = abs(item.get('price_difference', 0)) / item.get('binance_close_price', 1)
        
        # 毛利 (Gross Profit) = 投入 * 价差百分比
        gross_profit = trade_size_usdt * spread_pct
        
        # 成本 (Total Cost) = 手续费 + Gas
        total_cost = (trade_size_usdt * FEE_RATE) + GAS_COST
        
        # 净利 (Net Profit)
        net_profit = gross_profit - total_cost
        
        # --- 统计更新 ---
        total_profit += net_profit
        current_equity += net_profit
        
        if net_profit > 0: winning_trades += 1

        # Mock 置信度：Z-score 越高置信度越高，映射到 0.5 - 0.99
        confidence = min(0.99, 0.5 + (z / 10.0))

        signals.append({
            "id": str(item.get('id', total_trades_count)),
            "time": int(item.get('timestamp')),
            "direction": item.get('direction', 'Long'),
            "spread": _safe_float(item.get('price_difference')),
            "spreadPct": _safe_float(spread_pct),
            "zScore": _safe_float(z),
            "size": trade_size_usdt,
            # [新增字段] 补全前端需求
            "grossProfit": round(gross_profit, 2),
            "totalCost": round(total_cost, 2),
            "netProfit": round(net_profit, 2),
            "confidence": round(confidence, 2),
            # ------------
            "cexPrice": _safe_float(item.get('binance_close_price')),
            "dexPrice": _safe_float(item.get('uniswap_avg_price')),
            "params": {"zThreshold": z_threshold}
        })
        
        equity_curve.append({
            "time": int(item.get('timestamp')),
            "equity": round(current_equity, 2)
        })

    win_rate = winning_trades / total_trades_count if total_trades_count > 0 else 0
    avg_profit = total_profit / total_trades_count if total_trades_count > 0 else 0
    
    # Max Drawdown
    equity_values = [e['equity'] for e in equity_curve]
    peak = equity_values[0]
    max_drawdown = 0.0
    for val in equity_values:
        if val > peak: peak = val
        dd = (peak - val) / peak
        if dd > max_drawdown: max_drawdown = dd

    # Sharpe Ratio
    sharpe_ratio = 0
    if len(equity_values) > 1:
        returns = pd.Series(equity_values).pct_change().dropna()
        if returns.std() != 0:
            sharpe_ratio = returns.mean() / returns.std()

    stats = {
        "totalTrades": total_trades_count,
        "winningTrades": winning_trades,
        "winRate": round(win_rate, 4),
        "totalProfit": round(total_profit, 2),
        "avgProfit": round(avg_profit, 2),
        "maxDrawdown": round(max_drawdown, 4),
        "sharpeRatio": round(sharpe_ratio, 4),
        "equity": equity_curve,
        "signals": signals 
    }
    
    return signals, stats