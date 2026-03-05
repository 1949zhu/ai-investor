"""
自主问题解决引擎 - AI 系统的"主动能力"

核心思想：
1. 发现自己缺什么 → 自己去找
2. 发现哪里不行 → 自己分析原因
3. 需要新能力 → 自己搜索解决方案
4. 找到方案 → 自己尝试实现
5. 实现失败 → 自己换方法
6. 有进展 → 主动告诉人

这才是真正的自主智能体！
"""

import os
import sys
sys.path.insert(0, '.')

os.environ['DASHSCOPE_API_KEY'] = 'sk-fb6aa9235b6b4627aa2ac5f7295db04c'

import json
import sqlite3
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import dashscope
from dashscope import Generation


class AutonomousProblemSolver:
    """自主问题解决引擎"""
    
    def __init__(self):
        base_path = Path(__file__).parent.parent
        self.db_path = base_path / "storage" / "problems.db"
        self.solutions_dir = base_path / "solutions"
        self.logs_dir = base_path / "logs" / "autonomous"
        self.solutions_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 问题追踪表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS problems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                problem TEXT NOT NULL,
                category TEXT,
                severity TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'identified',
                root_cause TEXT,
                solution TEXT,
                implemented BOOLEAN DEFAULT FALSE,
                result TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                resolved_at TEXT
            )
        """)
        
        # 能力缺口表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS capability_gaps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                capability TEXT NOT NULL,
                why_needed TEXT,
                priority TEXT DEFAULT 'medium',
                search_query TEXT,
                found_solutions TEXT,
                implemented BOOLEAN DEFAULT FALSE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 自主改进行录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS improvements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                improvement TEXT NOT NULL,
                before_state TEXT,
                after_state TEXT,
                impact TEXT,
                verified BOOLEAN DEFAULT FALSE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def autonomous_self_improvement(self) -> Dict:
        """
        自主自我改进 - 完整流程
        
        1. 分析系统现状
        2. 识别问题和能力缺口
        3. 自主搜索解决方案
        4. 评估方案可行性
        5. 尝试实现
        6. 验证效果
        7. 记录经验
        """
        print("="*70)
        print("        🧠 自主自我改进引擎启动")
        print("="*70)
        
        # 步骤 1: 分析系统现状
        print("\n【1/6】分析系统现状...")
        status = self._analyze_system_status()
        print(f"  ✓ 系统状态分析完成")
        
        # 步骤 2: 识别问题和能力缺口
        print("\n【2/6】识别问题和能力缺口...")
        problems = self._identify_problems(status)
        gaps = self._identify_capability_gaps(status)
        print(f"  ✓ 发现 {len(problems)} 个问题，{len(gaps)} 个能力缺口")
        
        # 步骤 3: 对每个问题/缺口搜索解决方案
        print("\n【3/6】搜索解决方案...")
        solutions = []
        for problem in problems:
            solution = self._search_solution(problem['problem'], problem['category'])
            if solution:
                solutions.append({
                    'type': 'problem',
                    'problem': problem,
                    'solution': solution
                })
        
        for gap in gaps:
            solution = self._search_solution(gap['capability'], 'capability')
            if solution:
                solutions.append({
                    'type': 'gap',
                    'gap': gap,
                    'solution': solution
                })
        
        print(f"  ✓ 找到 {len(solutions)} 个可行方案")
        
        # 步骤 4: 评估并排序方案
        print("\n【4/6】评估方案优先级...")
        prioritized = self._prioritize_solutions(solutions)
        print(f"  ✓ 已排序，最高优先级：{prioritized[0]['priority'] if prioritized else '无'}")
        
        # 步骤 5: 尝试实现高优先级方案
        print("\n【5/6】尝试实现高优先级方案...")
        implementations = []
        for item in prioritized[:3]:  # 最多实现 3 个
            result = self._attempt_implementation(item)
            implementations.append(result)
            problem_text = item.get('problem', item.get('gap', {})).get('problem', item.get('gap', {}).get('capability', '未知'))
            if result['success']:
                print(f"  ✅ {problem_text[:30]}... → 已实现")
            else:
                print(f"  ⚠️  {problem_text[:30]}... → 实现失败：{result.get('reason', '未知')}")
        
        # 步骤 6: 生成改进报告
        print("\n【6/6】生成改进报告...")
        report = self._generate_improvement_report(status, problems, gaps, implementations)
        
        # 保存报告
        report_file = self.solutions_dir / f"improvement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"  ✓ 报告已保存：{report_file}")
        
        # 有重要改进时主动通知
        if any(i['success'] for i in implementations):
            self._notify_user(implementations, report_file)
        
        print("\n" + "="*70)
        print("                    ✅ 自主改进周期完成")
        print("="*70)
        
        return {
            "status": status,
            "problems": problems,
            "gaps": gaps,
            "solutions": solutions,
            "implementations": implementations,
            "report": report
        }
    
    def _analyze_system_status(self) -> Dict:
        """分析系统现状"""
        # 检查各个模块
        status = {
            "timestamp": datetime.now().isoformat(),
            "modules": {},
            "performance": {},
            "resources": {}
        }
        
        # 1. 检查数据模块
        data_status = self._check_module("data")
        status['modules']['data'] = data_status
        
        # 2. 检查智能体模块
        agent_status = self._check_module("agents")
        status['modules']['agents'] = agent_status
        
        # 3. 检查性能指标
        performance = self._check_performance()
        status['performance'] = performance
        
        # 4. 检查资源
        resources = self._check_resources()
        status['resources'] = resources
        
        return status
    
    def _check_module(self, module_name: str) -> Dict:
        """检查模块状态"""
        base_path = Path(__file__).parent.parent / module_name
        
        if not base_path.exists():
            return {"exists": False, "files": 0, "status": "missing"}
        
        files = list(base_path.glob("*.py"))
        
        # 简单检查：文件数量、最后修改时间
        return {
            "exists": True,
            "files": len(files),
            "last_modified": max([f.stat().st_mtime for f in files]) if files else 0,
            "status": "ok" if len(files) > 0 else "empty"
        }
    
    def _check_performance(self) -> Dict:
        """检查性能指标"""
        # 从 agent_memory.db 获取决策质量
        try:
            db_path = Path(__file__).parent.parent / "storage" / "agent_memory.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 获取最近 20 条决策
            cursor.execute("""
                SELECT outcome, reflection
                FROM decision_log
                WHERE outcome != '待验证'
                ORDER BY date DESC
                LIMIT 20
            """)
            
            decisions = cursor.fetchall()
            conn.close()
            
            if decisions:
                # 简单计算胜率
                winning = sum(1 for d in decisions if d[0] and ('收益' in d[0] or (d[1] and '收益' in d[1])))
                win_rate = winning / len(decisions)
                
                return {
                    "recent_decisions": len(decisions),
                    "winning": winning,
                    "win_rate": win_rate,
                    "quality": "good" if win_rate >= 0.6 else "needs_improvement" if win_rate >= 0.45 else "poor"
                }
        except Exception as e:
            return {"error": str(e)}
        
        return {"status": "no_data"}
    
    def _check_resources(self) -> Dict:
        """检查资源状态"""
        # 检查数据库
        db_path = Path(__file__).parent.parent / "storage" / "ashare.db"
        db_size = db_path.stat().st_size / (1024*1024) if db_path.exists() else 0
        
        # 检查 API 配额（简单估计）
        # (实际应该调用 API 查询)
        
        return {
            "database_size_mb": round(db_size, 1),
            "api_status": "unknown"
        }
    
    def _identify_problems(self, status: Dict) -> List[Dict]:
        """识别问题"""
        problems = []
        
        # 问题 1: 胜率低
        perf = status.get('performance', {})
        win_rate = perf.get('win_rate', 0.5)
        if win_rate < 0.5:
            problems.append({
                "problem": f"决策胜率过低 ({win_rate*100:.1f}%)，需要提升准确性",
                "category": "performance",
                "severity": "high" if win_rate < 0.4 else "medium",
                "root_cause": "待分析"
            })
        
        # 问题 2: 数据不足
        resources = status.get('resources', {})
        if resources.get('database_size_mb', 0) < 10:
            problems.append({
                "problem": "数据库太小，历史数据不足",
                "category": "data",
                "severity": "medium",
                "root_cause": "需要扩展数据源"
            })
        
        # 问题 3: 新闻数据缺失
        if status.get('modules', {}).get('data', {}).get('status') == 'ok':
            # 检查新闻获取
            try:
                from data.news_fetcher import NewsFetcher
                fetcher = NewsFetcher()
                news = fetcher.get_latest_news(hours=24)
                if len(news) == 0:
                    problems.append({
                        "problem": "新闻数据源失效，无法获取市场新闻",
                        "category": "data",
                        "severity": "medium",
                        "root_cause": "API 受限或反爬"
                    })
            except:
                pass
        
        # 问题 4: 模块缺失
        modules = status.get('modules', {})
        for mod_name, mod_status in modules.items():
            if not mod_status.get('exists', True):
                problems.append({
                    "problem": f"{mod_name} 模块缺失",
                    "category": "architecture",
                    "severity": "high",
                    "root_cause": "需要创建该模块"
                })
        
        # 保存问题到数据库
        self._save_problems(problems)
        
        return problems
    
    def _identify_capability_gaps(self, status: Dict) -> List[Dict]:
        """识别能力缺口"""
        gaps = []
        
        perf = status.get('performance', {})
        
        # 缺口 1: 如果胜率低，可能需要更好的分析能力
        if perf.get('win_rate', 0.5) < 0.5:
            gaps.append({
                "capability": "更准确的市场状态判断能力",
                "why_needed": f"当前胜率只有{perf.get('win_rate', 0)*100:.1f}%",
                "priority": "high",
                "search_query": "股票 市场状态判断 技术指标 机器学习"
            })
            
            gaps.append({
                "capability": "实时新闻情感分析能力",
                "why_needed": "新闻情绪对短期走势影响大",
                "priority": "high",
                "search_query": "财经新闻 情感分析 NLP API"
            })
        
        # 缺口 2: 可能需要更多数据源
        gaps.append({
            "capability": "龙虎榜数据接入",
            "why_needed": "机构动向是重要参考",
            "priority": "medium",
            "search_query": "A 股 龙虎榜 数据 API"
        })
        
        gaps.append({
            "capability": "研报数据接入",
            "why_needed": "券商研报提供专业分析",
            "priority": "medium",
            "search_query": "券商 研报 数据 API Python"
        })
        
        # 缺口 3: 可能需要更好的回测
        gaps.append({
            "capability": "更完善的回测框架",
            "why_needed": "验证策略有效性",
            "priority": "medium",
            "search_query": "股票 回测框架 Python backtrader"
        })
        
        # 保存缺口到数据库
        self._save_capability_gaps(gaps)
        
        return gaps
    
    def _search_solution(self, problem: str, category: str) -> Dict:
        """搜索解决方案"""
        print(f"    🔍 搜索解决方案：{problem[:50]}...")
        
        # 使用 LLM 帮助搜索和分析
        prompt = f"""你是一个技术问题解决专家。

