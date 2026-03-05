"""
运行 AI 投资决策 - 简化版
"""

import os
import sys
sys.path.insert(0, '.')

os.environ['DASHSCOPE_API_KEY'] = 'sk-fb6aa9235b6b4627aa2ac5f7295db04c'

from agents.memory import AgentMemory
from agents.agents.macro import MacroAnalyst
from agents.agents.quant import QuantAnalyst
from agents.agents.risk import RiskOfficer
from agents.agents.cio import ChiefInvestmentOfficer

print("="*60)
print("AI 投资顾问 - 智能体系统")
print("="*60)

memory = AgentMemory()
macro = MacroAnalyst(memory=memory)
quant = QuantAnalyst(memory=memory)
risk = RiskOfficer(memory=memory)
cio = ChiefInvestmentOfficer(memory=memory, macro_analyst=macro, quant_analyst=quant, risk_officer=risk)

print("\n开始 AI 决策...\n")
report = cio.make_decision()

from datetime import datetime
report_file = f"reports/ai_decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
with open(report_file, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"\n报告已保存：{report_file}")
print("完成")
