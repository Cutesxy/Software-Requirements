"""
get_data.py - 使用 Etherscan API 拉取数据并保存到 MySQL
优化版本：增加重试机制、降低频率、错误处理，并支持数据合并
"""
from dateutil import parser
from datetime import timedelta, datetime
import requests
import time
import json
from decimal import Decimal
import config
from dbMapper import DBMapper
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class DataFetcher:
    def __init__(self, db_mapper):
        self.db = db_mapper
        self.etherscan_swaps_count = 0
        self.binance_klines_count = 0
        
        # 创建带重试机制的 session
        self.session = self._create_retry_session()
        
    def _create_retry_session(self):
        """创建带重试机制的 requests session"""
        session = requests.Session()
        
        # 重试策略
        retry_strategy = Retry(
            total=5,  # 最大重试次数
            backoff_factor=1,  # 重试等待时间：1, 2, 4, 8, 16 秒
            status_forcelist=[429, 500, 502, 503, 504],  # 遇到这些状态码时重试
            allowed_methods=["GET"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def safe_etherscan_request(self, params, max_retries=3):
        """安全的 Etherscan API 请求，带重试和退避"""
        for attempt in range(max_retries):
            try:
                # 每次重试前增加延迟
                if attempt > 0:
                    wait_time = 2 ** attempt  # 指数退避：2, 4, 8 秒
                    print(f"第 {attempt + 1} 次重试，等待 {wait_time} 秒...")
                    time.sleep(wait_time)
                
                response = self.session.get(
                    "https://api.etherscan.io/v2/api",
                    params=params,
                    timeout=60  # 增加超时时间
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data
                elif response.status_code == 429:
                    print(f"达到速率限制，等待 10 秒后重试...")
                    time.sleep(10)
                    continue
                else:
                    print(f"HTTP 错误 {response.status_code}，响应: {response.text}")
                    
            except requests.exceptions.SSLError as e:
                print(f"SSL 错误 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise e
            except requests.exceptions.ConnectionError as e:
                print(f"连接错误 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise e
            except requests.exceptions.Timeout as e:
                print(f"超时错误 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise e
            except Exception as e:
                print(f"未知错误 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise e
        
        return None

    def fetch_etherscan_swaps_robust(self, start_block, end_block, max_retries=3):
        """
        更健壮的获取方法，遇到错误时会自动调整参数重试
        """
        for attempt in range(max_retries):
            try:
                print(f"\n尝试 {attempt + 1}/{max_retries} 获取数据...")
                transfers = self.fetch_etherscan_swaps(start_block, end_block)
                return transfers
                
            except Exception as e:
                print(f"第 {attempt + 1} 次尝试失败: {e}")
                
                if attempt < max_retries - 1:
                    # 调整参数重试
                    wait_time = (attempt + 1) * 10  # 10, 20, 30 秒
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    print("所有重试尝试都失败了")
                    return []
        
        return []
    
    def fetch_etherscan_swaps(self, start_block, end_block):
        """
        从 Etherscan 获取指定地址的 Token 交易数据（分批次获取）
        优化版本：更小的批次、更好的错误处理
        """
        print(f"Fetching Etherscan token transfers from block {start_block} to {end_block}")
        
        all_transfers = []
        batch_size = 1000  # 减小批次大小，避免超时
        
        current_block = start_block
        batch_count = 0
        
        while current_block <= end_block:
            batch_end = min(current_block + batch_size - 1, end_block)
            batch_count += 1
            
            print(f"\n批次 {batch_count}: 获取区块 {current_block} 到 {batch_end}")
            
            try:
                batch_transfers = self._fetch_etherscan_batch(current_block, batch_end)
                if batch_transfers:
                    all_transfers.extend(batch_transfers)
                    print(f"批次 {batch_count} 完成: 获取到 {len(batch_transfers)} 笔交易")
                else:
                    print(f"批次 {batch_count}: 没有获取到数据")
                
                # 批次间延迟，避免触发速率限制
                time.sleep(1)
                
            except Exception as e:
                print(f"批次 {batch_count} 失败: {e}")
                # 失败后等待更长时间再继续
                time.sleep(5)
            
            current_block = batch_end + 1
            
            # 每10个批次显示一次进度
            if batch_count % 10 == 0:
                progress = (current_block - start_block) / (end_block - start_block) * 100
                print(f"\n=== 进度: {progress:.1f}% ({len(all_transfers)} 笔交易) ===\n")
        
        print(f"\n总共获取到 {len(all_transfers)} 笔 token 交易")
        return all_transfers
    
    def _fetch_etherscan_batch(self, start_block, end_block):
        """
        获取单个批次的交易数据
        优化版本：更好的分页处理
        """
        batch_transfers = []
        page = 1
        page_size = 1000  # 使用最大页面大小
        
        while True:
            try:
                params = {
                    'chainid': 1,
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
                
                data = self.safe_etherscan_request(params)
                
                if data is None:
                    print(f"  页面 {page}: 请求失败，跳过此页面")
                    break
                
                if data.get('status') == '1':
                    transfers = data['result']
                    if not transfers:
                        break  # 没有更多数据了
                        
                    batch_transfers.extend(transfers)
                    print(f"  页面 {page}: {len(transfers)} 笔交易 (批次总计: {len(batch_transfers)})")
                    
                    # 如果返回的数据少于请求的数量，说明没有更多数据了
                    if len(transfers) < page_size:
                        break
                        
                    page += 1
                    
                    # 页面间延迟
                    time.sleep(0.5)
                    
                else:
                    error_msg = data.get('message', 'Unknown error')
                    print(f"  Etherscan API 错误: {error_msg}")
                    
                    # 处理特定错误
                    if "No transactions found" in error_msg:
                        break
                    elif "Result window is too large" in error_msg:
                        print("  结果集太大，尝试减小查询范围")
                        return batch_transfers
                    elif "Max rate limit reached" in error_msg:
                        print("  达到最大速率限制，等待 5 秒")
                        time.sleep(5)
                        continue
                    else:
                        # 其他错误返回已获取的数据
                        return batch_transfers
                        
            except Exception as e:
                print(f"  获取页面 {page} 时出错: {e}")
                # 返回已成功获取的数据
                return batch_transfers
                
        return batch_transfers
    
    def process_etherscan_transfers(self, transfers):
        """
        处理 Etherscan 交易数据，将同一交易哈希的 USDT 和 WETH 转账合并为 swap 事件
        """
        if not transfers:
            print("没有交易数据需要处理")
            return 0
            
        # 按交易哈希分组
        tx_groups = {}
        for transfer in transfers:
            tx_hash = transfer['hash']
            if tx_hash not in tx_groups:
                tx_groups[tx_hash] = []
            tx_groups[tx_hash].append(transfer)
        
        processed_swaps = []
        complex_tx_count = 0
        
        print(f"处理 {len(tx_groups)} 个交易...")
        
        # 处理每个交易组
        for i, (tx_hash, tx_transfers) in enumerate(tx_groups.items()):
            if (i + 1) % 1000 == 0:
                print(f"已处理 {i + 1}/{len(tx_groups)} 个交易")
                
            # 一个完整的 swap 应该有两个转账（USDT 和 WETH）
            if len(tx_transfers) == 2:
                swap_data = self._create_swap_from_transfers(tx_transfers)
                if swap_data:
                    processed_swaps.append(swap_data)
            elif len(tx_transfers) > 2:
                # 如果有超过2个转账，可能是复杂的交易，尝试配对处理
                complex_tx_count += 1
                if complex_tx_count <= 10:  # 只打印前10个复杂交易的日志
                    print(f"复杂交易 {tx_hash}: {len(tx_transfers)} 笔转账")
                paired_swaps = self._pair_complex_transfers(tx_transfers)
                processed_swaps.extend(paired_swaps)
        
        if complex_tx_count > 10:
            print(f"... 还有 {complex_tx_count - 10} 个复杂交易")
        
        # 保存到数据库
        saved_count = 0
        print(f"保存 {len(processed_swaps)} 个 swap 到数据库...")
        
        for i, swap in enumerate(processed_swaps):
            if self.db.store_uniswap_swap(swap):
                saved_count += 1
                
            if (i + 1) % 100 == 0:
                print(f"已保存 {i + 1}/{len(processed_swaps)} 个 swap")
        
        self.etherscan_swaps_count = saved_count
        print(f"成功处理并保存 {saved_count} 个 Uniswap swap 到数据库")
        print(f"从 {len(transfers)} 笔交易中识别出 {len(processed_swaps)} 个有效 swap")
        
        return saved_count

    def _pair_complex_transfers(self, transfers):
        """
        处理复杂交易（一个交易中有多个转账）
        """
        swaps = []
        
        # 分离 USDT 和 WETH 转账
        usdt_transfers = [t for t in transfers if t['contractAddress'].lower() == config.USDT_CONTRACT.lower()]
        weth_transfers = [t for t in transfers if t['contractAddress'].lower() == config.WETH_CONTRACT.lower()]
        
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
                
                # 检查价格是否在合理范围内（例如 500-10000 USDT/ETH）
                if 500 <= calculated_price <= 10000:
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
            print(f"从转账创建 swap 时出错: {e}")
            return None

    def fetch_binance_klines(self, start_timestamp, end_timestamp):
        """
        从 Binance 获取 K线数据（处理分页）
        优化版本：更好的错误处理和重试
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
        
        page_count = 0
        
        while current_start < end_time_ms:
            current_end = min(current_start + interval_ms, end_time_ms)
            page_count += 1
            
            for attempt in range(3):  # 重试3次
                try:
                    url = "https://api.binance.com/api/v3/klines"
                    params = {
                        'symbol': config.BINANCE_SYMBOL,
                        'interval': '1m',
                        'startTime': current_start,
                        'endTime': current_end,
                        'limit': limit
                    }
                    
                    response = self.session.get(url, params=params, timeout=30)
                    
                    if response.status_code == 200:
                        klines = response.json()
                        if not klines:
                            break  # 没有更多数据了
                            
                        all_klines.extend(klines)
                        print(f"页面 {page_count}: 获取 {len(klines)} 根 Binance K线 (总计: {len(all_klines)})")
                        
                        # 移动到下一时间段
                        current_start = int(klines[-1][0]) + 60000  # 最后一个K线的时间 + 1分钟
                        
                        # 避免请求过于频繁
                        time.sleep(0.2)
                        break  # 成功，跳出重试循环
                    else:
                        print(f"Binance API 错误: {response.status_code}, 响应: {response.text}")
                        if attempt < 2:  # 不是最后一次尝试
                            wait_time = (attempt + 1) * 2
                            print(f"等待 {wait_time} 秒后重试...")
                            time.sleep(wait_time)
                        else:
                            break
                            
                except Exception as e:
                    print(f"获取 Binance 数据时出错 (尝试 {attempt + 1}): {e}")
                    if attempt < 2:
                        time.sleep((attempt + 1) * 2)
                    else:
                        break
        
        print(f"总共获取到 {len(all_klines)} 根 Binance K线")
        return all_klines

    def process_binance_klines(self, klines):
        """
        处理 Binance K线数据并保存到数据库
        """
        if not klines:
            print("没有 K线数据需要处理")
            return 0
            
        processed_count = 0
        print(f"处理 {len(klines)} 根 K线...")
        
        for i, kline in enumerate(klines):
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
                    
                if (i + 1) % 1000 == 0:
                    print(f"已处理 {i + 1}/{len(klines)} 根 K线")
                    
            except Exception as e:
                print(f"处理 Binance K线时出错: {e}")
                continue
        
        self.binance_klines_count = processed_count
        print(f"处理并保存 {processed_count} 根 Binance K线到数据库")
        return processed_count

def main():
    # 初始化数据库
    db = DBMapper()
    db.init_db()
    print("数据库初始化完成")
    
    fetcher = DataFetcher(db)
    
    # 从 config 中读取时间范围（字符串），并转为 datetime
    start_dt = parser.isoparse(config.START_DATE)
    end_dt = parser.isoparse(config.END_DATE)
    # 包含结束日全天
    end_dt = end_dt + timedelta(days=1) - timedelta(seconds=1)
    
    # 转换为时间戳
    start_timestamp = int(start_dt.timestamp())
    end_timestamp = int(end_dt.timestamp())
    
    print(f"获取数据时间范围: {start_dt} 到 {end_dt}")
    print(f"时间戳范围: {start_timestamp} 到 {end_timestamp}")
    
    # 使用区块范围
    start_block = config.START_BLOCK
    end_block = config.END_BLOCK
    
    # 获取并处理 Etherscan 数据
    print("\n=== 获取 Etherscan 数据 ===")
    etherscan_transfers = fetcher.fetch_etherscan_swaps_robust(start_block, end_block, max_retries=3)
    if etherscan_transfers:
        fetcher.process_etherscan_transfers(etherscan_transfers)
    else:
        print("未能获取到 Etherscan 数据")
    
    # 获取并处理 Binance 数据
    print("\n=== 获取 Binance 数据 ===")
    binance_klines = fetcher.fetch_binance_klines(start_timestamp, end_timestamp)
    if binance_klines:
        fetcher.process_binance_klines(binance_klines)
    else:
        print("未能获取到 Binance 数据")
    
    # 输出总结
    print("\n=== 数据获取总结 ===")
    print(f"Etherscan swaps: {fetcher.etherscan_swaps_count}")
    print(f"Binance klines: {fetcher.binance_klines_count}")

if __name__ == "__main__":
    main()