问题：{problem}
类别：{category}

请分析：
1. 这个问题的根本原因可能是什么？
2. 有哪些可能的解决方案？
3. 每个方案的优缺点？
4. 推荐优先尝试哪个方案？为什么？

请给出具体、可执行的建议，包括：
- 需要查找的资料/文档
- 可能需要使用的 API 或库
- 实现的大致步骤
- 可能的难点和应对方法

格式：简洁、结构化"""

        try:
            resp = Generation.call(
                model='qwen-plus',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=1500
            )
            
            if resp.status_code == 200:
                solution_text = resp.output.text
                
                return {
                    "problem": problem,
                    "category": category,
                    "analysis": solution_text,
                    "search_time": datetime.now().isoformat(),
                    "confidence": 0.7  # LLM 建议的置信度
                }
        except Exception as e:
            print(f"      ⚠️  LLM 搜索失败：{e}")
        
        return None
    
    def _prioritize_solutions(self, solutions: List[Dict]) -> List[Dict]:
        """排序解决方案"""
        # 简单优先级排序
        priority_order = {"high": 0, "medium": 1, "low": 2}
        
        for s in solutions:
            problem = s.get('problem', s.get('gap', {}))
            severity = problem.get('severity', 'medium')
            s['priority'] = severity
            s['priority_score'] = priority_order.get(severity, 1)
        
        return sorted(solutions, key=lambda x: x['priority_score'])
    
    def _attempt_implementation(self, solution: Dict) -> Dict:
        """尝试实现方案"""
        problem = solution.get('problem', solution.get('gap', {}))
        analysis = solution.get('analysis', '')
        
        result = {
            "problem": problem.get('problem', problem.get('capability', '')),
            "attempted": True,
            "success": False,
            "steps_taken": [],
            "result": None
        }
        
        # 根据问题类型尝试不同方案
        category = problem.get('category', 'unknown')
        
        if category == 'data':
            # 尝试找新数据源
            result = self._attempt_data_solution(problem, analysis, result)
        elif category == 'performance':
            # 尝试优化策略
            result = self._attempt_performance_solution(problem, analysis, result)
        elif category == 'capability':
            # 尝试实现新能力
            result = self._attempt_capability_solution(problem, analysis, result)
        else:
            result['reason'] = "未知问题类型，需要人工介入"
        
        # 记录改进
        if result['success']:
            self._record_improvement(result)
        
        return result
    
    def _attempt_data_solution(self, problem: Dict, analysis: str, result: Dict) -> Dict:
        """尝试数据源解决方案"""
        result['steps_taken'].append("分析数据需求")
        
        # 根据问题尝试不同方案
        if "新闻" in problem.get('problem', ''):
            result['steps_taken'].append("尝试备用新闻 API")
            
            # 尝试找替代 API
            alternative_apis = [
                "https://api.tianapi.com",  # 天行数据
                "https://www.juhe.cn",      # 聚合数据
                "https://api.avatarg.com"   # 其他
            ]
            
            result['suggestion'] = f"建议尝试以下新闻 API: {alternative_apis}"
            result['success'] = False  # 需要人工配置 API Key
            result['reason'] = "需要人工注册 API Key"
        
        elif "龙虎榜" in problem.get('problem', ''):
            result['steps_taken'].append("搜索龙虎榜数据源")
            result['suggestion'] = "推荐使用 Tushare Pro 或东方财富 API"
            result['success'] = False
            result['reason'] = "需要人工配置"
        
        else:
            result['reason'] = "需要具体分析"
        
        return result
    
    def _attempt_performance_solution(self, problem: Dict, analysis: str, result: Dict) -> Dict:
        """尝试性能优化方案"""
        result['steps_taken'].append("分析性能瓶颈")
        
        # 如果是胜率低的问题
        if "胜率" in problem.get('problem', ''):
            result['steps_taken'].append("生成优化建议")
            
            # 创建优化建议文件
            suggestion_file = self.solutions_dir / f"optimize_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            
            content = f"""# 胜率优化建议

