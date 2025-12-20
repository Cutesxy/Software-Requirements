import requests
import json
import time

# 配置后端地址 (根据你的日志，端口是 5319)
BASE_URL = "http://127.0.0.1:5319"

# 定义测试用的时间范围 (2025年9月1日 - 9月2日，测试2天的数据即可)
# 2025-09-01 00:00:00 UTC = 1756684800
# 2025-09-02 00:00:00 UTC = 1756771200
START_TS = 1756684800
END_TS = 1756771200

def print_json(data, label):
    """辅助函数：美化打印 JSON，但限制长度防止刷屏"""
    print(f"\n{'='*20} {label} {'='*20}")
    if isinstance(data, list):
        print(f"返回数据类型: List (共 {len(data)} 条)")
        print("前 1 条示例:")
        print(json.dumps(data[:1], indent=2))
    elif isinstance(data, dict):
        print(f"返回数据类型: Dict (Keys: {list(data.keys())})")
        # 针对 price 这种嵌套结构做特殊处理
        if "cex" in data:
            print(f"CEX 数据点数: {len(data['cex'])}, DEX 数据点数: {len(data['dex'])}")
            print("CEX 第1条:", json.dumps(data['cex'][:1], indent=2))
        else:
            print(json.dumps(data, indent=2))
    else:
        print(data)

def test_endpoint(endpoint, params):
    url = f"{BASE_URL}{endpoint}"
    print(f"\n[Request] GET {url}")
    print(f"Params: {params}")
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # 检查 HTTP 错误
        data = response.json()
        return data
    except Exception as e:
        print(f"[Error] 请求失败: {e}")
        return None

def main():
    print(f"开始测试后端服务: {BASE_URL}")

    # ==========================================
    # 测试 1: 获取价格数据 (Price)
    # ==========================================
    price_params = {
        "start": START_TS,
        "end": END_TS,
        "type": "price",
        "interval": "15m"
    }
    data = test_endpoint("/app/getdata", price_params)
    if data: print_json(data, "Price Data 结果")

    # ==========================================
    # 测试 2: 获取价差数据 (Spread)
    # ==========================================
    spread_params = {
        "start": START_TS,
        "end": END_TS,
        "type": "spread"
    }
    data = test_endpoint("/app/getdata", spread_params)
    if data: print_json(data, "Spread Data 结果")

    # ==========================================
    # 测试 3: 获取回测统计 (Backtest Stats)
    # ==========================================
    backtest_params = {
        "start": START_TS,
        "end": END_TS,
        "type": "backtest",
        "zThreshold": 2.0,
        "tradeSize": 5000 # 测试自定义交易金额
    }
    data = test_endpoint("/app/getresult", backtest_params)
    if data: print_json(data, "Backtest Stats 结果")

    # ==========================================
    # 测试 4: 获取交易信号列表 (Signals)
    # ==========================================
    signal_params = {
        "start": START_TS,
        "end": END_TS,
        "type": "signals",
        "zThreshold": 2.0
    }
    data = test_endpoint("/app/getresult", signal_params)
    if data: print_json(data, "Signals List 结果")

    # ==========================================
    # 测试 5: 获取热力图 (Heatmap)
    # ==========================================
    heatmap_params = {"start": START_TS, "end": END_TS, "type": "heatmap"}
    data = test_endpoint("/app/getdata", heatmap_params) # 注意这里调用 test_endpoint
    if data: print_json(data, "Heatmap Data 结果")

    # ==========================================
    # 测试 6: 获取相关性 (Correlation)
    # ==========================================
    corr_params = {"start": START_TS, "end": END_TS, "type": "correlation"}
    data = test_endpoint("/app/getdata", corr_params)
    if data: print_json(data, "Correlation Data 结果")

if __name__ == "__main__":
    main()