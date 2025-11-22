"""
get_data.py - 拉取数据并保存到 MySQL 的主程序（使用 config.py 中的时间范围）
"""
from dateutil import parser
from datetime import timedelta, datetime
import requests
import time
import json
from decimal import Decimal
import config
from dbMapper import DBMapper

class DataFetcher:
    def __init__(self, db_mapper):
        self.db = db_mapper
        self.uniswap_swaps_count = 0
        self.binance_klines_count = 0
        
    def fetch_uniswap_swaps(self, start_timestamp, end_timestamp):
        """
        从 Dune Analytics 获取 Uniswap V3 交易数据（处理分页）
        """
        print(f"Fetching Uniswap swaps from {datetime.fromtimestamp(start_timestamp)} to {datetime.fromtimestamp(end_timestamp)}")
        
        all_swaps = []
        skip = 0
        batch_size = 1000  # 每次最多返回1000条记录
        
        # Dune API URL
        DUNE_API_URL = "https://api.dune.com/api/v1/query/execute"  # Dune API endpoint
        
        # GraphQL 查询（根据你的需求调整时间范围和池地址）
        query = """
        query {
          swaps(
            where: {
              pool: "0x11b815efb8f581194ae79006d24e0d814b7697f6"
              timestamp_gte: %d
              timestamp_lte: %d
            }
            orderBy: timestamp
            orderDirection: asc
          ) {
            id
            timestamp
            amount0
            amount1
            transaction {
              id
            }
          }
        }
        """ % (start_timestamp, end_timestamp)

        headers = {
            "Authorization": "Bearer 4Vg7XCgBeXvWBoowfRKXmnXZnv85m7dx",
            "Content-Type": "application/json"
        }
        
        # 请求 Dune 数据
        response = requests.post(DUNE_API_URL, json={"query": query}, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'swaps' in data['data']:
                swaps = data['data']['swaps']
                all_swaps.extend(swaps)
                print(f"Fetched {len(swaps)} Uniswap swaps (total: {len(all_swaps)})")
                
            else:
                print("Error in Dune response:", data.get('errors', 'Unknown error'))
        else:
            print(f"Dune API error: {response.status_code}")

        print(f"Total Uniswap swaps fetched: {len(all_swaps)}")
        return all_swaps
    
    def fetch_binance_klines(self, start_timestamp, end_timestamp):
        """
        从 Binance 获取 K线数据（处理分页）
        """
        print(f"Fetching Binance klines from {datetime.fromtimestamp(start_timestamp)} to {datetime.fromtimestamp(end_timestamp)}")
        
        all_klines = []
        
        # 将时间戳转换为毫秒
        start_time_ms = int(start_timestamp * 1000)
        end_time_ms = int(end_timestamp * 1000)
        current_start = start_time_ms
        
        # Binance K线限制：每次最多1000根K线
        limit = 1000
        interval_ms = 60 * 1000 * limit  # 1分钟K线 * 1000 = 1000分钟
        
        while current_start < end_time_ms:
            current_end = min(current_start + interval_ms, end_time_ms)
            
            try:
                url = "https://api.binance.com/api/v3/klines"
                params = {
                    'symbol': config.BINANCE_SYMBOL,
                    'interval': '1m',
                    'startTime': current_start,
                    'endTime': current_end,
                    'limit': limit
                }
                
                response = requests.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    klines = response.json()
                    if not klines:
                        break  # 没有更多数据了
                        
                    all_klines.extend(klines)
                    print(f"Fetched {len(klines)} Binance klines (total: {len(all_klines)})")
                    
                    # 移动到下一时间段
                    current_start = int(klines[-1][0]) + 60000  # 最后一个K线的时间 + 1分钟
                    
                    # 避免请求过于频繁
                    time.sleep(0.1)
                else:
                    print(f"Binance API error: {response.status_code}, response: {response.text}")
                    break
                    
            except Exception as e:
                print(f"Error fetching Binance data: {e}")
                break
                
        print(f"Total Binance klines fetched: {len(all_klines)}")
        return all_klines
    
    def process_uniswap_swaps(self, swaps):
        """
        处理 Uniswap 交易数据并保存到数据库
        """
        processed_count = 0
        
        for swap in swaps:
            try:
                # 转换时间戳为 datetime
                timestamp = int(swap['timestamp'])
                ts_datetime = datetime.fromtimestamp(timestamp)
                
                # 计算价格
                amount0 = Decimal(swap['amount0'])
                amount1 = Decimal(swap['amount1'])
                
                # 确定哪个是 ETH，哪个是 USDT
                token0_symbol = swap['token0']['symbol']
                token1_symbol = swap['token1']['symbol']
                
                price = None
                if token0_symbol == 'WETH' and token1_symbol == 'USDT':
                    # amount0 是 ETH, amount1 是 USDT
                    if amount0 != 0:
                        price = abs(amount1) / abs(amount0)  # USDT per ETH
                elif token1_symbol == 'WETH' and token0_symbol == 'USDT':
                    # amount1 是 ETH, amount0 是 USDT
                    if amount1 != 0:
                        price = abs(amount0) / abs(amount1)  # USDT per ETH
                
                swap_data = {
                    'id': swap['id'],
                    'pool_address': config.POOL_ADDRESS.lower(),
                    'timestamp': timestamp,
                    'ts': ts_datetime,
                    'amount0': amount0,
                    'amount1': amount1,
                    'sqrtPriceX96': swap['sqrtPriceX96'],
                    'tick': int(swap['tick']) if swap['tick'] is not None else None,
                    'tx_hash': swap['transaction']['id'],
                    'raw': json.dumps(swap)  # 存储原始数据
                }
                
                # 保存到数据库
                if self.db.store_uniswap_swap(swap_data):
                    processed_count += 1
                    
            except Exception as e:
                print(f"Error processing Uniswap swap {swap.get('id', 'unknown')}: {e}")
                continue
        
        self.uniswap_swaps_count = processed_count
        print(f"Processed and saved {processed_count} Uniswap swaps to database")
        return processed_count
    
    def process_binance_klines(self, klines):
        """
        处理 Binance K线数据并保存到数据库
        """
        processed_count = 0
        
        for kline in klines:
            try:
                # 解析K线数据
                open_time_ms = int(kline[0])
                open_time = datetime.fromtimestamp(open_time_ms / 1000.0)
                
                kline_data = {
                    'symbol': config.BINANCE_SYMBOL,
                    'open_time_ms': open_time_ms,
                    'open_time': open_time,
                    'open': Decimal(kline[1]),
                    'high': Decimal(kline[2]),
                    'low': Decimal(kline[3]),
                    'close': Decimal(kline[4]),
                    'volume': Decimal(kline[5]),
                    'quote_av': Decimal(kline[7]),  # 报价资产成交量
                    'trades': int(kline[8]),  # 成交笔数
                    'raw': json.dumps(kline)  # 存储原始数据
                }
                
                # 保存到数据库
                if self.db.store_binance_kline(kline_data):
                    processed_count += 1
                    
            except Exception as e:
                print(f"Error processing Binance kline: {e}")
                continue
        
        self.binance_klines_count = processed_count
        print(f"Processed and saved {processed_count} Binance klines to database")
        return processed_count

def main():
    # 初始化数据库
    db = DBMapper()
    db.init_db()
    print("Database initialized")
    
    fetcher = DataFetcher(db)
    
    # 从 config 中读取时间范围（字符串），并转为 datetime
    start_dt = parser.isoparse(config.START_DATE)
    end_dt = parser.isoparse(config.END_DATE)
    # 包含结束日全天
    end_dt = end_dt + timedelta(days=1) - timedelta(seconds=1)
    
    # 转换为时间戳
    start_timestamp = int(start_dt.timestamp())
    end_timestamp = int(end_dt.timestamp())
    
    print(f"Fetching data from {start_dt} to {end_dt}")
    print(f"Time range: {start_timestamp} to {end_timestamp}")
    
    # 获取并处理 Uniswap 数据
    print("\n=== Fetching Uniswap Data ===")
    uniswap_swaps = fetcher.fetch_uniswap_swaps(start_timestamp, end_timestamp)
    if uniswap_swaps:
        fetcher.process_uniswap_swaps(uniswap_swaps)
    
    # 获取并处理 Binance 数据
    print("\n=== Fetching Binance Data ===")
    binance_klines = fetcher.fetch_binance_klines(start_timestamp, end_timestamp)
    if binance_klines:
        fetcher.process_binance_klines(binance_klines)
    
    # 输出总结
    print("\n=== Data Fetching Summary ===")
    print(f"Uniswap swaps: {fetcher.uniswap_swaps_count}")
    print(f"Binance klines: {fetcher.binance_klines_count}")
    print("Data fetching completed!")

if __name__ == "__main__":
    main()