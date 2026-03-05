"""
自主进化引擎 - AI 投资系统的"大脑"

核心思想：
1. 自己定时运行（cron/心跳）
2. 自己评估决策质量
3. 自己发现问题
4. 自己尝试新方法
5. 自己记录什么有效/无效
6. 主动向人汇报重要发现
"""

import os
import sys
sys.path.insert(0, '.')

os.environ['DASHSCOPE_API_KEY'] = 'sk-fb6aa9235b6b4627aa2ac5f7295db04c'

import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import dashscope
from dashscope import Generation


class SelfEvolutionEngine:
    """自主进化引擎"""
    
    def __init__(self):
        base_path = Path(__file__).parent.parent
        self.db_path = base_path / "storage" / "evolution.db"
        self.config_path = base_path / "config" / "evolution.json"
        self.report_dir = base_path / "reports" / "evolution"
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_db()
        self._init_config()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 假设验证表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hypotheses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hypothesis TEXT NOT NULL,
                category TEXT,
                confidence REAL DEFAULT 0.5,
                test_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                fail_count INTEGER DEFAULT 0,
                last_tested TEXT,
                status TEXT DEFAULT 'testing',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 自主发现表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS discoveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discovery TEXT NOT NULL,
                evidence TEXT,
                confidence REAL,
                impact TEXT,
                verified BOOLEAN DEFAULT FALSE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 策略尝试表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                parameters TEXT,
                result TEXT,
                learned TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _init_config(self):
        """初始化配置"""
        if not self.config_path.exists():
            config = {
                "version": "1.0",
                "autonomous_mode": True,
                "check_interval_hours": 4,
                "auto_adjust_threshold": 0.6,
                "alert_on_discovery": True,
                "last_check": None,
                "active_hypotheses": [],
                "current_strategy": "default"
            }
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
    
    def _load_config(self) -> Dict:
        """加载配置"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_config(self, config: Dict):
        """保存配置"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def self_check(self) -> Dict:
        """自主检查 - 系统自己评估当前状态"""
        print("🔍 自主检查启动...")
        
        # 1. 检查最近决策质量
        quality = self._check_decision_quality()
        
        # 2. 检查当前策略有效性
        strategy_valid = self._check_strategy_effectiveness()
        
        # 3. 检查是否有异常模式
        anomalies = self._detect_anomalies()
        
        # 4. 生成自我评估报告
        assessment = {
            "timestamp": datetime.now().isoformat(),
            "decision_quality": quality,
            "strategy_valid": strategy_valid,
            "anomalies": anomalies,
            "needs_adjustment": quality['win_rate'] < 0.5 or strategy_valid['effective'] == False,
            "confidence": self._calculate_confidence()
        }
        
        # 保存评估
        self._save_assessment(assessment)
        
        return assessment
    
    def _check_decision_quality(self) -> Dict:
        """检查决策质量"""
        conn = sqlite3.connect(str(self.db_path).replace('evolution.db', 'agent_memory.db'))
        cursor = conn.cursor()
        
        # 获取最近的决策
        cursor.execute("""
            SELECT decision, outcome, reflection
            FROM decision_log
            WHERE outcome != '待验证'
            ORDER BY date DESC
            LIMIT 20
        """)
        
        decisions = cursor.fetchall()
        conn.close()
        
        if not decisions:
            return {"status": "no_data", "win_rate": 0.5}
        
        # 简单分析胜率
        winning = 0
        for d in decisions:
            outcome = d[1] or ""
            reflection = d[2] or ""
            if '收益' in outcome or ('收益' in reflection and any(x in reflection for x in ['%', '赚', '盈'])):
                winning += 1
        
        win_rate = winning / len(decisions) if decisions else 0.5
        
        return {
            "status": "analyzed",
            "total_decisions": len(decisions),
            "winning": winning,
            "win_rate": win_rate,
            "quality": "good" if win_rate >= 0.6 else "needs_improvement" if win_rate >= 0.45 else "poor"
        }
    
    def _check_strategy_effectiveness(self) -> Dict:
        """检查策略有效性"""
        # 获取当前策略
        config = self._load_config()
        current_strategy = config.get('current_strategy', 'default')
        
        # 分析该策略的历史表现
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT result, learned
            FROM strategy_experiments
            WHERE strategy_name = ?
            ORDER BY created_at DESC
            LIMIT 10
        """, (current_strategy,))
        
        experiments = cursor.fetchall()
        conn.close()
        
        if not experiments:
            return {"effective": None, "reason": "no_data"}
        
        # 简单判断
        positive = sum(1 for e in experiments if e[1] and ('有效' in e[1] or '成功' in e[1]))
        
        return {
            "effective": positive > len(experiments) * 0.5,
            "tested_count": len(experiments),
            "positive_count": positive
        }
    
    def _detect_anomalies(self) -> List[Dict]:
        """检测异常模式"""
        anomalies = []
        
        # 检查连续失败
        config = self._load_config()
        quality = self._check_decision_quality()
        
        if quality.get('win_rate', 0.5) < 0.3:
            anomalies.append({
                "type": "continuous_failure",
                "severity": "high",
                "description": f"胜率过低 ({quality['win_rate']*100:.1f}%)，需要调整策略",
                "suggestion": "降低仓位，重新评估市场状态判断逻辑"
            })
        
        # 检查市场状态突变
        # (这里可以接入更多检测逻辑)
        
        return anomalies
    
    def _calculate_confidence(self) -> float:
        """计算系统置信度"""
        quality = self._check_decision_quality()
        strategy = self._check_strategy_effectiveness()
        
        confidence = 0.5
        
        # 根据胜率调整
        if quality.get('win_rate', 0.5) >= 0.6:
            confidence += 0.2
        elif quality.get('win_rate', 0.5) >= 0.5:
            confidence += 0.1
        elif quality.get('win_rate', 0.5) < 0.4:
            confidence -= 0.2
        
        # 根据策略有效性调整
        if strategy.get('effective') == True:
            confidence += 0.1
        elif strategy.get('effective') == False:
            confidence -= 0.1
        
        return max(0.1, min(0.95, confidence))
    
    def _save_assessment(self, assessment: Dict):
        """保存评估报告"""
        report_file = self.report_dir / f"assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(assessment, f, ensure_ascii=False, indent=2)
    
    def self_improve(self) -> Dict:
        """自主改进 - 系统自己想办法变得更好"""
        print("🧠 自主改进启动...")
        
        assessment = self.self_check()
        
        if not assessment.get('needs_adjustment'):
            return {"action": "none", "reason": "当前状态良好，无需调整"}
        
        improvements = []
        
        # 1. 如果胜率低，生成新的假设
        if assessment['decision_quality'].get('win_rate', 0.5) < 0.5:
            new_hypothesis = self._generate_hypothesis("low_win_rate")
            self._register_hypothesis(new_hypothesis)
            improvements.append({
                "type": "new_hypothesis",
                "content": new_hypothesis
            })
        
        # 2. 如果策略无效，尝试新策略
        if not assessment['strategy_valid'].get('effective', True):
            new_strategy = self._generate_new_strategy()
            self._register_strategy_experiment(new_strategy)
            improvements.append({
                "type": "new_strategy",
                "content": new_strategy
            })
        
        # 3. 如果有异常，生成应对方案
        for anomaly in assessment.get('anomalies', []):
            response = self._generate_anomaly_response(anomaly)
            improvements.append({
                "type": "anomaly_response",
                "content": response
            })
        
        # 更新配置
        config = self._load_config()
        config['last_improvement'] = datetime.now().isoformat()
        config['improvement_count'] = config.get('improvement_count', 0) + len(improvements)
        self._save_config(config)
        
        return {
            "action": "improved",
            "improvements": improvements,
            "assessment": assessment
        }
    
    def _generate_hypothesis(self, problem_type: str) -> Dict:
        """生成新假设"""
        hypotheses = {
            "low_win_rate": [
                "市场状态判断可能过于简单，需要增加更多维度指标",
                "北向资金流向可能是更好的先行指标",
                "情绪极端值时应该反向操作",
                "当前市场风格可能已切换，需要重新识别"
            ]
        }
        
        import random
        hypothesis_list = hypotheses.get(problem_type, ["需要更多数据来分析问题"])
        
        return {
            "hypothesis": random.choice(hypothesis_list),
            "category": problem_type,
            "confidence": 0.5,
            "test_plan": "在下一次决策中验证"
        }
    
    def _register_hypothesis(self, hypothesis: Dict):
        """注册假设"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO hypotheses (hypothesis, category, confidence, last_tested)
            VALUES (?, ?, ?, ?)
        """, (hypothesis['hypothesis'], hypothesis['category'], 
              hypothesis['confidence'], datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def _generate_new_strategy(self) -> Dict:
        """生成新策略"""
        strategies = [
            {"name": "momentum", "params": {"lookback": 5, "threshold": 0.03}},
            {"name": "mean_reversion", "params": {"lookback": 20, "threshold": 0.05}},
            {"name": "northbound_follow", "params": {"threshold": 50, "lag": 1}},
            {"name": "sentiment_contrarian", "params": {"extreme_low": 20, "extreme_high": 80}}
        ]
        
        import random
        return random.choice(strategies)
    
    def _register_strategy_experiment(self, strategy: Dict):
        """注册策略实验"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO strategy_experiments (strategy_name, parameters, result)
            VALUES (?, ?, ?)
        """, (strategy['name'], json.dumps(strategy['params']), "pending"))
        
        conn.commit()
        conn.close()
    
    def _generate_anomaly_response(self, anomaly: Dict) -> Dict:
        """生成异常应对方案"""
        responses = {
            "continuous_failure": {
                "action": "降低仓位至 20%，暂停新策略，回归基础分析",
                "priority": "high"
            }
        }
        
        return responses.get(anomaly['type'], {
            "action": "继续观察，收集更多数据",
            "priority": "medium"
        })
    
    def autonomous_run(self) -> Dict:
        """自主运行 - 完整周期"""
        print("="*60)
        print("        🤖 AI 投资系统 - 自主进化周期")
        print("="*60)
        
        # 1. 自主检查
        print("\n【1/3】自主检查...")
        assessment = self.self_check()
        
        # 2. 如果需要，自主改进
        print("\n【2/3】评估是否需要改进...")
        if assessment.get('needs_adjustment'):
            print("  → 发现问题，启动改进...")
            improvement = self.self_improve()
        else:
            print("  → 状态良好，持续观察")
            improvement = {"action": "none"}
        
        # 3. 生成自主报告
        print("\n【3/3】生成自主报告...")
        report = self._generate_autonomous_report(assessment, improvement)
        
        # 4. 如果有重要发现，主动通知
        if assessment.get('anomalies'):
            print("\n⚠️  发现异常，需要人工关注！")
            self._send_alert(assessment['anomalies'])
        
        print("\n" + "="*60)
        print("                    ✅ 自主周期完成")
        print("="*60)
        
        return {
            "assessment": assessment,
            "improvement": improvement,
            "report": report
        }
    
    def _generate_autonomous_report(self, assessment: Dict, improvement: Dict) -> str:
        """生成自主报告"""
        report = f"""# 自主进化报告

