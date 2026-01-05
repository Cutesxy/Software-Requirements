"""
AI 分析助手服务
使用 DeepSeek API 提供智能分析和自然语言操控功能
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'sk-5a12767e3f694109a79da17f5499d880')
DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'

# Function Calling 工具定义
FUNCTIONS = [
    {
        "type": "function",
        "function": {
            "name": "filter_signals",
            "description": "根据条件筛选9月份的套利信号数据。用户可以用自然语言描述筛选条件，系统会从后端获取所有信号数据并筛选返回结构化结果。",
            "parameters": {
                "type": "object",
                "properties": {
                    "minProfit": {
                        "type": "number",
                        "description": "最小净利润（USDT），例如：10 表示净利润大于等于 10 USDT"
                    },
                    "maxProfit": {
                        "type": "number",
                        "description": "最大净利润（USDT）"
                    },
                    "minZScore": {
                        "type": "number",
                        "description": "最小 Z-Score 值，例如：2.5 表示 Z-Score 大于等于 2.5"
                    },
                    "maxZScore": {
                        "type": "number",
                        "description": "最大 Z-Score 值"
                    },
                    "direction": {
                        "type": "string",
                        "enum": ["CEX->DEX", "DEX->CEX", "Long", "Short", "both"],
                        "description": "交易方向：CEX->DEX 或 Long（从中心化交易所到去中心化交易所），DEX->CEX 或 Short（反向），both（全部）"
                    },
                    "minSpread": {
                        "type": "number",
                        "description": "最小价差（USDT）"
                    },
                    "maxSpread": {
                        "type": "number",
                        "description": "最大价差（USDT）"
                    }
                }
            }
        }
    }
]


def build_system_prompt(context: Dict[str, Any]) -> str:
    """构建系统提示词"""
    prompt = """你是一个数据筛选助手，专门帮助用户筛选9月份的套利信号数据。

数据说明：
- 数据时间范围：2025年9月1日 - 2025年9月30日
- 数据字段：时间(time)、方向(direction)、净利润(netProfit)、Z-Score(zScore)、价差(spread)等
- 方向值：CEX->DEX 或 Long（从中心化交易所到去中心化交易所），DEX->CEX 或 Short（反向）

你的任务：
1. 理解用户的自然语言筛选需求
2. 调用 filter_signals 函数，传入正确的筛选条件
3. 筛选条件会被应用到9月份的所有信号数据上
4. 返回筛选后的结构化数据

重要约束：
1. 必须使用 filter_signals 函数来筛选数据
2. 如果用户没有明确指定某个条件，不要设置该参数（让参数为 null）
3. 方向筛选：如果用户说"只看 DEX→CEX"或"DEX到CEX"，使用 "DEX->CEX"；如果用户说"CEX到DEX"，使用 "CEX->DEX"
4. 净利润条件：如果用户说"净利润>10"，设置 minProfit=10；如果用户说"净利润<50"，设置 maxProfit=50
5. Z-Score条件：如果用户说"Z>2.5"，设置 minZScore=2.5

示例：
- "把净利润>10、Z>2.5、只看 DEX→CEX 的信号筛出来" 
  → filter_signals(minProfit=10, minZScore=2.5, direction="DEX->CEX")
- "筛选净利润大于20的信号"
  → filter_signals(minProfit=20)
"""
    return prompt


def filter_signals_from_backend(filter_args: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    从后端获取所有信号数据并应用筛选条件
    
    Args:
        filter_args: 筛选条件字典
        
    Returns:
        筛选后的信号列表
    """
    import service
    from datetime import datetime
    import config
    
    # 获取9月份的时间范围（2025-09-01 到 2025-09-30）
    start_dt = datetime.strptime("2025-09-01", "%Y-%m-%d")
    end_dt = datetime.strptime("2025-09-30", "%Y-%m-%d")
    end_dt = end_dt.replace(hour=23, minute=59, second=59)
    start_ts = int(start_dt.timestamp())
    end_ts = int(end_dt.timestamp())
    
    # 使用默认参数获取所有信号
    z_threshold = 0  # 不限制 Z-Score，获取所有信号
    trade_size = 10000  # 默认交易规模
    
    signals, _ = service.run_backtest(start_ts, end_ts, z_threshold, trade_size)
    
    # 应用筛选条件
    filtered = []
    for signal in signals:
        # 净利润筛选
        if 'minProfit' in filter_args and filter_args['minProfit'] is not None:
            if signal.get('netProfit', 0) < filter_args['minProfit']:
                continue
        if 'maxProfit' in filter_args and filter_args['maxProfit'] is not None:
            if signal.get('netProfit', 0) > filter_args['maxProfit']:
                continue
        
        # Z-Score 筛选
        if 'minZScore' in filter_args and filter_args['minZScore'] is not None:
            if abs(signal.get('zScore', 0)) < filter_args['minZScore']:
                continue
        if 'maxZScore' in filter_args and filter_args['maxZScore'] is not None:
            if abs(signal.get('zScore', 0)) > filter_args['maxZScore']:
                continue
        
        # 方向筛选
        if 'direction' in filter_args and filter_args['direction'] is not None:
            direction = filter_args['direction']
            signal_dir = signal.get('direction', '')
            if direction == 'DEX->CEX' or direction == 'Short':
                if signal_dir not in ['DEX->CEX', 'Short']:
                    continue
            elif direction == 'CEX->DEX' or direction == 'Long':
                if signal_dir not in ['CEX->DEX', 'Long']:
                    continue
            elif direction != 'both':
                if signal_dir != direction:
                    continue
        
        # 价差筛选
        if 'minSpread' in filter_args and filter_args['minSpread'] is not None:
            if abs(signal.get('spread', 0)) < filter_args['minSpread']:
                continue
        if 'maxSpread' in filter_args and filter_args['maxSpread'] is not None:
            if abs(signal.get('spread', 0)) > filter_args['maxSpread']:
                continue
        
        filtered.append(signal)
    
    return filtered


