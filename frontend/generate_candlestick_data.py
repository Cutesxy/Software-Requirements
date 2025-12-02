#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
K线图数据生成脚本
从 processed_data.json 生成按天聚合的K线数据
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

def load_processed_data(file_path):
    """加载 processed_data.json 文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def aggregate_to_daily_candles(data_items):
    """
    将原始数据聚合为按天的K线数据
    
    Args:
        data_items: 原始数据数组 [[timestamp, uData, bData], ...]
    
    Returns:
        dict: {
            'dex': [{time, open, close, high, low, volume}, ...],
            'cex': [{time, open, close, high, low, volume}, ...]
        }
    """
    # 按天分组
    dex_buckets = defaultdict(lambda: {'prices': [], 'volumes': []})
    cex_buckets = defaultdict(lambda: {'prices': [], 'volumes': []})
    
    for item in data_items:
        if len(item) < 3:
            continue
            
        timestamp_sec = item[0]  # 秒级时间戳
        u_data = item[1]  # Uniswap 数据 [sc, ve, vu, ap, mp, xp, sd]
        b_data = item[2]  # Binance 数据 [o, h, l, c, v, qv, t]
        
        # 转换为毫秒时间戳
        timestamp_ms = int(timestamp_sec * 1000)
        
        # 计算当天的开始时间（毫秒时间戳，当天 00:00:00）
        dt = datetime.fromtimestamp(timestamp_sec)
        day_start = datetime(dt.year, dt.month, dt.day, 0, 0, 0)
        day_key = int(day_start.timestamp() * 1000)  # 转换为毫秒时间戳
        
        # Uniswap 数据
        # uData: [sc, ve, vu, ap, mp, xp, sd]
        # ap (索引3) = 平均价格
        # ve (索引1) = 成交量
        if len(u_data) > 3:
            dex_price = float(u_data[3])  # ap: 平均价格
            dex_volume = float(u_data[1]) if len(u_data) > 1 else 0.0  # ve: 成交量
            
            dex_buckets[day_key]['prices'].append({
                'time': timestamp_ms,
                'price': dex_price
            })
            dex_buckets[day_key]['volumes'].append(dex_volume)
        
        # Binance 数据
        # bData: [o, h, l, c, v, qv, t]
        # c (索引3) = 收盘价
        # v (索引4) = 成交量
        if len(b_data) > 4:
            cex_price = float(b_data[3])  # c: 收盘价
            cex_volume = float(b_data[4])  # v: 成交量
            
            cex_buckets[day_key]['prices'].append({
                'time': timestamp_ms,
                'price': cex_price
            })
            cex_buckets[day_key]['volumes'].append(cex_volume)
    
    # 转换为K线格式
    def convert_to_candles(buckets):
        candles = []
        for day_key in sorted(buckets.keys()):
            bucket = buckets[day_key]
            if not bucket['prices']:
                continue
            
            # 按时间排序
            prices_sorted = sorted(bucket['prices'], key=lambda x: x['time'])
            
            open_price = prices_sorted[0]['price']  # 开盘价：当天第一个价格
            close_price = prices_sorted[-1]['price']  # 收盘价：当天最后一个价格
            high_price = max(p['price'] for p in prices_sorted)  # 最高价
            low_price = min(p['price'] for p in prices_sorted)  # 最低价
            total_volume = sum(bucket['volumes'])  # 总成交量
            
            candles.append({
                'time': day_key,  # 当天开始时间（毫秒时间戳）
                'open': round(open_price, 2),
                'close': round(close_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'volume': round(total_volume, 2)
            })
        
        return candles
    
    return {
        'dex': convert_to_candles(dex_buckets),
        'cex': convert_to_candles(cex_buckets)
    }

def generate_candlestick_data(input_file, output_file):
    """
    生成K线数据并保存为JSON
    
    Args:
        input_file: 输入的 processed_data.json 文件路径
        output_file: 输出的K线数据JSON文件路径
    """
    print(f"正在加载数据: {input_file}")
    data = load_processed_data(input_file)
    
    if 'data' not in data or not data['data']:
        print("错误: 数据文件格式不正确或数据为空")
        return
    
    print(f"数据点数量: {len(data['data'])}")
    print("正在聚合为按天的K线数据...")
    
    # 聚合数据
    candles = aggregate_to_daily_candles(data['data'])
    
    # 构建输出数据
    output_data = {
        'meta': {
            'generatedAt': datetime.now().isoformat(),
            'sourceFile': input_file,
            'totalDataPoints': len(data['data']),
            'dexCandleCount': len(candles['dex']),
            'cexCandleCount': len(candles['cex']),
            'interval': '1day',
            'description': '按天聚合的K线数据，每天包含开盘、收盘、最高、最低价格和总成交量'
        },
        'dex': candles['dex'],
        'cex': candles['cex']
    }
    
    # 保存为JSON文件
    print(f"正在保存到: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 成功生成K线数据!")
    print(f"  - DEX K线数量: {len(candles['dex'])}")
    print(f"  - CEX K线数量: {len(candles['cex'])}")
    print(f"  - 输出文件: {output_file}")

def main():
    """主函数"""
    # 默认文件路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, 'public', 'processed_data.json')
    output_file = os.path.join(script_dir, 'public', 'candlestick_daily.json')
    
    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误: 找不到输入文件: {input_file}")
        print("请确保 processed_data.json 文件存在于 public 目录")
        return
    
    # 生成K线数据
    try:
        generate_candlestick_data(input_file, output_file)
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

