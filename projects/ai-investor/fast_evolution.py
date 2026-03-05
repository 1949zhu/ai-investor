# -*- coding: utf-8 -*-
"""
快速进化模式 - 每 30 分钟自主进化一次

免费方案：
- LLM 生成市场分析
- LLM 生成虚拟新闻
- LLM 生成龙虎榜分析
- AI 自主决策
"""

import os
import sys
sys.path.insert(0, '.')

os.environ['DASHSCOPE_API_KEY'] = 'sk-fb6aa9235b6b4627aa2ac5f7295db04c'

from datetime import datetime, timedelta
import schedule
import time
from pathlib import Path
from data.llm_market_analyzer import LLMMarketAnalyzer
from autonomous.problem_solver import AutonomousProblemSolver


class FastEvolution:
    """快速进化模式"""
    
    def __init__(self):
        self.analyzer = LLMMarketAnalyzer()
        self.solver = AutonomousProblemSolver()
        self.logs_dir = Path(__file__).parent.parent / "logs" / "evolution"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def run_evolution_cycle(self):
        """运行一次进化周期"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_file = self.logs_dir / f"evolution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"进化周期开始：{timestamp}\n")
            f.write("="*60 + "\n\n")
            
            # 1. 市场分析
            f.write("【1/3】市场分析...\n")
            analysis = self.analyzer.generate_daily_analysis()
            if analysis:
                f.write(f"{analysis[:200]}...\n\n")
            
            # 2. 新闻生成
            f.write("【2/3】生成市场新闻...\n")
            news = self.analyzer.generate_fake_news({})
            for n in news:
                f.write(f"  • {n}\n")
            f.write("\n")
            
            # 3. 自主进化
            f.write("【3/3】自主进化...\n")
            result = self.solver.autonomous_self_improvement()
            f.write(f"状态：{result.get('status', 'unknown')}\n")
            
            f.write("\n" + "="*60 + "\n")
            f.write(f"进化周期完成：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print(f"✅ 进化周期完成 - 日志：{log_file.name}")
    
    def start_scheduler(self, interval_minutes=30):
        """启动定时进化"""
        print("="*60)
        print("        快速进化模式启动")
        print("="*60)
        print(f"进化间隔：{interval_minutes} 分钟")
        print(f"首次运行：立即")
        print("\n按 Ctrl+C 停止\n")
        
        # 立即运行一次
        self.run_evolution_cycle()
        
        # 定时运行
        schedule.every(interval_minutes).minutes.do(self.run_evolution_cycle)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    def run_once(self):
        """只运行一次"""
        self.run_evolution_cycle()


if __name__ == "__main__":
    evolution = FastEvolution()
    
    if len(sys.argv) > 1 and sys.argv[1] == 'once':
        # 只运行一次
        evolution.run_once()
    else:
        # 持续运行（30 分钟间隔）
        evolution.start_scheduler(30)
