"""
每日决策入口

运行 AI 投资顾问的每日投资决策流程
"""

import sys
import os
from pathlib import Path

# 设置编码
os.environ['PYTHONUTF8'] = '1'
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.config import AgentConfig
from agents.memory import AgentMemory
from agents.crew import InvestmentCrew


def main():
    """主函数"""
    print("\n" + "="*60)
    print("[AI 投资顾问] 智能体系统")
    print("="*60)
    
    # 验证配置
    print("\n检查配置...")
    AgentConfig.validate()
    
    # 初始化记忆系统
    print("初始化记忆系统...")
    memory = AgentMemory()
    
    # 创建智能体团队
    print("创建智能体团队...")
    crew = InvestmentCrew(memory=memory)
    
    # 运行每日决策
    print("\n")
    report = crew.run_daily_decision()
    
    # 输出摘要
    print("\n" + "="*60)
    print("[决策摘要]")
    print("="*60)
    print("[OK] 投资决策已完成")
    print(f"[文件] 报告已保存至：reports/")
    print("\n查看完整报告获取详细操作建议。")
    
    return report


if __name__ == "__main__":
    main()
