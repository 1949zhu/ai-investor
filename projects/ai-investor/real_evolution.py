# -*- coding: utf-8 -*-
"""
真实数据进化模式

使用真实免费 API：
- 新浪财经新闻
- 东方财富龙虎榜
- 新浪财经财务数据
"""

import os
import sys
sys.path.insert(0, '.')

from pathlib import Path
from datetime import datetime
from data.real_news_fetcher import RealNewsFetcher
from data.real_lhb_fetcher import RealLHBFetcher
from autonomous.problem_solver import AutonomousProblemSolver


class RealEvolution:
    """真实数据进化"""
    
    def __init__(self):
        self.news = RealNewsFetcher()
        self.lhb = RealLHBFetcher()
        self.solver = AutonomousProblemSolver()
        self.logs_dir = Path(__file__).parent.parent / "logs" / "evolution"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def run_cycle(self):
        """运行一次进化周期"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_file = self.logs_dir / f"evolution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"进化周期：{timestamp}\n")
            f.write("="*60 + "\n\n")
            
            # 1. 龙虎榜
            f.write("【1/3】龙虎榜数据...\n")
            lhb = self.lhb.fetch_today()
            if lhb:
                stats = self.lhb.get_stats(lhb)
                f.write(f"  上榜：{stats['total']} 只\n")
                f.write(f"  净额：{stats['net']/100000000:.2f}亿\n")
                
                top = self.lhb.get_top_buy(lhb, 5)
                f.write(f"  净买入前 5:\n")
                for s in top:
                    f.write(f"    {s['code']} {s['name']} {s['net_amount']/10000:.0f}万\n")
            else:
                f.write("  无数据\n")
            
            # 2. 新闻
            f.write("\n【2/3】市场新闻...\n")
            news = self.news.fetch_all()
            if news:
                sentiment = self.news.get_sentiment(news)
                f.write(f"  共 {len(news)} 条\n")
                f.write(f"  利好：{sentiment['positive']} 条\n")
                f.write(f"  利空：{sentiment['negative']} 条\n")
            else:
                f.write("  抓取失败\n")
            
            # 3. 自主进化
            f.write("\n【3/3】自主进化...\n")
            result = self.solver.autonomous_self_improvement()
            f.write(f"  状态：{result.get('status', 'unknown')}\n")
            
            f.write("\n" + "="*60 + "\n")
            f.write(f"完成：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print(f"✅ 进化完成 - {log_file.name}")
    
    def run_once(self):
        """运行一次"""
        self.run_cycle()


if __name__ == "__main__":
    evolution = RealEvolution()
    evolution.run_once()