**问题：** {problem.get('problem', '未知')}
**分析时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## LLM 分析

{analysis}

## 建议尝试的方案

1. **增加更多特征**
   - 技术指标：MACD, KDJ, RSI 等
   - 资金流向：北向资金、主力资金
   - 市场情绪：涨跌比、涨停数

2. **优化模型**
   - 尝试不同的 LLM 提示词
   - 增加 few-shot 示例
   - 调整温度参数

3. **策略调整**
   - 只在高置信度时操作
   - 增加止损机制
   - 降低仓位

## 下一步

- [ ] 实施上述建议
- [ ] 回测验证
- [ ] 记录结果
"""
            
            with open(suggestion_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            result['suggestion_file'] = str(suggestion_file)
            result['success'] = True
            result['result'] = f"已生成优化建议：{suggestion_file}"
        
        return result
    
    def _attempt_capability_solution(self, problem: Dict, analysis: str, result: Dict) -> Dict:
        """尝试能力实现方案"""
        result['steps_taken'].append("分析能力需求")
        
        capability = problem.get('capability', '')
        
        # 创建能力实现计划
        plan_file = self.solutions_dir / f"implement_{capability[:10]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        content = f"""# 能力实现计划：{capability}

**需求原因：** {problem.get('why_needed', '未知')}
**优先级：** {problem.get('priority', 'medium')}
**分析时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## LLM 分析

