"""
data_merger.py - 专门处理数据合并
最终修复版本
"""
import pandas as pd
import numpy as np
from sqlalchemy import text
import config
from dbMapper import DBMapper

class DataMerger:
    def __init__(self, db_mapper):
        self.db = db_mapper
    
    def calculate_uniswap_prices(self):
        """
        计算 Uniswap 交易的价格并更新数据库
        """
        print("开始计算 Uniswap 交易价格...")
        
        try:
            # 从数据库读取 Uniswap 交易数据
            swaps = self.db.get_uniswap_swaps()
            if not swaps:
                print("没有找到 Uniswap 交易数据")
                return False
            
            print(f"找到 {len(swaps)} 条 Uniswap 交易记录")
            
            # 转换为 DataFrame
            df = pd.DataFrame(swaps)
            
            # 计算价格 (USDT per ETH)
            # 注意：amount0 是 WETH，amount1 是 USDT
            # 价格 = |amount1| / |amount0|
            df['price'] = (abs(df['amount1']) / abs(df['amount0'])).replace([np.inf, -np.inf], np.nan)
            
            # 过滤掉异常价格
            valid_prices = df[df['price'].notna() & (df['price'] > 0) & (df['price'] < 10000)]
            print(f"有效价格记录: {len(valid_prices)}/{len(df)}")
            
            # 更新数据库中的价格字段
            updated_count = 0
            for _, row in valid_prices.iterrows():
                # 使用 SQL 更新价格
                update_sql = text("""
                UPDATE uniswap_swaps 
                SET price = :price 
                WHERE id = :id
                """)
                
                with self.db.engine.connect() as connection:
                    result = connection.execute(
                        update_sql, 
                        {'price': float(row['price']), 'id': row['id']}
                    )
                    connection.commit()
                    updated_count += result.rowcount
            
            print(f"成功更新 {updated_count} 条记录的价格")
            return True
            
        except Exception as e:
            print(f"计算 Uniswap 价格时出错: {e}")
            return False
    
    def create_merged_trading_data(self):
        """
        创建时间戳对齐的合并交易数据
        修复了 ONLY_FULL_GROUP_BY 问题
        """
        print("开始创建合并交易数据...")
        
        try:
            # 首先确保价格已计算
            if not self.calculate_uniswap_prices():
                print("价格计算失败，无法创建合并数据")
                return False
            
            # 使用 SQLAlchemy 连接执行原生 SQL
            with self.db.engine.connect() as connection:
                # 开始事务
                with connection.begin():
                    # 清空合并表
                    connection.execute(text("TRUNCATE TABLE merged_trading_data"))
                    
                    # 构建合并 SQL - 完全兼容 ONLY_FULL_GROUP_BY
                    merge_sql = """
                    INSERT INTO merged_trading_data (
                        time_bucket, timestamp,
                        uniswap_swap_count, uniswap_total_volume_eth, uniswap_total_volume_usdt,
                        uniswap_avg_price, uniswap_min_price, uniswap_max_price, uniswap_price_std,
                        binance_open, binance_high, binance_low, binance_close, 
                        binance_volume, binance_quote_volume, binance_trades,
                        price_difference, price_ratio
                    )
                    
                    -- 生成所有时间桶（从 Binance 数据）
                    WITH time_buckets AS (
                        SELECT 
                            FROM_UNIXTIME(FLOOR(open_time_ms / 1000 / 60) * 60) as time_bucket,
                            FLOOR(open_time_ms / 1000 / 60) * 60 as timestamp
                        FROM binance_klines 
                        WHERE symbol = 'ETHUSDT'
                        GROUP BY FROM_UNIXTIME(FLOOR(open_time_ms / 1000 / 60) * 60), FLOOR(open_time_ms / 1000 / 60) * 60
                    ),
                    
                    -- Binance 数据按分钟聚合
                    binance_agg AS (
                        SELECT 
                            FROM_UNIXTIME(FLOOR(open_time_ms / 1000 / 60) * 60) as time_bucket,
                            AVG(open) as open,
                            MAX(high) as high,
                            MIN(low) as low,
                            AVG(close) as close,
                            SUM(volume) as volume,
                            SUM(quote_av) as quote_av,
                            SUM(trades) as trades
                        FROM binance_klines 
                        WHERE symbol = 'ETHUSDT'
                        GROUP BY FROM_UNIXTIME(FLOOR(open_time_ms / 1000 / 60) * 60)
                    ),
                    
                    -- Uniswap 数据按分钟聚合
                    uniswap_agg AS (
                        SELECT 
                            FROM_UNIXTIME(FLOOR(timestamp / 60) * 60) as time_bucket,
                            COUNT(*) as swap_count,
                            SUM(ABS(amount0)) as total_volume_eth,
                            SUM(ABS(amount1)) as total_volume_usdt,
                            AVG(price) as avg_price,
                            MIN(price) as min_price,
                            MAX(price) as max_price,
                            STDDEV(price) as price_std
                        FROM uniswap_swaps 
                        WHERE pool_address = :pool_address
                          AND price IS NOT NULL
                          AND price > 0
                          AND price < 10000
                        GROUP BY FROM_UNIXTIME(FLOOR(timestamp / 60) * 60)
                    )
                    
                    SELECT 
                        tb.time_bucket,
                        tb.timestamp,
                        COALESCE(ua.swap_count, 0) as uniswap_swap_count,
                        COALESCE(ua.total_volume_eth, 0) as uniswap_total_volume_eth,
                        COALESCE(ua.total_volume_usdt, 0) as uniswap_total_volume_usdt,
                        COALESCE(ua.avg_price, 0) as uniswap_avg_price,
                        COALESCE(ua.min_price, 0) as uniswap_min_price,
                        COALESCE(ua.max_price, 0) as uniswap_max_price,
                        COALESCE(ua.price_std, 0) as uniswap_price_std,
                        ba.open as binance_open,
                        ba.high as binance_high,
                        ba.low as binance_low,
                        ba.close as binance_close,
                        ba.volume as binance_volume,
                        ba.quote_av as binance_quote_volume,
                        ba.trades as binance_trades,
                        COALESCE((ua.avg_price - ba.close), 0) as price_difference,
                        COALESCE((ua.avg_price / NULLIF(ba.close, 0)), 0) as price_ratio
                    FROM time_buckets tb
                    LEFT JOIN binance_agg ba ON tb.time_bucket = ba.time_bucket
                    LEFT JOIN uniswap_agg ua ON tb.time_bucket = ua.time_bucket
                    WHERE ba.time_bucket IS NOT NULL OR ua.time_bucket IS NOT NULL
                    ORDER BY tb.time_bucket
                    """
                    
                    # 执行合并
                    result = connection.execute(
                        text(merge_sql), 
                        {'pool_address': config.POOL_ADDRESS.lower()}
                    )
                    
                    print(f"合并数据创建完成，插入了 {result.rowcount} 条记录")
                    
                    # 获取统计信息
                    stats = self.get_merged_data_stats(connection)
                    if stats:
                        print(f"合并数据统计:")
                        print(f"  总记录数: {stats['total_records']}")
                        print(f"  时间范围: {stats['start_time']} 到 {stats['end_time']}")
                        print(f"  有效 Uniswap 记录: {stats['valid_uniswap_records']}")
                        print(f"  有效 Binance 记录: {stats['valid_binance_records']}")
                        print(f"  每分钟平均swap数量: {stats['avg_swaps_per_minute']:.2f}")
                        print(f"  平均价格差异: {stats['avg_price_diff']:.4f}")
                        print(f"  平均价格比率: {stats['avg_price_ratio']:.4f}")
            
            return True
            
        except Exception as e:
            print(f"创建合并交易数据时出错: {e}")
            return False
    
    def get_merged_data_stats(self, connection=None):
        """
        获取合并数据的统计信息
        """
        try:
            if connection is None:
                connection = self.db.engine.connect()
                close_connection = True
            else:
                close_connection = False
            
            # 使用 CASE 语句计算有效记录数
            stats_sql = """
            SELECT 
                COUNT(*) as total_records,
                MIN(time_bucket) as start_time,
                MAX(time_bucket) as end_time,
                SUM(CASE WHEN uniswap_swap_count > 0 THEN 1 ELSE 0 END) as valid_uniswap_records,
                SUM(CASE WHEN binance_close IS NOT NULL THEN 1 ELSE 0 END) as valid_binance_records,
                AVG(uniswap_swap_count) as avg_swaps_per_minute,
                AVG(price_difference) as avg_price_diff,
                AVG(price_ratio) as avg_price_ratio
            FROM merged_trading_data
            """
            
            result = connection.execute(text(stats_sql)).fetchone()
            
            if close_connection:
                connection.close()
            
            if result:
                return {
                    'total_records': result[0],
                    'start_time': result[1],
                    'end_time': result[2],
                    'valid_uniswap_records': result[3],
                    'valid_binance_records': result[4],
                    'avg_swaps_per_minute': float(result[5] or 0),
                    'avg_price_diff': float(result[6] or 0),
                    'avg_price_ratio': float(result[7] or 0)
                }
            return None
            
        except Exception as e:
            print(f"获取合并数据统计时出错: {e}")
            return None
    
    def export_merged_data(self, output_format='csv', filename='merged_trading_data'):
        """
        导出合并的数据集
        """
        try:
            # 使用 pandas 直接从数据库读取
            query = "SELECT * FROM merged_trading_data ORDER BY time_bucket"
            with self.db.engine.connect() as connection:
                df = pd.read_sql(query, connection)

            if df.empty:
                print("没有找到合并数据")
                return False
            
            if output_format == 'csv':
                df.to_csv(f'{filename}.csv', index=False, encoding='utf-8')
                print(f"数据已导出到 {filename}.csv")
            elif output_format == 'excel':
                df.to_excel(f'{filename}.xlsx', index=False)
                print(f"数据已导出到 {filename}.xlsx")
            elif output_format == 'json':
                df.to_json(f'{filename}.json', orient='records', indent=2)
                print(f"数据已导出到 {filename}.json")
            elif output_format == 'parquet':
                df.to_parquet(f'{filename}.parquet', index=False)
                print(f"数据已导出到 {filename}.parquet")
            else:
                print(f"不支持的格式: {output_format}")
                return False
                
            print(f"共导出 {len(df)} 条记录")
            return True
            
        except Exception as e:
            print(f"导出合并数据时出错: {e}")
            return False
    
    def analyze_data_quality(self):
        """
        分析数据质量
        """
        print("\n=== 数据质量分析 ===")
        
        try:
            # Uniswap 数据质量
            uniswap_sql = """
            SELECT 
                COUNT(*) as total_swaps,
                COUNT(DISTINCT DATE(ts)) as active_days,
                AVG(ABS(amount0)) as avg_eth_volume,
                AVG(ABS(amount1)) as avg_usdt_volume,
                MIN(ts) as first_swap,
                MAX(ts) as last_swap,
                COUNT(CASE WHEN price IS NOT NULL THEN 1 END) as priced_swaps
            FROM uniswap_swaps
            WHERE pool_address = :pool_address
            """
            
            with self.db.engine.connect() as connection:
                uniswap_stats = connection.execute(
                    text(uniswap_sql), 
                    {'pool_address': config.POOL_ADDRESS.lower()}
                ).fetchone()
                
                if uniswap_stats:
                    print("Uniswap 数据统计:")
                    print(f"  总交易数: {uniswap_stats[0]}")
                    print(f"  活跃天数: {uniswap_stats[1]}")
                    print(f"  平均 ETH 交易量: {float(uniswap_stats[2] or 0):.4f}")
                    print(f"  平均 USDT 交易量: {float(uniswap_stats[3] or 0):.2f}")
                    print(f"  已计算价格的交易: {uniswap_stats[6]}")
                    print(f"  时间范围: {uniswap_stats[4]} 到 {uniswap_stats[5]}")
                
                # Binance 数据质量
                binance_sql = """
                SELECT 
                    COUNT(*) as total_klines,
                    COUNT(DISTINCT DATE(open_time)) as active_days,
                    MIN(open_time) as first_kline,
                    MAX(open_time) as last_kline
                FROM binance_klines
                WHERE symbol = 'ETHUSDT'
                """
                
                binance_stats = connection.execute(text(binance_sql)).fetchone()
                
                if binance_stats:
                    print("\nBinance 数据统计:")
                    print(f"  总K线数: {binance_stats[0]}")
                    print(f"  活跃天数: {binance_stats[1]}")
                    print(f"  时间范围: {binance_stats[2]} 到 {binance_stats[3]}")
            
            return True
            
        except Exception as e:
            print(f"分析数据质量时出错: {e}")
            return False

def main():
    """
    独立运行数据合并
    """
    # 初始化数据库连接
    db = DBMapper()
    merger = DataMerger(db)
    
    print("开始数据合并流程...")
    
    # 分析数据质量
    merger.analyze_data_quality()
    
    # 创建合并数据集
    success = merger.create_merged_trading_data()
    
    if success:
        # 导出数据
        merger.export_merged_data(output_format='csv', filename='merged_trading_data')
        print("\n数据合并流程完成!")
    else:
        print("\n数据合并流程失败!")

if __name__ == "__main__":
    main()