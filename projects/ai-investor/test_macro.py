"""
测试宏观分析师 - 直接使用 LLM
"""

import os
import sys
sys.path.insert(0, '.')

os.environ['DASHSCOPE_API_KEY'] = 'sk-fb6aa9235b6b4627aa2ac5f7295db04c'

from agents.memory import AgentMemory
from agents.agents.macro import MacroAnalyst

print("测试宏观分析师...")
memory = AgentMemory()
macro = MacroAnalyst(memory=memory)

print("开始分析...\n")
report = macro.analyze()

print(report[:500] if len(report) > 500 else report)
print("\n完成")
