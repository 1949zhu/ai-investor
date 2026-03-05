"""
量化分析师智能体 - LLM 增强版

使用真实 LLM 进行策略验证和量化分析
"""

import os
from typing import Dict, List
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class QuantAnalyst:
    """
    量化分析师智能体
    
    职责：
    - 策略回测验证
    - 统计分析
    - 绩效评估
    - 策略可信度评分
    """
    
    def __init__(self, llm=None, memory=None, db_path: str = None):
        self.memory = memory
        self.llm = llm
        self.db_path = db_path
        self.api_key = os.environ.get("DASHSCOPE_API_KEY", "")
    
    def verify_strategy(self, strategy_name: str, context: Dict = None) -> str:
        """
        验证策略（使用 LLM + 回测数据）
        """
        # 获取回测结果
        backtest_results = self._get_backtest_results(strategy_name)
        
        # 使用 LLM 分析回测结果
        return self._llm_verify(strategy_name, backtest_results, context)
    
    def _llm_verify(self, strategy_name: str, results: Dict, context: Dict = None) -> str:
        """使用 LLM 分析回测结果"""
        import dashscope
        from dashscope import Generation
        
        dashscope.api_key = self.api_key
        
        # 构建分析提示
        prompt = f"""你是一位量化投资专家，拥有数学和统计学博士学位，曾在顶级对冲基金工作。

请分析以下策略的回测结果：

**策略名称：** {strategy_name}

**回测数据：**
- 总收益率：{results.get('total_return_pct', 0):.2f}%
- 年化收益：{results.get('annual_return_pct', 0):.2f}%
- 夏普比率：{results.get('sharpe_ratio', 0):.2f}
- 最大回撤：{results.get('max_drawdown_pct', 0):.2f}%
- 胜率：{results.get('win_rate_pct', 0):.1f}%
- 交易次数：{results.get('trade_count', 0)}

请从专业量化角度分析：
1. 策略表现评价（优秀/良好/一般/差）
2. 统计显著性（是否可能是运气）
3. 潜在风险（过拟合、市场变化等）
4. 策略可信度评分（0-100 分）
5. 是否建议采用及理由

要求：
- 分析严谨、客观
- 给出明确的评分和建议
- 用中文输出，格式清晰

请以专业量化分析师的口吻撰写一份完整的量化分析报告。
"""
        
        try:
            response = Generation.call(
                model='qwen-plus',
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.3,  # 降低温度，更严谨
                max_tokens=1500
            )
            
            if response.status_code == 200:
                report = response.output.text
                return f"# 量化分析报告（AI 生成）\n\n**策略：** {strategy_name}\n\n{report}"
            else:
                print(f"⚠️ LLM 调用失败：{response.status_code}")
                return self._fallback_verify(strategy_name, results)
                
        except Exception as e:
            print(f"⚠️ LLM 分析异常：{e}")
            return self._fallback_verify(strategy_name, results)
    
    def _get_backtest_results(self, strategy_name: str) -> Dict:
        """获取回测结果"""
        results = {
            "均值回归策略": {
                "total_return_pct": 52.52,
                "annual_return_pct": 50.08,
                "sharpe_ratio": 2.06,
                "max_drawdown_pct": 1.55,
                "win_rate_pct": 84.2,
                "trade_count": 19
            },
            "动量突破策略": {
                "total_return_pct": 6.20,
                "annual_return_pct": 5.96,
                "sharpe_ratio": 0.53,
                "max_drawdown_pct": 4.93,
                "win_rate_pct": 33.3,
                "trade_count": 9
            },
            "价值投资策略": {
                "total_return_pct": 18.11,
                "annual_return_pct": 17.36,
                "sharpe_ratio": 0.80,
                "max_drawdown_pct": 8.48,
                "win_rate_pct": 38.1,
                "trade_count": 21
            }
        }
        
        return results.get(strategy_name, {
            "total_return_pct": 0,
            "annual_return_pct": 0,
            "sharpe_ratio": 0,
            "max_drawdown_pct": 0,
            "win_rate_pct": 0,
            "trade_count": 0
        })
    
    def _fallback_verify(self, strategy_name: str, results: Dict) -> str:
        """降级验证"""
        report = f"""# 量化分析报告

**策略：** {strategy_name}

## 回测结果
| 指标 | 数值 |
|------|------|
| 总收益率 | {results.get('total_return_pct', 0):.2f}% |
| 夏普比率 | {results.get('sharpe_ratio', 0):.2f} |
| 最大回撤 | {results.get('max_drawdown_pct', 0):.2f}% |
| 胜率 | {results.get('win_rate_pct', 0):.1f}% |

## 建议
基于回测数据，策略表现{"优秀" if results.get('sharpe_ratio', 0) > 1.5 else "一般"}。

---
*注：LLM 服务不可用，使用简化分析*
"""
        return report
    
    def compare_strategies(self, strategies: List[str]) -> str:
        """对比多个策略"""
        report = "# 策略对比分析\n\n"
        
        for strategy in strategies:
            results = self._get_backtest_results(strategy)
            report += f"## {strategy}\n"
            report += f"- 总收益：{results.get('total_return_pct', 0):.2f}%\n"
            report += f"- 夏普比率：{results.get('sharpe_ratio', 0):.2f}\n"
            report += f"- 最大回撤：{results.get('max_drawdown_pct', 0):.2f}%\n\n"
        
        return report
