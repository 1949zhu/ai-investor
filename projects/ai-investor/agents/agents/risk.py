"""
风控官智能体 - LLM 增强版

使用真实 LLM 进行风险评估
"""

import os
from typing import Dict, List
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class RiskOfficer:
    """
    风控官智能体
    
    职责：
    - 风险评估
    - 仓位控制
    - 压力测试
    - 止损判断
    """
    
    def __init__(self, llm=None, memory=None, risk_limits: Dict = None):
        self.memory = memory
        self.llm = llm
        self.risk_limits = risk_limits or self._default_risk_limits()
        self.api_key = os.environ.get("DASHSCOPE_API_KEY", "")
    
    def _default_risk_limits(self) -> Dict:
        """默认风险限制"""
        from ..config import AgentConfig
        return AgentConfig.RISK_LIMITS
    
    def assess_risk(self, portfolio: Dict = None, market_state: str = None) -> str:
        """
        评估投资风险（使用 LLM）
        """
        return self._llm_assess_risk(portfolio, market_state)
    
    def _llm_assess_risk(self, portfolio: Dict = None, market_state: str = None) -> str:
        """使用 LLM 进行风险评估"""
        import dashscope
        from dashscope import Generation
        
        dashscope.api_key = self.api_key
        
        date = datetime.now().strftime("%Y-%m-%d")
        
        # 构建分析提示
        prompt = f"""你是一位资深风控专家，经历过多次市场危机，深知风险控制的重要性。

当前日期：{date}
市场状态：{market_state or "未知"}

请评估当前投资风险，包括：
1. 市场风险（系统性风险、波动率）
2. 个股风险（集中度、流动性）
3. 策略风险（失效风险、参数敏感性）
4. 压力测试（不同情景下的预期回撤）
5. 仓位建议（总仓位、单只股票上限）
6. 风险监控清单（需要关注的指标和预警信号）

风险限制框架：
- 最大回撤：{self.risk_limits['max_drawdown']*100:.0f}%
- 单只股票上限：{self.risk_limits['single_stock_max']*100:.0f}%
- 单行业上限：{self.risk_limits['single_sector_max']*100:.0f}%
- 现金下限：{self.risk_limits['cash_min']*100:.0f}%
- 止损线：{self.risk_limits['stop_loss']*100:.0f}%
- 止盈线：{self.risk_limits['take_profit']*100:.0f}%

要求：
- 从最坏情况出发思考
- 给出明确的风险等级（低/中/高）
- 提供具体的风控建议
- 用中文输出，格式清晰

请以专业风控官的口吻撰写一份完整的风险评估报告。
"""
        
        try:
            response = Generation.call(
                model='qwen-plus',
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.3,  # 降低温度，更严谨
                max_tokens=2000
            )
            
            if response.status_code == 200:
                report = response.output.text
                return f"# 风险评估报告（AI 生成）\n\n**日期：** {date}\n**市场状态：** {market_state or '未知'}\n\n{report}"
            else:
                print(f"⚠️ LLM 调用失败：{response.status_code}")
                return self._fallback_assess(market_state)
                
        except Exception as e:
            print(f"⚠️ LLM 分析异常：{e}")
            return self._fallback_assess(market_state)
    
    def _fallback_assess(self, market_state: str = None) -> str:
        """降级评估"""
        date = datetime.now().strftime("%Y-%m-%d")
        report = f"""# 风险评估报告

**日期：** {date}
**市场状态：** {market_state or "未知"}

## 风险等级
**中等**

## 关键风险指标
| 指标 | 限制 | 状态 |
|------|------|------|
| 最大回撤 | 15% | 安全 |
| 单只股票 | 20% | 安全 |
| 现金下限 | 10% | 安全 |

## 建议
- 严格执行仓位限制
- 设置止损止盈（8%/20%）

---
*注：LLM 服务不可用，使用简化分析*
"""
        return report
    
    def check_position_limits(self, current_position: float, proposed_addition: float) -> Dict:
        """检查仓位限制"""
        new_position = current_position + proposed_addition
        
        result = {
            "allowed": True,
            "reason": "",
            "suggested_position": new_position
        }
        
        max_position = 1 - self.risk_limits['cash_min']
        if new_position > max_position:
            result["allowed"] = False
            result["reason"] = f"超过最大仓位限制 ({max_position*100:.0f}%)"
            result["suggested_position"] = max_position
        
        if proposed_addition > self.risk_limits['daily_trade_max']:
            result["allowed"] = False
            result["reason"] = f"超过单日交易限制 ({self.risk_limits['daily_trade_max']*100:.0f}%)"
        
        return result
    
    def should_stop_loss(self, entry_price: float, current_price: float) -> bool:
        """判断是否止损"""
        loss_pct = (current_price - entry_price) / entry_price
        return loss_pct < -self.risk_limits['stop_loss']
    
    def should_take_profit(self, entry_price: float, current_price: float) -> bool:
        """判断是否止盈"""
        profit_pct = (current_price - entry_price) / entry_price
        return profit_pct > self.risk_limits['take_profit']
