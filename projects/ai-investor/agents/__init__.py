"""
AI 投资顾问智能体系统

基于 CrewAI 构建的多智能体投资顾问系统
"""

from .config import AgentConfig
from .memory import AgentMemory
from .agents.macro import MacroAnalyst
from .agents.quant import QuantAnalyst
from .agents.risk import RiskOfficer
from .agents.cio import ChiefInvestmentOfficer
from .crew import InvestmentCrew

__version__ = "1.0.0"
__all__ = [
    "AgentConfig",
    "AgentMemory",
    "MacroAnalyst",
    "QuantAnalyst",
    "RiskOfficer",
    "ChiefInvestmentOfficer",
    "InvestmentCrew"
]
