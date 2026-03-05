"""
智能体系统配置
"""

import os
from pathlib import Path
from typing import Dict, Optional


class AgentConfig:
    """智能体配置"""
    
    # ===== LLM 配置 =====
    LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "dashscope")
    LLM_MODEL = os.environ.get("LLM_MODEL", "qwen-plus")
    LLM_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
    LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "")
    
    # ===== 风险边界配置 =====
    RISK_LIMITS = {
        "max_drawdown": 0.15,        # 最大回撤 15%
        "single_stock_max": 0.20,    # 单只股票上限 20%
        "single_sector_max": 0.40,   # 单行业上限 40%
        "cash_min": 0.10,            # 现金下限 10%
        "daily_trade_max": 0.05,     # 日交易上限 5%
        "stop_loss": 0.08,           # 止损线 8%
        "take_profit": 0.20,         # 止盈线 20%
        "leverage_allowed": False,   # 禁止杠杆
    }
    
    # ===== 记忆系统配置 =====
    MEMORY_DIR = Path(__file__).parent.parent / "storage" / "agent_memory"
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    
    SHORT_TERM_MEMORY_FILE = MEMORY_DIR / "short_term.json"
    LONG_TERM_MEMORY_DIR = MEMORY_DIR / "long_term"
    LONG_TERM_MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    
    DECISION_LOG_FILE = MEMORY_DIR / "decision_log.json"
    REFLECTION_FILE = MEMORY_DIR / "reflections.json"
    
    # ===== 报告配置 =====
    REPORT_DIR = Path(__file__).parent.parent / "reports"
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    
    # ===== 智能体配置 =====
    AGENTS = {
        "macro_analyst": {
            "name": "宏观分析师",
            "role": "宏观经济与市场环境分析",
            "goal": "准确判断宏观经济趋势和市场状态，为投资决策提供宏观依据",
            "backstory": "你是一位经验丰富的宏观经济分析师，擅长解读经济数据、政策动向和市场情绪。"
                        "你曾在大投行担任首席经济学家，对经济周期有深刻理解。"
                        "你的分析总是全面、客观，能够洞察数据背后的趋势。",
        },
        "quant_analyst": {
            "name": "量化分析师",
            "role": "策略回测与量化验证",
            "goal": "通过严谨的数据分析和回测验证，确保投资策略的可靠性和有效性",
            "backstory": "你是一位量化投资专家，拥有数学和统计学博士学位。"
                        "你曾在顶级对冲基金工作，擅长用数据说话。"
                        "你对策略的验证非常严格，不相信没有数据支持的观点。",
        },
        "risk_officer": {
            "name": "风控官",
            "role": "风险评估与仓位控制",
            "goal": "识别和控制投资风险，确保投资组合在可接受的风险范围内运行",
            "backstory": "你是一位资深风控专家，经历过多次市场危机。"
                        "你深知风险控制的重要性，总是从最坏情况出发思考问题。"
                        "你的谨慎帮助基金躲过了多次重大损失。",
        },
        "cio": {
            "name": "首席投资官",
            "role": "最终投资决策",
            "goal": "综合各方意见，做出明智的投资决策，为投资者创造长期价值",
            "backstory": "你是一位传奇投资者，管理过数百亿资金，长期跑赢市场。"
                        "你善于综合各方信息，做出独立判断。"
                        "你重视风险控制，但也敢于在机会来临时下重注。"
                        "你的决策总是经过深思熟虑，有充分的逻辑支持。",
        },
    }
    
    # ===== 任务配置 =====
    TASKS = {
        "macro_analysis": {
            "description": "分析当前宏观经济环境和市场状态",
            "expected_output": "包含经济数据解读、政策分析、市场情绪判断的宏观分析报告",
        },
        "quant_verification": {
            "description": "对投资策略进行回测验证",
            "expected_output": "包含回测结果、统计显著性、策略可信度评分的量化分析报告",
        },
        "risk_assessment": {
            "description": "评估投资风险和仓位建议",
            "expected_output": "包含风险评估、压力测试结果、仓位限制的风险分析报告",
        },
        "final_decision": {
            "description": "综合各方意见，做出最终投资决策",
            "expected_output": "包含市场判断、操作建议、决策理由、风险提示的完整投资决策报告",
        },
    }
    
    # ===== 汇报配置 =====
    REPORT_TIME = "09:00"  # 每日汇报时间
    REPORT_FORMAT = "markdown"
    
    @classmethod
    def get_llm_config(cls) -> Dict:
        """获取 LLM 配置"""
        config = {
            "model": cls.LLM_MODEL,
        }
        
        if cls.LLM_API_KEY:
            config["api_key"] = cls.LLM_API_KEY
        
        if cls.LLM_BASE_URL:
            config["base_url"] = cls.LLM_BASE_URL
        
        return config
    
    @classmethod
    def get_risk_limit(cls, key: str) -> float:
        """获取风险限制"""
        return cls.RISK_LIMITS.get(key, 0)
    
    @classmethod
    def get_agent_config(cls, agent_name: str) -> Optional[Dict]:
        """获取智能体配置"""
        return cls.AGENTS.get(agent_name)
    
    @classmethod
    def get_task_config(cls, task_name: str) -> Optional[Dict]:
        """获取任务配置"""
        return cls.TASKS.get(task_name)
    
    @classmethod
    def validate(cls) -> bool:
        """验证配置"""
        if not cls.LLM_API_KEY:
            print("⚠️ 未设置 DASHSCOPE_API_KEY 环境变量")
            print("  智能体系统将使用模拟模式")
            return False
        return True
