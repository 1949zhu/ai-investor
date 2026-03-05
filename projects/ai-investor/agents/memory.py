"""
智能体记忆系统

实现短期记忆、长期记忆、决策日志和反思功能
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class DecisionRecord:
    """决策记录"""
    date: str
    market_state: str
    decision: str
    reasoning: str
    confidence: float
    outcome: Optional[str] = None
    reflection: Optional[str] = None


@dataclass
class CaseRecord:
    """历史案例"""
    date: str
    situation: str  # 市场情况
    action: str     # 采取的行动
    result: str     # 结果
    lesson: str     # 教训


class AgentMemory:
    """
    智能体记忆系统
    
    功能：
    - 短期记忆：当前分析上下文
    - 长期记忆：历史决策案例
    - 决策日志：记录所有决策
    - 反思：定期复盘
    """
    
    def __init__(self, config=None):
        from .config import AgentConfig
        self.config = config or AgentConfig
        
        self.short_term_file = self.config.SHORT_TERM_MEMORY_FILE
        self.decision_log_file = self.config.DECISION_LOG_FILE
        self.reflection_file = self.config.REFLECTION_FILE
        self.long_term_dir = self.config.LONG_TERM_MEMORY_DIR
        
        # 加载短期记忆
        self.short_term = self._load_short_term()
    
    # ========== 短期记忆 ==========
    
    def _load_short_term(self) -> Dict:
        """加载短期记忆"""
        if self.short_term_file.exists():
            with open(self.short_term_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            "market_state": None,
            "pending_analysis": [],
            "context": {}
        }
    
    def save_short_term(self):
        """保存短期记忆"""
        with open(self.short_term_file, 'w', encoding='utf-8') as f:
            json.dump(self.short_term, f, ensure_ascii=False, indent=2)
    
    def set_market_state(self, state: str):
        """设置市场状态"""
        self.short_term["market_state"] = state
        self.save_short_term()
    
    def get_market_state(self) -> Optional[str]:
        """获取市场状态"""
        return self.short_term.get("market_state")
    
    def add_context(self, key: str, value: Any):
        """添加上下文信息"""
        self.short_term["context"][key] = value
        self.save_short_term()
    
    def get_context(self, key: str = None) -> Any:
        """获取上下文信息"""
        if key:
            return self.short_term["context"].get(key)
        return self.short_term["context"]
    
    def clear_short_term(self):
        """清空短期记忆"""
        self.short_term = {
            "current_date": datetime.now().strftime("%Y-%m-%d"),
            "market_state": None,
            "pending_analysis": [],
            "context": {}
        }
        self.save_short_term()
    
    # ========== 决策日志 ==========
    
    def log_decision(self, decision: DecisionRecord):
        """记录决策"""
        log = self._load_decision_log()
        log.append(asdict(decision))
        self._save_decision_log(log)
    
    def _load_decision_log(self) -> List[Dict]:
        """加载决策日志"""
        if self.decision_log_file.exists():
            with open(self.decision_log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_decision_log(self, log: List[Dict]):
        """保存决策日志"""
        with open(self.decision_log_file, 'w', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
    
    def get_decision_history(self, limit: int = 30) -> List[Dict]:
        """获取历史决策"""
        log = self._load_decision_log()
        return log[-limit:]
    
    def update_decision_outcome(self, date: str, outcome: str, reflection: str = None):
        """更新决策结果"""
        log = self._load_decision_log()
        for record in log:
            if record.get("date") == date:
                record["outcome"] = outcome
                if reflection:
                    record["reflection"] = reflection
                break
        self._save_decision_log(log)
    
    # ========== 长期记忆（案例库） ==========
    
    def add_case(self, case: CaseRecord):
        """添加案例"""
        case_file = self.long_term_dir / f"case_{case.date}.json"
        with open(case_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(case), f, ensure_ascii=False, indent=2)
    
    def search_similar_cases(self, situation: str, limit: int = 5) -> List[Dict]:
        """搜索类似案例（简单关键词匹配）"""
        cases = []
        for case_file in self.long_term_dir.glob("case_*.json"):
            with open(case_file, 'r', encoding='utf-8') as f:
                case = json.load(f)
                # 简单匹配
                if any(keyword in case.get("situation", "") for keyword in situation.split()):
                    cases.append(case)
        return cases[:limit]
    
    def get_all_cases(self) -> List[Dict]:
        """获取所有案例"""
        cases = []
        for case_file in self.long_term_dir.glob("case_*.json"):
            with open(case_file, 'r', encoding='utf-8') as f:
                cases.append(json.load(f))
        return cases
    
    # ========== 反思 ==========
    
    def add_reflection(self, date: str, content: str):
        """添加反思"""
        reflections = self._load_reflections()
        reflections.append({
            "date": date,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self._save_reflections(reflections)
    
    def _load_reflections(self) -> List[Dict]:
        """加载反思记录"""
        if self.reflection_file.exists():
            with open(self.reflection_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_reflections(self, reflections: List[Dict]):
        """保存反思记录"""
        with open(self.reflection_file, 'w', encoding='utf-8') as f:
            json.dump(reflections, f, ensure_ascii=False, indent=2)
    
    def get_recent_reflections(self, limit: int = 10) -> List[Dict]:
        """获取最近的反思"""
        reflections = self._load_reflections()
        return reflections[-limit:]
    
    # ========== 学习 ==========
    
    def learn_from_outcome(self, date: str, outcome: str, actual_return: float):
        """从结果中学习"""
        # 找到对应决策
        log = self._load_decision_log()
        for record in log:
            if record.get("date") == date:
                # 生成反思
                expected = record.get("confidence", 0)
                success = actual_return > 0
                
                reflection = f"决策置信度{expected:.0%}，实际收益{actual_return:.2%}，"
                if success and expected > 0.7:
                    reflection += "判断准确，策略有效"
                elif not success and expected > 0.7:
                    reflection += "判断失误，需要分析原因"
                elif success and expected < 0.5:
                    reflection += "低估了机会，下次可以更果断"
                else:
                    reflection += "符合预期"
                
                self.add_reflection(date, reflection)
                
                # 更新决策记录
                record["outcome"] = outcome
                record["actual_return"] = actual_return
                break
        
        self._save_decision_log(log)
        
        # 添加到案例库
        case = CaseRecord(
            date=date,
            situation=self.get_market_state() or "未知",
            action=log[-1].get("decision", "") if log else "",
            result=outcome,
            lesson=reflection
        )
        self.add_case(case)


if __name__ == "__main__":
    # 测试记忆系统
    memory = AgentMemory()
    
    # 测试短期记忆
    memory.set_market_state("震荡上行")
    memory.add_context("sentiment", "谨慎乐观")
    print(f"市场状态：{memory.get_market_state()}")
    print(f"上下文：{memory.get_context()}")
    
    # 测试决策日志
    decision = DecisionRecord(
        date="2026-03-05",
        market_state="震荡上行",
        decision="加仓科技股 10%",
        reasoning="宏观向好 + 量化验证通过",
        confidence=0.75
    )
    memory.log_decision(decision)
    print(f"决策历史：{memory.get_decision_history(5)}")
