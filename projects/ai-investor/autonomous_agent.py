# -*- coding: utf-8 -*-
"""
AI 投资智能体 - 完全自主运行模式

功能：
1. 自主获取数据（龙虎榜、新闻、财务）
2. 自主分析市场
3. 自主发现问题
4. 自主搜索解决方案
5. 自主实施改进
6. 自主记录日志

运行间隔：30 分钟
"""

import os
import sys
sys.path.insert(0, '.')

os.environ['DASHSCOPE_API_KEY'] = 'sk-fb6aa9235b6b4627aa2ac5f7295db04c'

import schedule
import time
from datetime import datetime
from pathlib import Path
from data.real_lhb_fetcher import RealLHBFetcher
from data.real_news_fetcher import RealNewsFetcher
from autonomous.problem_solver import AutonomousProblemSolver
from analysis.enhanced_analyzer import EnhancedAnalyzer


class AutonomousAgent:
    """自主智能体"""
    
    def __init__(self):
        self.lhb = RealLHBFetcher()
        self.news = RealNewsFetcher()
        self.solver = AutonomousProblemSolver()
        self.analyzer = EnhancedAnalyzer()
        
        self.logs_dir = Path(__file__).parent / "logs" / "autonomous"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.run_count = 0
    
    def run_cycle(self):
        """运行一个自主周期"""
        self.run_count += 1
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_file = self.logs_dir / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"{'='*60}\n")
            f.write(f"自主运行周期 #{self.run_count}\n")
            f.write(f"时间：{timestamp}\n")
            f.write(f"{'='*60}\n\n")
            
            try:
                # 1. 获取数据
                f.write("【1/5】获取市场数据...\n")
                data_status = self._fetch_data(f)
                
                # 2. 分析市场
                f.write("\n【2/5】市场分析...\n")
                analysis_status = self._analyze_market(f)
                
                # 3. 发现问题
                f.write("\n【3/5】问题发现与分析...\n")
                problem_status = self._discover_problems(f)
                
                # 4. 自主改进
                f.write("\n【4/5】自主改进...\n")
                improvement_status = self._self_improve(f)
                
                # 5. 生成报告
                f.write("\n【5/5】生成报告...\n")
                report_status = self._generate_report(f)
                
                f.write(f"\n{'='*60}\n")
                f.write(f"周期完成\n")
                f.write(f"{'='*60}\n")
                
                print(f"[{timestamp}] 周期 #{self.run_count} 完成 ✓")
                
            except Exception as e:
                f.write(f"\n❌ 错误：{e}\n")
                print(f"[{timestamp}] 周期 #{self.run_count} 失败：{e}")
    
    def _fetch_data(self, f):
        """获取数据"""
        # 龙虎榜
        lhb = self.lhb.fetch_today()
        if lhb:
            f.write(f"  ✓ 龙虎榜：{len(lhb)} 只股票\n")
        else:
            f.write(f"  ⚠ 龙虎榜：无数据 (可能休市)\n")
        
        # 新闻
        news = self.news.fetch_all()
        f.write(f"  {'✓' if news else '⚠'} 新闻：{len(news)} 条\n")
        
        return {'lhb': len(lhb), 'news': len(news)}
    
    def _analyze_market(self, f):
        """市场分析"""
        try:
            analysis = self.analyzer.analyze_lhb_trend()
            if analysis:
                f.write(f"  ✓ 板块分析完成\n")
                f.write(f"  ✓ 机构动向分析完成\n")
            return {'status': 'success'}
        except Exception as e:
            f.write(f"  ⚠ 分析失败：{e}\n")
            return {'status': 'failed', 'error': str(e)}
    
    def _discover_problems(self, f):
        """发现问题"""
        try:
            # 简单问题发现逻辑
            problems = []
            
            # 检查数据获取
            if not self.news.fetch_all():
                problems.append("新闻数据获取失败")
            
            f.write(f"  ✓ 发现 {len(problems)} 个问题\n")
            for p in problems:
                f.write(f"    - {p}\n")
            
            return {'problems': problems}
        except Exception as e:
            f.write(f"  ⚠ 问题发现失败：{e}\n")
            return {'problems': [], 'error': str(e)}
    
    def _self_improve(self, f):
        """自主改进"""
        try:
            result = self.solver.autonomous_self_improvement()
            f.write(f"  ✓ 改进引擎运行完成\n")
            return result
        except Exception as e:
            f.write(f"  ⚠ 改进失败：{e}\n")
            return {'status': 'failed', 'error': str(e)}
    
    def _generate_report(self, f):
        """生成报告"""
        try:
            report = self.analyzer.generate_daily_report()
            f.write(f"  ✓ 每日报告已生成\n")
            return report
        except Exception as e:
            f.write(f"  ⚠ 报告生成失败：{e}\n")
            return None
    
    def start(self, interval_minutes=30):
        """启动自主运行"""
        print("="*60)
        print("        AI 投资智能体 - 自主运行模式")
        print("="*60)
        print(f"启动时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"运行间隔：{interval_minutes} 分钟")
        print(f"日志目录：{self.logs_dir}")
        print("\n按 Ctrl+C 停止\n")
        
        # 立即运行一次
        self.run_cycle()
        
        # 定时运行
        schedule.every(interval_minutes).minutes.do(self.run_cycle)
        
        while True:
            schedule.run_pending()
            time.sleep(60)


if __name__ == "__main__":
    agent = AutonomousAgent()
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
            print(f"自定义间隔：{interval} 分钟")
        except:
            interval = 30
    else:
        interval = 30
    
    agent.start(interval)