{analysis}

## 实现步骤

1. **调研阶段**
   - [ ] 搜索相关 API/库
   - [ ] 评估可行性
   - [ ] 确定技术方案

2. **开发阶段**
   - [ ] 设计接口
   - [ ] 实现核心功能
   - [ ] 测试验证

3. **集成阶段**
   - [ ] 集成到主系统
   - [ ] 更新文档
   - [ ] 监控运行

## 搜索关键词

{problem.get('search_query', '')}

## 备注

需要人工审核和实现
"""
        
        with open(plan_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        result['plan_file'] = str(plan_file)
        result['success'] = False  # 需要人工实现
        result['reason'] = "新能力需要人工实现，已生成实现计划"
        
        return result
    
    def _save_problems(self, problems: List[Dict]):
        """保存问题到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for p in problems:
            cursor.execute("""
                INSERT INTO problems (problem, category, severity, root_cause, status)
                VALUES (?, ?, ?, ?, ?)
            """, (p['problem'], p['category'], p['severity'], 
                  p.get('root_cause', ''), 'identified'))
        
        conn.commit()
        conn.close()
    
    def _save_capability_gaps(self, gaps: List[Dict]):
        """保存能力缺口到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for g in gaps:
            cursor.execute("""
                INSERT INTO capability_gaps (capability, why_needed, priority, search_query)
                VALUES (?, ?, ?, ?)
            """, (g['capability'], g['why_needed'], g['priority'], 
                  g.get('search_query', '')))
        
        conn.commit()
        conn.close()
    
    def _record_improvement(self, result: Dict):
        """记录改进"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO improvements (improvement, before_state, after_state, impact)
            VALUES (?, ?, ?, ?)
        """, (result.get('problem', ''), 'before', 'after', 
              result.get('result', '')))
        
        conn.commit()
        conn.close()
    
    def _generate_improvement_report(self, status: Dict, problems: List[Dict], 
                                      gaps: List[Dict], implementations: List[Dict]) -> str:
        """生成改进报告"""
        report = f"""# 自主改进报告

