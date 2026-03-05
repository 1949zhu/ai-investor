"""
LLM 报告增强器

使用 AI 生成专业、人性化的投资分析报告
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_service import get_llm_service
from llm_service.config import LLMConfig


class LLMReportEnhancer:
    """
    LLM 报告增强器
    
    将模板化报告转换为专业、自然的投资分析报告
    """
    
    def __init__(self, llm_service=None):
        if llm_service:
            self.llm = llm_service
        else:
            config = LLMConfig.get_service_config()
            self.llm = get_llm_service(**config)
    
    def enhance_report(self, report_data: Dict) -> Dict:
        """
        增强投资报告
        
        Args:
            report_data: 原始报告数据
            
        Returns:
            增强结果（包含状态）
        """
        prompt = self._build_enhance_prompt(report_data)
        
        print("🧠 LLM 正在撰写投资分析报告...")
        enhanced_report = self.llm.generate(prompt)
        
        # 检查是否返回错误
        if isinstance(enhanced_report, str) and '"status": "error"' in enhanced_report:
            return {
                'status': 'error',
                'error': 'LLM 报告增强失败',
                'content': None
            }
        
        return {
            'status': 'success',
            'content': enhanced_report
        }
    
    def generate_executive_summary(self, strategy: Dict, backtest: Dict, stocks: List[Dict]) -> str:
        """
        生成执行摘要
        
        Args:
            strategy: 策略信息
            backtest: 回测结果
            stocks: 推荐股票
            
        Returns:
            执行摘要文本
        """
        prompt = f"""请为以下投资分析生成一个简洁有力的执行摘要（200-300 字）。

【策略信息】
名称：{strategy.get('name', '未知')}
描述：{strategy.get('description', '')}

【回测表现】
总收益：{backtest.get('total_return_pct', 0):.2f}%
年化收益：{backtest.get('annual_return_pct', 0):.2f}%
夏普比率：{backtest.get('sharpe_ratio', 0):.2f}
最大回撤：{backtest.get('max_drawdown_pct', 0):.2f}%
胜率：{backtest.get('win_rate_pct', 0):.1f}%

【推荐股票】
{json.dumps(stocks[:3], ensure_ascii=False, indent=2)}

请用专业但易懂的语言，总结：
1. 策略的核心优势
2. 历史表现亮点
3. 当前投资建议
4. 主要风险提示

输出纯文本，不要 Markdown 格式。"""
        
        print("🧠 LLM 正在生成执行摘要...")
        return self.llm.generate(prompt)
    
    def explain_strategy_logic(self, strategy: Dict) -> str:
        """
        解释策略逻辑
        
        Args:
            strategy: 策略配置
            
        Returns:
            策略逻辑解释
        """
        prompt = f"""请用通俗易懂的语言，解释以下投资策略的逻辑。

【策略名称】{strategy.get('name', '未知')}

【策略描述】{strategy.get('description', '')}

【核心逻辑】{strategy.get('logic', '')}

【买入条件】
{json.dumps(strategy.get('entry_conditions', []), ensure_ascii=False, indent=2)}

【卖出条件】
{json.dumps(strategy.get('exit_conditions', []), ensure_ascii=False, indent=2)}

请解释：
1. 这个策略的核心思想是什么？（用生活中的例子类比）
2. 为什么这些买入/卖出条件是有效的？
3. 什么市场环境下这个策略最有效？
4. 什么情况下这个策略可能失效？

输出 300-500 字的解释，使用通俗易懂的语言，避免过多专业术语。"""
        
        print("🧠 LLM 正在解释策略逻辑...")
        return self.llm.generate(prompt)
    
    def analyze_backtest_result(self, backtest: Dict) -> str:
        """
        分析回测结果
        
        Args:
            backtest: 回测数据
            
        Returns:
            回测分析文本
        """
        prompt = f"""请专业分析以下回测结果。

【回测数据】
总收益率：{backtest.get('total_return_pct', 0):.2f}%
年化收益：{backtest.get('annual_return_pct', 0):.2f}%
夏普比率：{backtest.get('sharpe_ratio', 0):.2f}
最大回撤：{backtest.get('max_drawdown_pct', 0):.2f}%
胜率：{backtest.get('win_rate_pct', 0):.1f}%
交易次数：{backtest.get('trade_count', 0)}
评估结果：{backtest.get('evaluation', 'UNKNOWN')}

