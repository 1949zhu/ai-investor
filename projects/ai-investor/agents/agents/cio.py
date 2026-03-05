"""
首席投资官智能体 (CIO) - LLM 增强版

使用真实 LLM 进行最终投资决策
"""

import os
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class ChiefInvestmentOfficer:
    """
    首席投资官智能体
    
    职责：
    - 综合各方意见
    - 做出最终投资决策
    - 生成投资建议报告
    - 向用户汇报
    """
    
    def __init__(self, llm=None, memory=None, macro_analyst=None, quant_analyst=None, risk_officer=None):
        self.memory = memory
        self.llm = llm
        self.api_key = os.environ.get("DASHSCOPE_API_KEY", "")
        
        # 各分析师智能体
        self.macro_analyst = macro_analyst
        self.quant_analyst = quant_analyst
        self.risk_officer = risk_officer
    
    def make_decision(self, context: Dict = None) -> str:
        """
        做出投资决策（使用 LLM 综合决策）
        """
        return self._llm_decision(context)
    
    def _llm_decision(self, context: Dict = None) -> str:
        """
        使用 LLM 进行投资决策
        
        流程：
        1. 收集各方意见
        2. 让 LLM 综合判断
        3. 生成决策报告
        """
        date = datetime.now().strftime("%Y-%m-%d")
        
        # ========== Step 1: 收集各方意见 ==========
        print("\n[Step 1] 收集各方意见...")
        
        # 宏观分析
        if self.macro_analyst:
            print("  - 宏观分析师正在分析...")
            macro_report = self.macro_analyst.analyze(context)
        else:
            macro_report = "暂无宏观分析"
        
        # 量化验证
        if self.quant_analyst:
            print("  - 量化分析师正在验证...")
            quant_report = self.quant_analyst.verify_strategy("均值回归策略", context)
        else:
            quant_report = "暂无量化分析"
        
        # 风险评估
        if self.risk_officer:
            print("  - 风控官正在评估...")
            market_state = self.memory.get_market_state() if self.memory else "未知"
            risk_report = self.risk_officer.assess_risk(market_state=market_state)
        else:
            risk_report = "暂无风险评估"
        
        # ========== Step 2: LLM 综合决策 ==========
        print("\n[Step 2] LLM 综合决策...")
        
        import dashscope
        from dashscope import Generation
        
        dashscope.api_key = self.api_key
        
        # 构建决策提示
        prompt = f"""你是一位传奇首席投资官，管理过数百亿资金，长期跑赢市场。你善于综合各方信息，做出独立判断。

当前日期：{date}

请综合以下三方分析报告，做出最终投资决策：

## 宏观分析报告
{macro_report[:1500]}...

## 量化分析报告
{quant_report[:1500]}...

## 风险评估报告
{risk_report[:1500]}...

请基于以上信息，生成一份完整的投资决策报告，包括：

1. **执行摘要** - 市场判断、操作方向、建议仓位、置信度
2. **宏观分析摘要** - 核心观点、配置建议
3. **量化验证摘要** - 策略回测结果、可信度评分
4. **风险评估摘要** - 风险等级、关键指标、压力测试
5. **今日操作建议** - 具体操作（标的、操作、仓位、止损、止盈）
6. **决策理由** - 为什么做出这个决策
7. **置信度评估** - 整体置信度及来源
8. **风险提示** - 需要注意的风险

要求：
- 决策明确、可执行
- 理由充分、有逻辑
- 风险收益比合理
- 用中文输出，格式清晰，使用 Markdown

请以专业 CIO 的口吻撰写一份完整的投资决策报告。
"""
        
        try:
            response = Generation.call(
                model='qwen-plus',
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.5,
                max_tokens=3000
            )
            
            if response.status_code == 200:
                report = response.output.text
                
                # 记录决策
                if self.memory:
                    from ..memory import DecisionRecord
                    decision = DecisionRecord(
                        date=date,
                        market_state="根据 LLM 分析",
                        decision="详见报告",
                        reasoning="宏观 + 量化 + 风控三方分析",
                        confidence=0.75
                    )
                    self.memory.log_decision(decision)
                
                print("\n[OK] 决策报告生成完成")
                return f"# 投资决策报告\n\n**日期：** {date}\n**决策者：** 首席投资官 (CIO)\n\n{report}"
            else:
                print(f"⚠️ LLM 调用失败：{response.status_code}")
                return self._fallback_decision()
                
        except Exception as e:
            print(f"⚠️ LLM 决策异常：{e}")
            return self._fallback_decision()
    
    def _fallback_decision(self) -> str:
        """降级决策"""
        date = datetime.now().strftime("%Y-%m-%d")
        return f"""# 投资决策报告

**日期：** {date}

⚠️ LLM 服务不可用，无法生成智能决策报告。

请配置有效的 DASHSCOPE_API_KEY 以启用 AI 决策功能。

---
*注：系统降级模式*
"""
    
    def review_decision(self, date: str, actual_return: float) -> str:
        """复盘决策"""
        if self.memory:
            self.memory.learn_from_outcome(date, f"实际收益{actual_return:.2%}", actual_return)
        
        return f"决策复盘报告生成中..."


if __name__ == "__main__":
    # 测试 CIO
    from ..memory import AgentMemory
    from .macro import MacroAnalyst
    from .quant import QuantAnalyst
    from .risk import RiskOfficer
    
    memory = AgentMemory()
    
    print("="*60)
    print("[测试] 首席投资官智能体")
    print("="*60)
    
    macro = MacroAnalyst(memory=memory)
    quant = QuantAnalyst(memory=memory)
    risk = RiskOfficer(memory=memory)
    
    cio = ChiefInvestmentOfficer(
        memory=memory,
        macro_analyst=macro,
        quant_analyst=quant,
        risk_officer=risk
    )
    
    print("\n开始投资决策流程...\n")
    report = cio.make_decision()
    print(report)
