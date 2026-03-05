"""
自主学习机制 - 根据反馈优化决策
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sys


class AutonomousLearner:
    """自主学习系统"""
    
    def __init__(self, memory_db_path: str = None):
        if memory_db_path is None:
            memory_db_path = Path(__file__).parent.parent / "storage" / "agent_memory.db"
        self.db_path = memory_db_path
        self.config_path = Path(__file__).parent.parent / "config" / "learning.json"
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_config()
    
    def _init_config(self):
        """初始化配置"""
        if not self.config_path.exists():
            config = {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "learning_rate": 0.1,  # 学习率
                "min_samples": 10,  # 最小样本数
                "performance_threshold": 0.55,  # 胜率阈值
                "adjustment_rules": []
            }
            self._save_config(config)
    
    def _load_config(self) -> Dict:
        """加载配置"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_config(self, config: Dict):
        """保存配置"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def record_decision_feedback(self, decision_id: int, actual_return: float,
                                  expected_return: float, market_context: str = ""):
        """记录决策反馈"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 计算误差
        error = actual_return - expected_return
        
        # 记录反馈
        cursor.execute("""
            INSERT INTO decision_feedback 
            (decision_id, actual_return, expected_return, error, market_context, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (decision_id, actual_return, expected_return, error, market_context, 
              datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def analyze_performance(self, days: int = 30) -> Dict:
        """分析决策绩效"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取最近的决策反馈
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute("""
            SELECT actual_return, expected_return, error
            FROM decision_feedback
            WHERE created_at > ?
        """, (cutoff_date,))
        
        feedbacks = cursor.fetchall()
        conn.close()
        
        if not feedbacks:
            return {"error": "暂无足够数据"}
        
        # 计算统计
        actual_returns = [f[0] for f in feedbacks]
        expected_returns = [f[1] for f in feedbacks]
        errors = [f[2] for f in feedbacks]
        
        winning_trades = sum(1 for r in actual_returns if r > 0)
        total_trades = len(actual_returns)
        
        return {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "win_rate": winning_trades / total_trades if total_trades > 0 else 0,
            "avg_actual_return": sum(actual_returns) / total_trades,
            "avg_expected_return": sum(expected_returns) / total_trades,
            "avg_error": sum(errors) / total_trades,
            "error_std": (sum(e**2 for e in errors) / total_trades) ** 0.5,
            "best_trade": max(actual_returns),
            "worst_trade": min(actual_returns)
        }
    
    def generate_adjustment_rules(self) -> List[Dict]:
        """生成调整规则"""
        config = self._load_config()
        performance = self.analyze_performance(days=30)
        
        if "error" in performance:
            return []
        
        rules = []
        
        # 规则 1: 胜率过低时降低仓位
        if performance['win_rate'] < config['performance_threshold']:
            rules.append({
                "condition": f"胜率 < {config['performance_threshold']*100:.0f}%",
                "action": "降低建议仓位 10-20%",
                "priority": "高",
                "created_at": datetime.now().isoformat()
            })
        
        # 规则 2: 平均误差过大时调整预期
        if abs(performance['avg_error']) > 0.05:  # 5%
            direction = "调低" if performance['avg_error'] < 0 else "调高"
            rules.append({
                "condition": f"平均误差 > 5%",
                "action": f"{direction}预期收益率 {abs(performance['avg_error'])*100:.1f}%",
                "priority": "中",
                "created_at": datetime.now().isoformat()
            })
        
        # 规则 3: 误差标准差过大时增加风控
        if performance['error_std'] > 0.1:  # 10%
            rules.append({
                "condition": "收益波动过大",
                "action": "收紧止损至 5%，降低单股上限至 15%",
                "priority": "高",
                "created_at": datetime.now().isoformat()
            })
        
        # 保存规则
        config['adjustment_rules'] = rules
        config['last_updated'] = datetime.now().isoformat()
        config['last_performance'] = performance
        self._save_config(config)
        
        return rules
    
    def get_learning_insights(self) -> List[str]:
        """获取学习洞察"""
        config = self._load_config()
        insights = []
        
        if 'last_performance' not in config:
            return ["暂无足够数据进行学习"]
        
        perf = config['last_performance']
        
        # 洞察 1: 胜率分析
        if perf['win_rate'] > 0.6:
            insights.append(f"✅ 胜率优秀 ({perf['win_rate']*100:.1f}%)，当前策略有效")
        elif perf['win_rate'] > 0.45:
            insights.append(f"⚠️ 胜率一般 ({perf['win_rate']*100:.1f}%)，需微调")
        else:
            insights.append(f"❌ 胜率偏低 ({perf['win_rate']*100:.1f}%)，建议重新评估策略")
        
        # 洞察 2: 预期准确性
        error_ratio = abs(perf['avg_error']) / abs(perf['avg_expected_return']) if perf['avg_expected_return'] != 0 else 0
        if error_ratio < 0.2:
            insights.append(f"✅ 预期准确 (误差{error_ratio*100:.1f}%)")
        elif error_ratio < 0.5:
            insights.append(f"⚠️ 预期偏差较大 (误差{error_ratio*100:.1f}%)")
        else:
            insights.append(f"❌ 预期严重偏离 (误差{error_ratio*100:.1f}%)")
        
        # 洞察 3: 风险提示
        if perf['error_std'] > 0.1:
            insights.append(f"⚠️ 收益波动大，建议加强风控")
        
        if perf['worst_trade'] < -0.1:
            insights.append(f"⚠️ 存在大额亏损 ({perf['worst_trade']*100:.1f}%)，检查止损执行")
        
        return insights
    
    def auto_adjust_prompts(self) -> Dict:
        """自动调整提示词"""
        config = self._load_config()
        adjustments = {}
        
        if 'last_performance' not in config:
            return {"status": "no_data"}
        
        perf = config['last_performance']
        
        # 根据胜率调整风险偏好
        if perf['win_rate'] < 0.45:
            adjustments['risk_tolerance'] = 'conservative'
            adjustments['position_suggestion'] = '降低 10-20%'
        elif perf['win_rate'] > 0.6:
            adjustments['risk_tolerance'] = 'moderate'
            adjustments['position_suggestion'] = '维持当前'
        
        # 根据误差调整预期
        if perf['avg_error'] < -0.05:
            adjustments['expected_return_modifier'] = -0.05
        elif perf['avg_error'] > 0.05:
            adjustments['expected_return_modifier'] = 0.05
        
        config['prompt_adjustments'] = adjustments
        config['last_adjustment'] = datetime.now().isoformat()
        self._save_config(config)
        
        return {
            "status": "adjusted",
            "adjustments": adjustments
        }
    
    def run_learning_cycle(self) -> Dict:
        """运行完整学习周期"""
        print("运行学习周期...")
        
        # 1. 分析绩效
        print("  1. 分析绩效...")
        performance = self.analyze_performance(days=30)
        
        if "error" in performance:
            return {"status": "no_data", "message": "暂无足够数据"}
        
        # 2. 生成调整规则
        print("  2. 生成调整规则...")
        rules = self.generate_adjustment_rules()
        
        # 3. 获取洞察
        print("  3. 获取学习洞察...")
        insights = self.get_learning_insights()
        
        # 4. 自动调整
        print("  4. 自动调整提示词...")
        adjustments = self.auto_adjust_prompts()
        
        return {
            "status": "completed",
            "performance": performance,
            "rules": rules,
            "insights": insights,
            "adjustments": adjustments
        }


# 初始化数据库表
def init_feedback_table(db_path: str = None):
    """初始化反馈表"""
    if db_path is None:
        db_path = Path(__file__).parent.parent / "storage" / "agent_memory.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS decision_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            decision_id INTEGER,
            actual_return REAL NOT NULL,
            expected_return REAL NOT NULL,
            error REAL NOT NULL,
            market_context TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


if __name__ == "__main__":
    print("测试自主学习系统...\n")
    
    # 初始化
    init_feedback_table()
    learner = AutonomousLearner()
    
    # 模拟反馈数据
    print("记录模拟反馈数据...")
    import random
    for i in range(20):
        decision_id = i + 1
        expected = random.uniform(0.02, 0.08)
        actual = expected + random.uniform(-0.05, 0.05)
        learner.record_decision_feedback(
            decision_id=decision_id,
            actual_return=actual,
            expected_return=expected,
            market_context="震荡市"
        )
    print(f"  已记录 20 条反馈\n")
    
    # 运行学习周期
    print("运行学习周期...\n")
    result = learner.run_learning_cycle()
    
    print("\n=== 学习结果 ===")
    if result['status'] == 'completed':
        perf = result['performance']
        print(f"胜率：{perf['win_rate']*100:.1f}%")
        print(f"平均收益：{perf['avg_actual_return']*100:.2f}%")
        print(f"平均误差：{perf['avg_error']*100:.2f}%")
        
        print(f"\n调整规则 ({len(result['rules'])}条):")
        for rule in result['rules']:
            print(f"  - {rule['condition']} → {rule['action']}")
        
        print(f"\n学习洞察:")
        for insight in result['insights']:
            print(f"  {insight}")
