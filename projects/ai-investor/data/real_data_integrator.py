# -*- coding: utf-8 -*-
"""
真实数据源集成

完全使用真实免费 API，无虚拟数据
"""

import os
import sys
sys.path.insert(0, '.')

from pathlib import Path
from datetime import datetime
from data.real_news_fetcher import RealNewsFetcher
from data.real_lhb_fetcher import RealLHBFetcher
from data.real_financial_fetcher import RealFinancialFetcher


class RealDataIntegrator:
    """真实数据集成器"""
    
    def __init__(self):
        self.news = RealNewsFetcher()
        self.lhb = RealLHBFetcher()
        self.financial = RealFinancialFetcher()
    
    def fetch_all(self):
        """获取所有真实数据"""
        print("="*60)
        print("        真实数据源集成")
        print("="*60)
        
        results = {}
        
        # 1. 新闻
        print("\n【1/3】新闻数据...")
        news_list = self.news.fetch_all()
        results['news'] = len(news_list)
        
        if news_list:
            sentiment = self.news.get_sentiment(news_list)
            print(f"  利好：{sentiment['positive']} 条")
            print(f"  利空：{sentiment['negative']} 条")
        
        # 2. 龙虎榜
        print("\n【2/3】龙虎榜...")
        lhb_list = self.lhb.fetch_today()
        results['lhb'] = len(lhb_list)
        
        if lhb_list:
            stats = self.lhb.get_stats(lhb_list)
            print(f"  上榜股票：{stats['total']} 只")
            print(f"  净买入：{stats['net']/100000000:.2f}亿")
            
            top_buy = self.lhb.get_top_buy(lhb_list, 3)
            if top_buy:
                print(f"  净买入前 3:")
                for stock in top_buy:
                    print(f"    {stock['code']} {stock['name']} {stock['net_amount']/10000:.1f}万")
        else:
            print(f"  ⚠️ 今日无数据（可能休市）")
        
        # 3. 财务数据示例
        print("\n【3/3】财务数据示例...")
        market_data = self.financial.get_market_data('sh600519')
        if market_data:
            print(f"  贵州茅台：¥{market_data['current']}")
            results['financial'] = 'success'
        else:
            results['financial'] = 'failed'
        
        print("\n" + "="*60)
        print("        ✅ 真实数据获取完成")
        print("="*60)
        
        return results


if __name__ == "__main__":
    integrator = RealDataIntegrator()
    integrator.fetch_all()
