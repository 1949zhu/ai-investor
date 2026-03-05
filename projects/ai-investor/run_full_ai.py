"""
完整 AI 投资决策流程
"""

import os
import sys
sys.path.insert(0, '.')

os.environ['DASHSCOPE_API_KEY'] = 'sk-fb6aa9235b6b4627aa2ac5f7295db04c'

from datetime import datetime
from agents.memory import AgentMemory, DecisionRecord
from agents.agents.macro import MacroAnalyst
from agents.agents.quant import QuantAnalyst
from agents.agents.risk import RiskOfficer
from agents.agents.cio import ChiefInvestmentOfficer

print("="*60)
print("AI 投资顾问 - 智能体决策系统")
print("="*60)
print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
print()

# 初始化
memory = AgentMemory()
macro = MacroAnalyst(memory=memory)
quant = QuantAnalyst(memory=memory)
risk = RiskOfficer(memory=memory)
cio = ChiefInvestmentOfficer(memory=memory, macro_analyst=macro, quant_analyst=quant, risk_officer=risk)

# 执行决策
print("[1/4] 宏观分析...")
macro_report = macro.analyze()
print(f"     完成 ({len(macro_report)} 字)")

print("[2/4] 量化验证...")
quant_report = quant.verify_strategy("均值回归策略")
print(f"     完成 ({len(quant_report)} 字)")

print("[3/4] 风险评估...")
risk_report = risk.assess_risk()
print(f"     完成 ({len(risk_report)} 字)")

print("[4/4] CIO 综合决策...")
decision = cio.make_decision()
print(f"     完成 ({len(decision)} 字)")

# 保存
report_file = f"reports/ai_investor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
with open(report_file, 'w', encoding='utf-8') as f:
    f.write(decision)

print()
print("="*60)
print(f"AI 决策完成！")
print(f"报告：{report_file}")
print("="*60)
