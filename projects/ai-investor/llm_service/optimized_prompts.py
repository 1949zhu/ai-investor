"""
优化的 LLM 提示词模板 - 减少 token 消耗
"""

from typing import Dict, List, Optional


class OptimizedPrompts:
    """优化的提示词模板"""
    
    @staticmethod
    def macro_analyst(data: Dict, memory_context: str = "") -> str:
        """宏观分析师 - 精简版"""
        return f"""【角色】首席宏观经济分析师
【任务】分析 A 股市场状态并给出配置建议

【数据】
日期：{data.get('date', '未知')}
涨跌：涨{data.get('up', 0)}/跌{data.get('down', 0)}
情绪：{data.get('sentiment', '中性')}({data.get('score', 50)}/100)
均幅：{data.get('avg_change', 0):.2f}%

{f'【记忆】{memory_context[:300]}' if memory_context else ''}

【输出要求】
1. 市场状态 (牛/熊/震荡，1 句)
2. 情绪分析 (1 句)
3. 配置建议 (3 条以内)

【格式】简洁专业，300 字内"""

    @staticmethod
    def quant_analyst(strategy_data: Dict, history: str = "") -> str:
        """量化分析师 - 精简版"""
        return f"""【角色】量化分析师
【任务】评估策略可信度

【策略数据】
收益：{strategy_data.get('return', 52.52):.1f}%
年化：{strategy_data.get('annual', 50.08):.1f}%
夏普：{strategy_data.get('sharpe', 2.06):.2f}
回撤：{strategy_data.get('mdd', 1.55):.2f}%
胜率：{strategy_data.get('win_rate', 84.2):.1f}%

{f'【历史】{history[:200]}' if history else ''}

【输出要求】
1. 可信度评分 (0-100)
2. 主要风险 (2 条)
3. 改进建议 (2 条)

【格式】简洁，200 字内"""

    @staticmethod
    def risk_officer(sentiment_data: Dict) -> str:
        """风控官 - 精简版"""
        return f"""【角色】风控官
【任务】评估投资风险

【市场数据】
情绪：{sentiment_data.get('label', '中性')}({sentiment_data.get('score', 50)})
涨跌比：{sentiment_data.get('up', 0)}:{sentiment_data.get('down', 0)}
均幅：{sentiment_data.get('avg_change', 0):.2f}%

【风险限制】
最大回撤 15% | 单股≤20% | 止损 8% | 止盈 20%

【输出要求】
1. 风险等级 (低/中/高)
2. 仓位建议 (%)
3. 关键提醒 (1 条)

【格式】简洁，150 字内"""

    @staticmethod
    def cio_decision(macro: str, quant: str, risk: str, memory: str = "") -> str:
        """CIO 综合决策 - 精简版"""
        return f"""【角色】首席投资官
【任务】综合三方报告做投资决策

【输入】
宏观：{macro[:400]}
量化：{quant[:300]}
风控：{risk[:200]}
{f'记忆：{memory[:200]}' if memory else ''}

【输出要求】
1. 执行摘要 (市场判断 + 仓位 + 置信度)
2. 操作建议 (最多 3 个标的，含止损止盈)
3. 主要风险 (1 条)

【格式】简洁专业，400 字内"""

    @staticmethod
    def sentiment_analysis(news_list: List[Dict]) -> str:
        """新闻情绪分析 - 精简版"""
        news_summary = "\n".join([f"- {n['title'][:50]}" for n in news_list[:10]])
        
        return f"""【任务】分析新闻情绪

【新闻摘要】
{news_summary}

【输出要求】
1. 整体情绪 (乐观/中性/悲观)
2. 关键词 (3 个)
3. 市场影响 (1 句)

【格式】100 字内"""

    @staticmethod
    def northbound_analysis(flow_data: Dict) -> str:
        """北向资金分析 - 精简版"""
        return f"""【任务】分析北向资金流向

【数据】
最新：{flow_data.get('latest', 0):.1f}亿
5 日累计：{flow_data.get('inflow_5d', 0):.1f}亿
趋势：{flow_data.get('trend', '未知')}

【输出要求】
1. 资金态度 (流入/流出/震荡)
2. 信号强度 (强/中/弱)
3. 操作启示 (1 句)

【格式】80 字内"""


class TokenOptimizer:
    """Token 优化器"""
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 500) -> str:
        """截断文本"""
        if len(text) <= max_length:
            return text
        return text[:max_length-20] + "...(略)"
    
    @staticmethod
    def summarize_list(items: List, max_items: int = 5, format_func=None) -> str:
        """列表摘要"""
        if not items:
            return "无"
        
        limited = items[:max_items]
        if format_func:
            return "\n".join([format_func(item) for item in limited])
        return "\n".join([str(item) for item in limited])
    
    @staticmethod
    def compress_data(data: Dict, keep_keys: List[str] = None) -> Dict:
        """压缩数据，只保留关键字段"""
        if not keep_keys:
            return data
        return {k: v for k, v in data.items() if k in keep_keys}
    
    @staticmethod
    def format_number(value: float, decimals: int = 2) -> str:
        """格式化数字"""
        if abs(value) >= 1000:
            return f"{value/10000:.1f}万"
        return f"{value:.{decimals}f}"


# 使用示例
if __name__ == "__main__":
    print("优化的提示词模板示例\n")
    
    # 宏观分析师提示词
    data = {
        'date': '2026-03-05',
        'up': 1500,
        'down': 2000,
        'sentiment': '悲观',
        'score': 35,
        'avg_change': -1.2
    }
    
    prompt = OptimizedPrompts.macro_analyst(data)
    print(f"宏观分析师提示词 ({len(prompt)} 字):")
    print(prompt)
    print("\n" + "="*60 + "\n")
    
    # CIO 提示词
    macro_report = "市场处于震荡市，情绪偏悲观，建议防御配置。"
    quant_report = "策略可信度 65 分，存在过拟合风险。"
    risk_report = "风险等级中，建议仓位 60%。"
    
    cio_prompt = OptimizedPrompts.cio_decision(macro_report, quant_report, risk_report)
    print(f"CIO 提示词 ({len(cio_prompt)} 字):")
    print(cio_prompt)
