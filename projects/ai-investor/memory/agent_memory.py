"""
智能体记忆系统 - 跨会话记忆，累积投资经验
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict


class AgentMemory:
    """智能体记忆系统"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "storage" / "agent_memory.db"
        
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 决策日志表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS decision_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                market_state TEXT,
                decision TEXT,
                reasoning TEXT,
                outcome TEXT,
                reflection TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 经验教训表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lessons_learned (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lesson TEXT NOT NULL,
                category TEXT,
                confidence REAL DEFAULT 0.5,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 市场状态表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_regime (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                regime TEXT NOT NULL,
                confidence REAL,
                start_date TEXT,
                end_date TEXT,
                is_current INTEGER DEFAULT 1
            )
        """)
        
        # 策略绩效表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                test_date TEXT,
                return_rate REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                win_rate REAL,
                is_valid INTEGER DEFAULT 1
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_decision(self, date: str, market_state: str, decision: str, 
                     reasoning: str, outcome: str = "待验证"):
        """添加决策记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO decision_log (date, market_state, decision, reasoning, outcome)
            VALUES (?, ?, ?, ?, ?)
        """, (date, market_state, decision, reasoning, outcome))
        
        conn.commit()
        conn.close()
        return True
    
    def update_decision_outcome(self, decision_id: int, outcome: str, reflection: str = None):
        """更新决策结果"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE decision_log 
            SET outcome = ?, reflection = ?
            WHERE id = ?
        """, (outcome, reflection, decision_id))
        
        conn.commit()
        conn.close()
        return True
    
    def add_lesson(self, lesson: str, category: str = None, confidence: float = 0.5):
        """添加经验教训"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO lessons_learned (lesson, category, confidence)
            VALUES (?, ?, ?)
        """, (lesson, category, confidence))
        
        conn.commit()
        conn.close()
        return True
    
    def get_decision_history(self, limit: int = 20) -> List[Dict]:
        """获取决策历史记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, date, market_state, decision, reasoning, outcome, reflection, created_at
            FROM decision_log
            ORDER BY date DESC, id DESC
            LIMIT ?
        """, (limit,))
        
        decisions = [
            {
                "id": r[0],
                "date": r[1],
                "market_state": r[2],
                "decision": r[3],
                "reasoning": r[4],
                "outcome": r[5],
                "reflection": r[6],
                "created_at": r[7]
            }
            for r in cursor.fetchall()
        ]
        
        conn.close()
        return decisions
    
    def get_lessons(self, limit: int = 10) -> List[Dict]:
        """获取经验教训"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT lesson, category, confidence, created_at
            FROM lessons_learned
            ORDER BY confidence DESC, created_at DESC
            LIMIT ?
        """, (limit,))
        
        lessons = [
            {"lesson": r[0], "category": r[1], "confidence": r[2], "created_at": r[3]}
            for r in cursor.fetchall()
        ]
        
        conn.close()
        return lessons
    
    def set_market_regime(self, regime: str, confidence: float):
        """设置当前市场状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 结束当前状态
        cursor.execute("""
            UPDATE market_regime SET is_current = 0, end_date = ?
            WHERE is_current = 1
        """, (datetime.now().strftime("%Y-%m-%d"),))
        
        # 添加新状态
        cursor.execute("""
            INSERT INTO market_regime (regime, confidence, start_date, is_current)
            VALUES (?, ?, ?, 1)
        """, (regime, confidence, datetime.now().strftime("%Y-%m-%d")))
        
        conn.commit()
        conn.close()
        return True
    
    def get_market_regime(self) -> Optional[Dict]:
        """获取当前市场状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT regime, confidence, start_date
            FROM market_regime
            WHERE is_current = 1
            ORDER BY id DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {"regime": row[0], "confidence": row[1], "start_date": row[2]}
        return None
    
    def add_strategy_performance(self, strategy_name: str, return_rate: float,
                                  sharpe_ratio: float, max_drawdown: float,
                                  win_rate: float, test_date: str = None):
        """添加策略绩效"""
        if test_date is None:
            test_date = datetime.now().strftime("%Y-%m-%d")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO strategy_performance 
            (strategy_name, test_date, return_rate, sharpe_ratio, max_drawdown, win_rate)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (strategy_name, test_date, return_rate, sharpe_ratio, max_drawdown, win_rate))
        
        conn.commit()
        conn.close()
        return True
    
    def get_strategy_history(self, strategy_name: str = None, limit: int = 10) -> List[Dict]:
        """获取策略历史绩效"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if strategy_name:
            cursor.execute("""
                SELECT strategy_name, test_date, return_rate, sharpe_ratio, 
                       max_drawdown, win_rate, is_valid
                FROM strategy_performance
                WHERE strategy_name = ?
                ORDER BY test_date DESC
                LIMIT ?
            """, (strategy_name, limit))
        else:
            cursor.execute("""
                SELECT strategy_name, test_date, return_rate, sharpe_ratio, 
                       max_drawdown, win_rate, is_valid
                FROM strategy_performance
                ORDER BY test_date DESC
                LIMIT ?
            """, (limit,))
        
        strategies = [
            {
                "strategy_name": r[0],
                "test_date": r[1],
                "return_rate": r[2],
                "sharpe_ratio": r[3],
                "max_drawdown": r[4],
                "win_rate": r[5],
                "is_valid": bool(r[6])
            }
            for r in cursor.fetchall()
        ]
        
        conn.close()
        return strategies
    
    def get_context_for_agent(self, agent_type: str) -> str:
        """为智能体生成上下文提示"""
        context_parts = []
        
        # 获取当前市场状态
        regime = self.get_market_regime()
        if regime:
            context_parts.append(
                f"当前市场状态：{regime['regime']} "
                f"(置信度：{regime['confidence']:.0%}, 始于：{regime['start_date']})"
            )
        
        # 获取经验教训
        lessons = self.get_lessons(limit=5)
        if lessons:
            context_parts.append("\n历史经验教训:")
            for i, lesson in enumerate(lessons, 1):
                context_parts.append(
                    f"  {i}. {lesson['lesson']} "
                    f"(置信度：{lesson['confidence']:.0%})"
                )
        
        # 获取最近决策
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date, decision, outcome
            FROM decision_log
            ORDER BY date DESC
            LIMIT 3
        """)
        recent_decisions = cursor.fetchall()
        conn.close()
        
        if recent_decisions:
            context_parts.append("\n最近决策记录:")
            for i, dec in enumerate(recent_decisions, 1):
                context_parts.append(
                    f"  {i}. [{dec[0]}] {dec[1][:50]}... → {dec[2]}"
                )
        
        return "\n".join(context_parts)
    
    def export_memory(self, output_path: str = None):
        """导出记忆为 JSON"""
        if output_path is None:
            output_path = Path(__file__).parent.parent / "memory" / "agent_memory.json"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        memory = {
            "exported_at": datetime.now().isoformat(),
            "market_regime": self.get_market_regime(),
            "lessons_learned": self.get_lessons(limit=50),
            "recent_decisions": [],
            "strategy_performance": []
        }
        
        # 获取最近决策
        cursor.execute("""
            SELECT date, market_state, decision, reasoning, outcome, reflection
            FROM decision_log
            ORDER BY date DESC
            LIMIT 20
        """)
        memory["recent_decisions"] = [
            {
                "date": r[0],
                "market_state": r[1],
                "decision": r[2],
                "reasoning": r[3],
                "outcome": r[4],
                "reflection": r[5]
            }
            for r in cursor.fetchall()
        ]
        
        # 获取策略绩效
        cursor.execute("""
            SELECT strategy_name, test_date, return_rate, sharpe_ratio, 
                   max_drawdown, win_rate
            FROM strategy_performance
            ORDER BY test_date DESC
            LIMIT 20
        """)
        memory["strategy_performance"] = [
            {
                "strategy_name": r[0],
                "test_date": r[1],
                "return_rate": r[2],
                "sharpe_ratio": r[3],
                "max_drawdown": r[4],
                "win_rate": r[5]
            }
            for r in cursor.fetchall()
        ]
        
        conn.close()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
        
        return output_path


if __name__ == "__main__":
    # 测试记忆系统
    memory = AgentMemory()
    
    print("测试智能体记忆系统...")
    
    # 添加测试数据
    memory.add_decision(
        date="2026-03-05",
        market_state="震荡市",
        decision="买入中国平安 (601318.SH)",
        reasoning="低估值 + 高股息，防御性强",
        outcome="待验证"
    )
    
    memory.add_lesson(
        lesson="均值回归策略在趋势市中表现不佳，需增加趋势过滤",
        category="策略",
        confidence=0.8
    )
    
    memory.set_market_regime("震荡市", 0.75)
    
    memory.add_strategy_performance(
        strategy_name="均值回归",
        return_rate=0.5252,
        sharpe_ratio=2.06,
        max_drawdown=0.0155,
        win_rate=0.842
    )
    
    # 获取上下文
    context = memory.get_context_for_agent("macro")
    print("\n智能体上下文:")
    print(context)
    
    # 导出记忆
    output = memory.export_memory()
    print(f"\n记忆已导出：{output}")
