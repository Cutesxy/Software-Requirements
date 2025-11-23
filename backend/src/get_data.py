"""
get_data.py - 使用 Etherscan API 拉取数据并保存到 MySQL
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
        self.etherscan_swaps_count = 0
        self.binance_klines_count = 0
        
    def fetch_etherscan_swaps(self, start_block, end_block):
        """
        从 Etherscan 获取指定地址的 Token 交易数据（分批次获取）
        """
        print(f"Fetching Etherscan token transfers from block {start_block} to {end_block}")
        
        all_transfers = []
        batch_size = 5000  # 每批5000个区块
        
        current_block = start_block
        
        while current_block <= end_block:
            batch_end = min(current_block + batch_size - 1, end_block)
            print(f"Fetching blocks {current_block} to {batch_end}")
            
            batch_transfers = self._fetch_etherscan_batch(current_block, batch_end)
            if batch_transfers is not None:  # 只有在有数据时才添加
                all_transfers.extend(batch_transfers)
            
            current_block = batch_end + 1
            time.sleep(0.5)  # 避免速率限制
            
        print(f"Total token transfers fetched: {len(all_transfers)}")
        return all_transfers
    
    def _fetch_etherscan_batch(self, start_block, end_block):
        """
        获取单个批次的交易数据
        """
        batch_transfers = []
        page = 1
        page_size = 1000
        
        while True:
            try:
                # 使用正确的 v2 API URL
                url = "https://api.etherscan.io/v2/api"
                params = {
                    'chainid': 1,  # 保留 chainid 参数
                    'module': 'account',
                    'action': 'tokentx',
                    'address': config.POOL_ADDRESS,
                    'startblock': start_block,
                    'endblock': end_block,
                    'page': page,
                    'offset': page_size,
                    'sort': 'asc',
                    'apikey': config.ETHERSCAN_API_KEY
                }
                
                response = requests.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data['status'] == '1':
                        transfers = data['result']
                        if not transfers:
                            break  # 没有更多数据了
                            
                        batch_transfers.extend(transfers)
                        print(f"  Page {page}: {len(transfers)} transfers (batch total: {len(batch_transfers)})")
                        
                        # 如果返回的数据少于请求的数量，说明没有更多数据了
                        if len(transfers) < page_size:
                            break
                            
                        page += 1
                        
                        # 避免请求过于频繁
                        time.sleep(0.2)
                    else:
                        error_msg = data.get('message', 'Unknown error')
                        print(f"Etherscan API error: {error_msg}")
                        
                        # 如果是"No transactions found"，直接退出
                        if "No transactions found" in error_msg:
                            return batch_transfers
                        # 如果是其他错误，返回已获取的数据
                        else:
                            print(f"Stopping batch due to API error: {error_msg}")
                            return batch_transfers
                else:
                    print(f"HTTP error: {response.status_code}")
                    return batch_transfers
                    
            except Exception as e:
                print(f"Error fetching Etherscan data: {e}")
                return batch_transfers
                
        return batch_transfers
    
    def process_etherscan_transfers(self, transfers):
        """
        处理 Etherscan 交易数据，将同一交易哈希的 USDT 和 WETH 转账合并为 swap 事件
        """
        # 按交易哈希分组
        tx_groups = {}
        for transfer in transfers:
            tx_hash = transfer['hash']
            if tx_hash not in tx_groups:
                tx_groups[tx_hash] = []
            tx_groups[tx_hash].append(transfer)
        
        processed_swaps = []
        
        # 处理每个交易组
        for tx_hash, tx_transfers in tx_groups.items():
            # 一个完整的 swap 应该有两个转账（USDT 和 WETH）
            if len(tx_transfers) == 2:
                swap_data = self._create_swap_from_transfers(tx_transfers)
                if swap_data:
                    processed_swaps.append(swap_data)
            elif len(tx_transfers) > 2:
                # 如果有超过2个转账，可能是复杂的交易，尝试配对处理
                print(f"Warning: Transaction {tx_hash} has {len(tx_transfers)} transfers, attempting to pair...")
                paired_swaps = self._pair_complex_transfers(tx_transfers)
                processed_swaps.extend(paired_swaps)
        
        # 保存到数据库
        saved_count = 0
        for swap in processed_swaps:
            if self.db.store_uniswap_swap(swap):
                saved_count += 1
        
        self.etherscan_swaps_count = saved_count
        print(f"Processed and saved {saved_count} Uniswap swaps to database")
        return saved_count
    
    def _pair_complex_transfers(self, transfers):
        """
        处理复杂交易（一个交易中有多个转账）
        """
        swaps = []
        
        # 分离 USDT 和 WETH 转账
        usdt_transfers = [t for t in transfers if t['contractAddress'].lower() == config.USDT_CONTRACT.lower()]
        weth_transfers = [t for t in transfers if t['contractAddress'].lower() == config.WETH_CONTRACT.lower()]
        
        print(f"  Complex transaction analysis: {len(usdt_transfers)} USDT transfers, {len(weth_transfers)} WETH transfers")
        
        # 按转账金额排序，尝试匹配金额相近的转账
        usdt_transfers.sort(key=lambda x: abs(Decimal(x['value'])))
        weth_transfers.sort(key=lambda x: abs(Decimal(x['value'])))
        
        # 创建副本用于迭代
        usdt_remaining = usdt_transfers.copy()
        weth_remaining = weth_transfers.copy()
        
        # 尝试配对逻辑：寻找金额比例合理的配对
        for usdt_t in usdt_transfers:
            if usdt_t not in usdt_remaining:
                continue
                
            best_match = None
            best_ratio_diff = float('inf')
            
            usdt_value = abs(Decimal(usdt_t['value']) / Decimal(10 ** int(usdt_t['tokenDecimal'])))
            
            for weth_t in weth_remaining:
                weth_value = abs(Decimal(weth_t['value']) / Decimal(10 ** int(weth_t['tokenDecimal'])))
                
                if weth_value == 0:
                    continue
                    
                # 计算价格比例
                calculated_price = usdt_value / weth_value
                
                # 检查价格是否在合理范围内（例如 1000-5000 USDT/ETH）
                if 1000 <= calculated_price <= 5000:
                    ratio_diff = abs(calculated_price - 3000)  # 以3000为基准
                    
                    if ratio_diff < best_ratio_diff:
                        best_ratio_diff = ratio_diff
                        best_match = weth_t
            
            if best_match:
                swap_data = self._create_swap_from_transfers([usdt_t, best_match])
                if swap_data:
                    swaps.append(swap_data)
                    usdt_remaining.remove(usdt_t)
                    weth_remaining.remove(best_match)
        
        print(f"  Successfully paired {len(swaps)} swaps from complex transaction")
        return swaps
    
    def _create_swap_from_transfers(self, transfers):
        """
        从两个转账记录创建 swap 数据
        """
        try:
            # 首先获取交易哈希
            tx_hash = transfers[0]['hash']
            
            # 识别 USDT 和 WETH 转账
            usdt_transfer = None
            weth_transfer = None
            
            for transfer in transfers:
                contract_address = transfer['contractAddress'].lower()
                if contract_address == config.USDT_CONTRACT.lower():
                    usdt_transfer = transfer
                elif contract_address == config.WETH_CONTRACT.lower():
                    weth_transfer = transfer
            
            if not usdt_transfer or not weth_transfer:
                return None
            
            # 确定交易方向
            pool_address_lower = config.POOL_ADDRESS.lower()
            
            # 解析 USDT 数据
            usdt_value = Decimal(usdt_transfer['value']) / Decimal(10 ** int(usdt_transfer['tokenDecimal']))
            usdt_direction = 'out' if usdt_transfer['from'].lower() == pool_address_lower else 'in'
            
            # 解析 WETH 数据  
            weth_value = Decimal(weth_transfer['value']) / Decimal(10 ** int(weth_transfer['tokenDecimal']))
            weth_direction = 'out' if weth_transfer['from'].lower() == pool_address_lower else 'in'
            
            # 计算价格 (USDT per ETH)
            if weth_value > 0:
                price = abs(usdt_value) / abs(weth_value)
            else:
                price = Decimal('0')
            
            # 确定 amount0 (WETH) 和 amount1 (USDT)
            # 遵循 Uniswap V3 的约定：token0 = WETH, token1 = USDT
            if weth_direction == 'in':
                amount0 = weth_value  # 池子收到 WETH
                amount1 = -usdt_value  # 池子付出 USDT
            else:
                amount0 = -weth_value  # 池子付出 WETH  
                amount1 = usdt_value   # 池子收到 USDT
            
            # 创建 swap 数据
            swap_data = {
                'id': f"{tx_hash}_{transfers[0]['transactionIndex']}",
                'pool_address': config.POOL_ADDRESS.lower(),
                'timestamp': int(transfers[0]['timeStamp']),
                'ts': datetime.fromtimestamp(int(transfers[0]['timeStamp'])),
                'amount0': amount0,
                'amount1': amount1,
                'price': float(price),  # 存储计算出的价格
                'sqrtPriceX96': None,  # Etherscan 不提供这个数据
                'tick': None,          # Etherscan 不提供这个数据
                'tx_hash': tx_hash,
                'raw': json.dumps(transfers)  # 存储原始转账数据
            }
            
            return swap_data
            
        except Exception as e:
            print(f"Error creating swap from transfers: {e}")
            return None
    
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
    
    # 使用区块范围
    start_block = config.START_BLOCK
    end_block = config.END_BLOCK
    
    # 获取并处理 Etherscan 数据
    print("\n=== Fetching Etherscan Data ===")
    etherscan_transfers = fetcher.fetch_etherscan_swaps(start_block, end_block)
    if etherscan_transfers:
        fetcher.process_etherscan_transfers(etherscan_transfers)
    
    # 获取并处理 Binance 数据
    print("\n=== Fetching Binance Data ===")
    binance_klines = fetcher.fetch_binance_klines(start_timestamp, end_timestamp)
    if binance_klines:
        fetcher.process_binance_klines(binance_klines)
    
    # 输出总结
    print("\n=== Data Fetching Summary ===")
    print(f"Etherscan swaps: {fetcher.etherscan_swaps_count}")
    print(f"Binance klines: {fetcher.binance_klines_count}")
    print("Data fetching completed!")

if __name__ == "__main__":
    main()