**时间：** {assessment['timestamp']}

## 系统状态

| 指标 | 值 |
|------|------|
| 决策胜率 | {assessment['decision_quality'].get('win_rate', 0)*100:.1f}% |
| 决策质量 | {assessment['decision_quality'].get('quality', 'unknown')} |
| 策略有效性 | {assessment['strategy_valid'].get('effective', 'unknown')} |
| 系统置信度 | {assessment['confidence']*100:.1f}% |

## 自主改进

{json.dumps(improvement, ensure_ascii=False, indent=2)}

## 异常检测

{json.dumps(assessment.get('anomalies', []), ensure_ascii=False, indent=2)}

---
*报告由自主进化引擎自动生成*
"""
        
        report_file = self.report_dir / f"autonomous_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report
    
    def _send_alert(self, anomalies: List[Dict]):
        """发送警报"""
        alert_file = self.report_dir / f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        content = "⚠️  系统警报\n\n"
        for a in anomalies:
            content += f"类型：{a['type']}\n"
            content += f"严重性：{a['severity']}\n"
            content += f"描述：{a['description']}\n"
            content += f"建议：{a.get('suggestion', '无')}\n\n"
        
        with open(alert_file, 'w', encoding='utf-8') as f:
            f.write(content)


if __name__ == "__main__":
    engine = SelfEvolutionEngine()
    result = engine.autonomous_run()
    
    print(f"\n📊 系统置信度：{result['assessment']['confidence']*100:.1f}%")
    print(f"📄 报告已保存：{engine.report_dir}")