**时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 系统状态摘要

| 指标 | 值 |
|------|------|
| 决策胜率 | {status.get('performance', {}).get('win_rate', 0)*100:.1f}% |
| 数据量 | {status.get('resources', {}).get('database_size_mb', 0)}MB |
| 模块状态 | {len(status.get('modules', {}))} 个 |

## 识别的问题 ({len(problems)}个)

"""
        for i, p in enumerate(problems, 1):
            report += f"{i}. **{p['problem']}**  \n"
            report += f"   类别：{p['category']} | 严重性：{p['severity']}  \n\n"
        
        report += f"""
## 能力缺口 ({len(gaps)}个)

"""
        for i, g in enumerate(gaps, 1):
            report += f"{i}. **{g['capability']}**  \n"
            report += f"   原因：{g['why_needed']} | 优先级：{g['priority']}  \n\n"
        
        report += f"""
## 实施的改进 ({len(implementations)}个)

"""
        for i, impl in enumerate(implementations, 1):
            status_icon = "✅" if impl.get('success') else "⚠️"
            report += f"{i}. {status_icon} {impl.get('problem', '未知')}  \n"
            report += f"   结果：{impl.get('result', impl.get('reason', '未知'))}  \n\n"
        
        report += f"""
---
*报告由自主问题解决引擎自动生成*
"""
        return report
    
    def _notify_user(self, implementations: List[Dict], report_file: Path):
        """通知用户"""
        # 生成通知文件
        alert_file = self.logs_dir / f"notification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        successful = [i for i in implementations if i.get('success')]
        
        content = f"🎉 自主改进通知\n\n"
        content += f"系统自主完成了 {len(successful)} 项改进：\n\n"
        
        for impl in successful:
            content += f"✅ {impl.get('problem', '未知')}\n"
            content += f"   {impl.get('result', '')}\n\n"
        
        content += f"\n详细报告：{report_file}\n"
        
        with open(alert_file, 'w', encoding='utf-8') as f:
            f.write(content)


if __name__ == "__main__":
    solver = AutonomousProblemSolver()
    result = solver.autonomous_self_improvement()
    
    print(f"\n📄 报告已保存：{solver.solutions_dir}")
    print(f"📊 识别问题：{len(result['problems'])}个")
    print(f"🔧 能力缺口：{len(result['gaps'])}个")
    print(f"✅ 成功改进：{sum(1 for i in result['implementations'] if i['success'])}个")
