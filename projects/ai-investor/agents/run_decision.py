"""
每日决策入口 - 独立运行版

解决编码问题，直接调用 CIO
"""

import os
import sys
from pathlib import Path

# 设置编码
os.environ['PYTHONUTF8'] = '1'
sys.stdout.reconfigure(encoding='utf-8')

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.memory import AgentMemory
from agents.agents.macro import MacroAnalyst
from agents.agents.quant import QuantAnalyst
from agents.agents.risk import RiskOfficer
from agents.agents.cio import ChiefInvestmentOfficer


def main():
    """主函数"""
    print("\n" + "="*60)
    print("AI 投资顾问 - 智能体系统")
    print("="*60)
    print(f"日期：{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # 检查 API Key
    api_key = os.environ.get("DASHSCOPE_API_KEY", "")
    if not api_key:
        print("\n[错误] 未设置 DASHSCOPE_API_KEY 环境变量")
        return
    
    print(f"\n[OK] API Key 已配置 ({api_key[:15]}...)")
    
    # 初始化记忆系统
    print("[OK] 初始化记忆系统...")
    memory = AgentMemory()
    
    # 创建各分析师
    print("[OK] 创建智能体团队...")
    macro = MacroAnalyst(memory=memory)
    quant = QuantAnalyst(memory=memory)
    risk = RiskOfficer(memory=memory)
    
    # 创建 CIO
    cio = ChiefInvestmentOfficer(
        memory=memory,
        macro_analyst=macro,
        quant_analyst=quant,
        risk_officer=risk
    )
    
    # 运行决策
    print("\n开始 AI 投资决策流程...\n")
    report = cio.make_decision()
    
    # 保存报告
    from datetime import datetime
    report_file = Path(__file__).parent.parent / "reports" / f"ai_decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n[OK] 报告已保存：{report_file}")
    print("\n" + "="*60)
    print("AI 投资决策完成")
    print("="*60)
    
    return report


if __name__ == "__main__":
    main()