def chat_with_ai(message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    与 AI 对话
    
    Args:
        message: 用户消息
        context: 页面上下文
        
    Returns:
        {
            "content": "AI 回复内容",
            "functionCall": {
                "name": "function_name",
                "arguments": {...}
            } 或 None
        }
    """
    try:
        system_prompt = build_system_prompt(context)
        
        # 构建消息历史
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
        
        # 调用 DeepSeek API
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "tools": FUNCTIONS,
            "tool_choice": "auto",  # 让模型自动决定是否调用工具
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        response = requests.post(
            DEEPSEEK_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            error_msg = f"DeepSeek API 错误: {response.status_code} - {response.text}"
            print(error_msg)
            return {
                "content": "抱歉，AI 服务暂时不可用，请稍后重试。",
                "functionCall": None
            }
        
        result = response.json()
        
        # 解析响应
        if "choices" not in result or len(result["choices"]) == 0:
            return {
                "content": "抱歉，AI 无法生成回复。",
                "functionCall": None
            }
        
        choice = result["choices"][0]
        message_obj = choice.get("message", {})
        
        # 提取文本内容
        content = message_obj.get("content", "")
        
        # 检查是否有 function call
        tool_calls = message_obj.get("tool_calls", [])
        filtered_data = None
        
        if tool_calls and len(tool_calls) > 0:
            tool_call = tool_calls[0]
            function_name = tool_call.get("function", {}).get("name", "")
            function_args_str = tool_call.get("function", {}).get("arguments", "{}")
            
            try:
                function_args = json.loads(function_args_str)
                
                # 如果是筛选函数，执行筛选
                if function_name == "filter_signals":
                    filtered_data = filter_signals_from_backend(function_args)
                    
                    # 生成说明文本
                    count = len(filtered_data)
                    if not content:
                        content = f"已筛选出 {count} 条符合条件的信号数据。"
                    else:
                        content += f"\n\n已筛选出 {count} 条符合条件的信号数据。"
                        
            except json.JSONDecodeError:
                print(f"Function call 参数解析失败: {function_args_str}")
            except Exception as e:
                print(f"筛选数据失败: {e}")
                content = f"筛选数据时发生错误：{str(e)}"
        
        return {
            "content": content,
            "filteredData": filtered_data
        }
        
    except requests.exceptions.Timeout:
        return {
            "content": "请求超时，请稍后重试。",
            "functionCall": None
        }
    except requests.exceptions.RequestException as e:
        print(f"DeepSeek API 请求异常: {e}")
        return {
            "content": "网络请求失败，请检查网络连接。",
            "functionCall": None
        }
    except Exception as e:
        print(f"AI 服务异常: {e}")
        return {
            "content": f"发生错误：{str(e)}",
            "functionCall": None
        }


def get_page_summary(page: str, context: Dict[str, Any]) -> str:
    """
    获取页面数据摘要（用于上下文）
    这里可以根据页面类型返回不同的摘要
    """
    page_summaries = {
        "overview": "总览页面：显示整体套利机会统计和关键指标",
        "Compare": "数据分析页面：展示市场数据对比和价差趋势",
        "Radar": "套利识别页面：实时检测和展示套利信号",
        "Backtest": "回测分析页面：策略回测和绩效评估",
        "Case": "案例回放页面：历史套利案例详情",
        "Lab": "数据实验台：数据探索和分析工具",
        "Alerts": "告警中心：异常情况监控",
        "Report": "报告生成：生成分析报告"
    }
    
    return page_summaries.get(page, "未知页面")


if __name__ == "__main__":
    # 测试
    test_context = {
        "page": "Backtest",
        "config": {
            "detector": {
                "priceThreshold": 1.0,
                "zScoreThreshold": 2.0,
                "volumeMin": 1500,
                "fees": {
                    "cex": 0.001,
                    "dex": 0.003,
                    "gas": 15
                }
            }
        }
    }
    
    result = chat_with_ai("用一句话总结本周期表现", test_context)
    print(json.dumps(result, indent=2, ensure_ascii=False))

