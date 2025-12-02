"""
Analyzer: 非原子套利事件识别与估算，封装为类供 API 调用。
"""
from datetime import timedelta
import pandas as pd
import config
import json
import math
import dbMapper

class Analyzer:
    def __init__(self, db_mapper, params=None):
        self.db = db_mapper
        self.params = params or config.ANALYSIS_PARAMS

    def detect_events_from_df(self):
        is_signal_empty = self.db.clear_signals()
        if not is_signal_empty:
            print('signal 表清理失败，停止分析')
            return
        # 从 self.db 读取 uniswap_swaps 表到 DataFrame（兼容常见 db_store 类型）
        uniswap_swaps = self.db.get_uniswap_swaps()

        if uniswap_swaps is None:
            print('无法从 self.db 读取 uniswap_swaps 表，未知的 db_store 类型')
            return

        # dbMapper 当前实现返回 list of dicts，兼容 list 和 DataFrame
        if isinstance(uniswap_swaps, list):
            if len(uniswap_swaps) == 0:
                print('uniswap_swaps 表为空')
                return
            try:
                uniswap_swaps = pd.DataFrame(uniswap_swaps)
            except Exception as e:
                print(f'转换为 DataFrame 失败: {e}')
                return

        if not isinstance(uniswap_swaps, pd.DataFrame):
            try:
                uniswap_swaps = pd.DataFrame(uniswap_swaps)
            except Exception as e:
                print(f'无法将数据转换为 DataFrame: {e}')
                return

        if uniswap_swaps.empty:
            print('uniswap_swaps 表为空')
            return

        print('uniswap_swaps load finished\n')

        uniswap_swaps_i = 0
        # 读取 merged_trading_data 并删除 uniswap_swaps_count 为 0 的行（内存中过滤）
        merged_data = self.db.get_merged_trading_data()

        # dbMapper 当前实现返回 list of dicts，兼容 list 和 DataFrame
        if isinstance(merged_data, list):
            if len(merged_data) == 0:
                print('merged_data 表为空')
                return
            try:
                merged_data = pd.DataFrame(merged_data)
            except Exception as e:
                print(f'转换为 DataFrame 失败: {e}')
                return

        if not isinstance(merged_data, pd.DataFrame):
            try:
                merged_data = pd.DataFrame(merged_data)
            except Exception as e:
                print(f'无法将数据转换为 DataFrame: {e}')
                return

        if merged_data.empty:
            print('merged_data 表为空')
            return

        # 遍历处理每一行
        for row in merged_data.itertuples(index=True, name="Row"):
            # row.Index 是原始 DataFrame 的索引，其他字段通过属性访问：row.column_name
            swap_count = int(getattr(row, 'uniswap_swap_count', 0))  # 用实际列名
            if swap_count == 0:
                continue  # 跳过无 swap 的行
            price_diff = float(getattr(row, 'price_difference', 0.0))
            # if price_diff <= 0:
            #    uniswap_swaps_i += swap_count
            #    continue  # 仅处理价格差为正的情况
            uniswap_swap_volume = float(getattr(row, 'uniswap_total_volume_eth', 0.0))
            gross_profit = abs(price_diff) * uniswap_swap_volume  # 估算毛利润
            binance_fee_total = 0.0  # 累计Binance的现货交易手续费
            uniswap_fee_total = 0.0  # 累计Uniswap V3的交易手续费
            gas_cost_total = 0.0  # 累计 gas 成本
            current_uniswap_swaps = []
            for _ in range(swap_count):
                if uniswap_swaps_i >= len(uniswap_swaps):
                    print('uniswap_swaps 数据不足，提前结束')
                    return
                uniswap_swap = uniswap_swaps.iloc[uniswap_swaps_i]
                current_uniswap_swaps.append(uniswap_swap)
                uniswap_swaps_i += 1
                raw_field = json.loads(uniswap_swap['raw'])
                gasUsed = int(raw_field[0].get('gasUsed', 0))
                gasPrice = int(raw_field[0].get('gasPrice', 0))
                price = float(uniswap_swap['price'])
                amount0 = abs(float(uniswap_swap['amount0']))
                uniswap_fee_total += amount0 * price * config.ANALYSIS_PARAMS['uniswap_fee_pct']  # 从config文件中获取'uniswap_fee_pct'
                amount1 = abs(float(uniswap_swap['amount1']))
                binance_fee_total += amount1 * config.ANALYSIS_PARAMS['binance_fee_pct']  # 从config文件中获取'binance_fee_pct'
                gas_cost_total += 1.0 * gasUsed * gasPrice * price / 1e18  # 转为 USDT

            net_profit = gross_profit - (binance_fee_total + uniswap_fee_total + gas_cost_total)
            if net_profit > config.ANALYSIS_PARAMS['profit_threshold_in_usdt']:
                uniswap_price_std = row.uniswap_price_std
                confidence = math.exp(-uniswap_price_std / 1000)  # 使用Uniswap价格标准差计算信心值
                signal = dbMapper.Signal(
                    time_bucket=row.time_bucket,
                    timestamp=row.timestamp,
                    direction='Long DEX' if price_diff > 0 else 'Short DEX',
                    size=row.binance_volume,
                    swap_count=row.uniswap_swap_count,
                    zscore=price_diff / row.uniswap_price_std if row.uniswap_price_std != 0 else None,
                    gross_profit=gross_profit,
                    binance_fee=binance_fee_total,
                    uniswap_fee=uniswap_fee_total,
                    gas_cost=gas_cost_total,
                    net_profit=net_profit,
                    confidence=confidence,
                    uniswap_avg_price=row.uniswap_avg_price,
                    binance_close_price=row.binance_close,
                    price_difference=price_diff
                )
                self.db.store_signal(signal.to_dict())

    def export_analysis_data(self, output_format='csv', filename='merged_trading_data'):
        """
        导出合并的数据集
        """
        try:
            rows = self.db.get_signals()

            df = pd.DataFrame(rows)

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
                try:
                    df.to_parquet(f'{filename}.parquet', index=False)
                    print(f"数据已导出到 {filename}.parquet")
                except Exception as e:
                    print(f"导出 parquet 失败，是否安装了 pyarrow 或 fastparquet? 错误: {e}")
                    return False
            else:
                print(f"不支持的格式: {output_format}")
                return False
                
            print(f"共导出 {len(df)} 条记录")
            return True
            
        except Exception as e:
            print(f"导出合并数据时出错: {e}")
            return False

    def run_analysis(self):
        self.detect_events_from_df()

def main():
    db = dbMapper.DBMapper()
    analyzer = Analyzer(db)
    analyzer.run_analysis()
    analyzer.export_analysis_data(output_format='csv', filename='arbitrage_signals')

if __name__ == "__main__":
    main()