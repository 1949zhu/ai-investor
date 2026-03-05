"""
自主智能体 - 总控脚本

整合：
1. 自主进化引擎（评估和改进系统）
2. 自主问题解决引擎（发现问题并尝试解决）
3. 自主调度器（定时运行）

这才是真正的自主 AI Agent！
"""

import os
import sys
sys.path.insert(0, '.')

os.environ['DASHSCOPE_API_KEY'] = 'sk-fb6aa9235b6b4627aa2ac5f7295db04c'

from datetime import datetime
from pathlib import Path

from autonomous.evolution_engine import SelfEvolutionEngine
from autonomous.problem_solver import AutonomousProblemSolver


class AutonomousAgent:
    """自主智能体总控"""
    
    def __init__(self):
        self.evolution_engine = SelfEvolutionEngine()
        self.problem_solver = AutonomousProblemSolver()
        self.report_dir = Path(__file__).parent.parent / "reports" / "autonomous"
        self.report_dir.mkdir(parents=True, exist_ok=True)
    
    def full_autonomous_cycle(self) -> dict:
        """
        完整自主周期
        
        1. 自主进化检查（系统状态评估）
        2. 自主问题分析（发现并尝试解决问题）
        3. 生成综合报告
        4. 必要时通知用户
        """
        print("="*70)
        print("        🤖 自主智能体 - 完整周期")
        print("="*70)
        print(f"启动时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = {}
        
        # 步骤 1: 自主进化检查
        print("\n" + "="*70)
        print("【阶段 1/3】自主进化检查")
        print("="*70)
        
        try:
            evolution_result = self.evolution_engine.autonomous_run()
            results['evolution'] = evolution_result
            print("\n✅ 自主进化检查完成")
        except Exception as e:
            print(f"\n❌ 自主进化检查失败：{e}")
            results['evolution'] = {'error': str(e)}
        
        # 步骤 2: 自主问题分析
        print("\n" + "="*70)
        print("【阶段 2/3】自主问题分析")
        print("="*70)
        
        try:
            problem_result = self.problem_solver.autonomous_self_improvement()
            results['problem_solving'] = problem_result
            print("\n✅ 自主问题分析完成")
        except Exception as e:
            print(f"\n❌ 自主问题分析失败：{e}")
            results['problem_solving'] = {'error': str(e)}
        
        # 步骤 3: 生成综合报告
        print("\n" + "="*70)
        print("【阶段 3/3】生成综合报告")
        print("="*70)
        
        report = self._generate_comprehensive_report(results)
        report_file = self.report_dir / f"autonomous_cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ 综合报告已保存：{report_file}")
        
        # 检查是否需要通知用户
        should_notify = self._should_notify_user(results)
        if should_notify:
            self._notify_user(report_file, results)
            print(f"\n📬 已生成用户通知")
        
        print("\n" + "="*70)
        print("                    ✅ 完整自主周期完成")
        print("="*70)
        
        return results
    
    def _generate_comprehensive_report(self, results: dict) -> str:
        """生成综合报告"""
        report = f"""# 自主智能体综合报告

**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 自主进化检查

"""
        # 进化检查结果
        evolution = results.get('evolution', {})
        if 'error' in evolution:
            report += f"❌ 执行失败：{evolution['error']}\n"
        else:
            assessment = evolution.get('assessment', {})
            report += f"""### 系统状态

| 指标 | 值 |
|------|------|
| 决策胜率 | {assessment.get('decision_quality', {}).get('win_rate', 0)*100:.1f}% |
| 系统置信度 | {assessment.get('confidence', 0)*100:.1f}% |
| 需要改进 | {'是' if assessment.get('needs_adjustment') else '否'} |

### 自主改进

{json.dumps(evolution.get('improvement', {}), ensure_ascii=False, indent=2)}

### 异常检测

{json.dumps(assessment.get('anomalies', []), ensure_ascii=False, indent=2)}
"""
        
        report += f"""
---

## 🔧 自主问题分析

"""
        # 问题分析结果
        problem = results.get('problem_solving', {})
        if 'error' in problem:
            report += f"❌ 执行失败：{problem['error']}\n"
        else:
            report += f"""### 识别的问题

{len(problem.get('problems', []))} 个问题

"""
            for i, p in enumerate(problem.get('problems', [])[:5], 1):
                report += f"{i}. **{p.get('problem', '未知')}** ({p.get('severity', 'medium')})  \n"
            
            report += f"""
### 能力缺口

{len(problem.get('gaps', []))} 个缺口

"""
            for i, g in enumerate(problem.get('gaps', [])[:5], 1):
                report += f"{i}. **{g.get('capability', '未知')}** ({g.get('priority', 'medium')})  \n"
            
            report += f"""
### 实施的改进

成功：{sum(1 for i in problem.get('implementations', []) if i.get('success'))}
失败：{sum(1 for i in problem.get('implementations', []) if not i.get('success'))}

"""
        
        report += f"""
---

## 📝 总结

自主智能体已完成本次周期检查。

**下一步建议：**
- 查看上述报告了解系统状态
- 如有需要人工介入的事项，请处理
- 系统将继续自主运行

---
*报告由自主智能体自动生成*
"""
        
        return report
    
    def _should_notify_user(self, results: dict) -> bool:
        """判断是否需要通知用户"""
        # 有成功改进时通知
        problem = results.get('problem_solving', {})
        if any(i.get('success') for i in problem.get('implementations', [])):
            return True
        
        # 有严重问题时通知
        evolution = results.get('evolution', {})
        assessment = evolution.get('assessment', {})
        if assessment.get('anomalies'):
            return True
        
        # 置信度过低时通知
        if assessment.get('confidence', 1) < 0.4:
            return True
        
        return False
    
    def _notify_user(self, report_file: Path, results: dict):
        """通知用户"""
        import json
        notification_file = self.report_dir / f"notification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        content = f"🤖 自主智能体通知\n\n"
        content += f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # 检查有改进
        problem = results.get('problem_solving', {})
        successful = [i for i in problem.get('implementations', []) if i.get('success')]
        if successful:
            content += f"✅ 系统自主完成了 {len(successful)} 项改进\n\n"
            for impl in successful:
                content += f"  - {impl.get('problem', '未知')}\n"
        
        # 检查有异常
        evolution = results.get('evolution', {})
        assessment = evolution.get('assessment', {})
        anomalies = assessment.get('anomalies', [])
        if anomalies:
            content += f"\n⚠️  发现 {len(anomalies)} 个异常，需要关注\n\n"
            for a in anomalies:
                content += f"  - {a.get('description', '未知')}\n"
        
        content += f"\n📄 详细报告：{report_file}\n"
        
        with open(notification_file, 'w', encoding='utf-8') as f:
            f.write(content)


# 导入 json
import json


if __name__ == "__main__":
    agent = AutonomousAgent()
    result = agent.full_autonomous_cycle()
    
    print(f"\n📄 报告目录：{agent.report_dir}")
    print(f"\n💡 提示：设置定时任务让系统自主运行")
    print(f"   Windows 任务计划 → 每 4 小时运行一次此脚本")
