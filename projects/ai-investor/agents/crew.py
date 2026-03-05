"""
投资智能体协作流程

基于 CrewAI 组织多智能体协作完成投资决策
"""

from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path


class InvestmentCrew:
    """
    投资智能体团队
    
    组织宏观分析师、量化分析师、风控官、CIO 协作完成投资决策
    """
    
    def __init__(self, llm=None, memory=None, config=None):
        self.llm = llm
        self.memory = memory
        self.config = config
        
        # 延迟导入，避免循环依赖
        self._agents = {}
        self._crew = None
        
        # 初始化智能体
        self._init_agents()
    
    def _init_agents(self):
        """初始化各智能体"""
        from .agents.macro import MacroAnalyst
        from .agents.quant import QuantAnalyst
        from .agents.risk import RiskOfficer
        from .agents.cio import ChiefInvestmentOfficer
        
        # 创建各分析师智能体
        self._agents['macro'] = MacroAnalyst(llm=self.llm, memory=self.memory)
        self._agents['quant'] = QuantAnalyst(llm=self.llm, memory=self.memory)
        self._agents['risk'] = RiskOfficer(llm=self.llm, memory=self.memory)
        
        # 创建 CIO
        self._agents['cio'] = ChiefInvestmentOfficer(
            llm=self.llm,
            memory=self.memory,
            macro_analyst=self._agents['macro'],
            quant_analyst=self._agents['quant'],
            risk_officer=self._agents['risk']
        )
    
    def run_daily_decision(self, context: Dict = None) -> str:
        """
        运行每日决策流程
        
        Args:
            context: 决策上下文
            
        Returns:
            投资决策报告
        """
        print("\n" + "="*60)
        print("[AI 投资顾问] 每日决策")
        print("="*60)
        print(f"日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # CIO 主导决策流程
        report = self._agents['cio'].make_decision(context)
        
        # 保存报告
        self._save_report(report)
        
        print("\n" + "="*60)
        print("[OK] 每日决策完成")
        print("="*60)
        
        return report
    
    def _save_report(self, report: str):
        """保存报告"""
        from .config import AgentConfig
        
        report_file = AgentConfig.REPORT_DIR / f"agent_decision_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n[文件] 报告已保存：{report_file}")
    
    def get_agent(self, name: str):
        """获取指定智能体"""
        return self._agents.get(name)
    
    def get_all_agents(self) -> Dict:
        """获取所有智能体"""
        return self._agents.copy()
    
    def run_crewai_mode(self, context: Dict = None):
        """
        使用 CrewAI 原生模式运行
        
        需要 crewai 库支持
        """
        try:
            from crewai import Crew, Process
            
            # 创建 Crew
            crew = Crew(
                agents=list(self._agents.values()),
                process=Process.sequential,  # 顺序执行
                verbose=True
            )
            
            # 执行
            result = crew.kickoff(inputs=context or {})
            
            return result
            
        except ImportError:
            print("⚠️ crewai 未安装，使用自主模式")
            return self.run_daily_decision(context)


def create_investment_crew(llm=None, memory=None) -> InvestmentCrew:
    """
    创建投资智能体团队
    
    Args:
        llm: LLM 实例
        memory: 记忆系统实例
        
    Returns:
        InvestmentCrew 实例
    """
    return InvestmentCrew(llm=llm, memory=memory)


if __name__ == "__main__":
    # 测试智能体协作
    from .memory import AgentMemory
    
    print("="*60)
    print("[测试] 投资智能体协作系统")
    print("="*60)
    
    # 创建记忆系统
    memory = AgentMemory()
    
    # 创建智能体团队
    crew = create_investment_crew(memory=memory)
    
    # 运行每日决策
    print("\n开始每日决策流程...\n")
    report = crew.run_daily_decision()
    
    print("\n" + "="*60)
    print("[完成] 测试结束")
    print("="*60)