请分析：
1. 收益表现如何？（与大盘对比）
2. 风险调整后收益如何？（夏普比率解读）
3. 风险控制如何？（最大回撤评估）
4. 策略稳定性如何？（胜率 + 交易次数）
5. 综合评估和建议

输出 300-400 字的专业分析。"""
        
        print("🧠 LLM 正在分析回测结果...")
        return self.llm.generate(prompt)
    
    def generate_risk_warning(self, strategy: Dict, market_context: str = "") -> str:
        """
        生成风险提示
        
        Args:
            strategy: 策略配置
            market_context: 市场环境
            
        Returns:
            风险提示文本
        """
        prompt = f"""请为以下投资策略生成风险提示。

【策略信息】
名称：{strategy.get('name', '未知')}
类型：{strategy.get('trading_style', '短线')}
止损：{strategy.get('risk_management', {}).get('stop_loss', 0) * 100:.1f}%

【市场环境】{market_context if market_context else "当前 A 股市场"}

请列出：
1. 策略特有的风险
2. 市场风险
3. 执行风险
4. 给投资者的具体建议

输出格式清晰的风险提示，使用⚠️emoji 标记重要风险。"""
        
        print("🧠 LLM 正在生成风险提示...")
        return self.llm.generate(prompt)
    
    def _build_enhance_prompt(self, report_data: Dict) -> str:
        """构建报告增强提示词"""
        
        return f"""你是一个专业的投资顾问。请将以下数据转换为一份专业、有深度的投资分析报告。

【基础数据】
{json.dumps(report_data, ensure_ascii=False, indent=2)}

【报告要求】
1. 使用专业的投资分析语言
2. 结构清晰，层次分明
3. 数据解读深入，不只是罗列
4. 给出明确的投资建议
5. 风险提示充分但不过度

【报告结构】
## 📋 执行摘要
（200-300 字，核心观点）

## 🎯 投资策略详解
（策略逻辑、适用场景）

## 📊 历史表现分析
（回测数据深度解读）

## 💼 当前投资建议
（具体操作建议）

## ⚠️ 风险提示
（全面但理性的风险说明）

请输出完整的 Markdown 格式报告。"""
    
    def create_daily_brief(self, strategies: List[Dict], market_data: Dict) -> str:
        """
        创建每日简报
        
        Args:
            strategies: 策略表现列表
            market_data: 市场数据
            
        Returns:
            每日简报文本
        """
        prompt = f"""请生成一份投资每日简报。

【策略表现】
{json.dumps(strategies, ensure_ascii=False, indent=2)}

【市场概况】
{json.dumps(market_data, ensure_ascii=False, indent=2)}

【简报结构】
📈 市场概览
🏆 最佳策略
📉 需关注策略
💡 今日建议

输出简洁的日报格式，500 字以内。"""
        
        print("🧠 LLM 正在生成每日简报...")
        return self.llm.generate(prompt)


if __name__ == "__main__":
    # 测试报告增强
    print("=" * 60)
    print("LLM 报告增强器测试")
    print("=" * 60)
    
    enhancer = LLMReportEnhancer()
    
    # 模拟报告数据
    report_data = {
        "strategy": {
            "name": "均值回归策略",
            "description": "当股价偏离均线时反向操作",
            "logic": "价格围绕价值波动，超卖时买入，超买时卖出"
        },
        "backtest": {
            "total_return_pct": 52.52,
            "annual_return_pct": 50.08,
            "sharpe_ratio": 2.06,
            "max_drawdown_pct": 1.55,
            "win_rate_pct": 84.2,
            "trade_count": 19
        },
        "stocks": [
            {"symbol": "000001", "name": "平安银行", "reason": "超卖信号"},
            {"symbol": "600036", "name": "招商银行", "reason": "估值合理"}
        ]
    }
    
    # 生成执行摘要
    print("\n生成执行摘要...\n")
    summary = enhancer.generate_executive_summary(
        report_data['strategy'],
        report_data['backtest'],
        report_data['stocks']
    )
    print(summary)
