# -*- coding: utf-8 -*-
"""
增强数据分析 - 真实数据驱动

功能：
1. 龙虎榜深度分析
2. 资金流向追踪
3. 热点板块识别
4. 机构动向分析
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

os.environ['DASHSCOPE_API_KEY'] = 'sk-fb6aa9235b6b4627aa2ac5f7295db04c'

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from data.real_lhb_fetcher import RealLHBFetcher
from data.real_news_fetcher import RealNewsFetcher


class EnhancedAnalyzer:
    """增强分析器"""
    
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "storage" / "ashare.db"
        self.lhb_db = Path(__file__).parent.parent / "storage" / "lhb.db"
        self.cache_dir = Path(__file__).parent.parent / "cache" / "analysis"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self._init_lhb_db()
    
    def _init_lhb_db(self):
        """初始化龙虎榜数据库"""
        conn = sqlite3.connect(self.lhb_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lhb_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                code TEXT,
                name TEXT,
                price REAL,
                change REAL,
                buy_amount REAL,
                sell_amount REAL,
                net_amount REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def analyze_lhb_trend(self, days=5):
        """
        分析龙虎榜趋势
        
        days: 分析最近 N 天
        """
        print("📊 龙虎榜趋势分析...")
        
        # 获取今日数据
        fetcher = RealLHBFetcher()
        today_lhb = fetcher.fetch_today()
        
        if not today_lhb:
            print("  ⚠️ 无数据")
            return None
        
        # 保存到数据库
        self._save_lhb_data(today_lhb)
        
        # 分析
        analysis = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total_stocks': len(today_lhb),
            'total_net': sum(s['net_amount'] for s in today_lhb),
            'top_sectors': self._analyze_sectors(today_lhb),
            'institution_activity': self._analyze_institution(today_lhb),
            'hot_stocks': self._get_hot_stocks(today_lhb)
        }
        
        # 保存
        self._save_analysis(analysis)
        
        # 打印
        print(f"  上榜股票：{analysis['total_stocks']} 只")
        print(f"  净买入总额：{analysis['total_net']:.2f}亿")
        
        if analysis['top_sectors']:
            print(f"  热门板块:")
            for sector in analysis['top_sectors'][:3]:
                print(f"    {sector['name']}: {sector['count']}只")
        
        return analysis
    
    def _save_lhb_data(self, lhb_list):
        """保存龙虎榜数据"""
        try:
            conn = sqlite3.connect(self.lhb_db)
            cursor = conn.cursor()
            
            date = datetime.now().strftime('%Y-%m-%d')
            
            for stock in lhb_list:
                cursor.execute("""
                    INSERT INTO lhb_history 
                    (date, code, name, price, change, buy_amount, sell_amount, net_amount)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    date,
                    stock['code'],
                    stock['name'],
                    stock['price'],
                    stock['change'],
                    stock['buy_amount'],
                    stock['sell_amount'],
                    stock['net_amount']
                ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"保存失败：{e}")
    
    def _analyze_sectors(self, lhb_list):
        """分析板块"""
        # 简单按股票代码前缀分组
        sectors = {}
        
        for stock in lhb_list:
            code = stock['code']
            if code.startswith('688'):
                sector = '科创板'
            elif code.startswith('300'):
                sector = '创业板'
            elif code.startswith('002'):
                sector = '中小板'
            else:
                sector = '主板'
            
            if sector not in sectors:
                sectors[sector] = {'name': sector, 'count': 0, 'net': 0}
            
            sectors[sector]['count'] += 1
            sectors[sector]['net'] += stock['net_amount']
        
        return sorted(sectors.values(), key=lambda x: x['count'], reverse=True)
    
    def _analyze_institution(self, lhb_list):
        """分析机构动向"""
        # 净买入超 1 亿的可能是机构
        institution_stocks = [s for s in lhb_list if abs(s['net_amount']) > 1]
        
        return {
            'total': len(institution_stocks),
            'net_buy': sum(s['net_amount'] for s in institution_stocks if s['net_amount'] > 0),
            'net_sell': sum(s['net_amount'] for s in institution_stocks if s['net_amount'] < 0)
        }
    
    def _get_hot_stocks(self, lhb_list, top=10):
        """获取热门股票"""
        sorted_list = sorted(lhb_list, key=lambda x: x['net_amount'], reverse=True)
        return sorted_list[:top]
    
    def _save_analysis(self, analysis):
        """保存分析结果"""
        cache_file = self.cache_dir / f"lhb_analysis_{datetime.now().strftime('%Y%m%d')}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    def get_market_sentiment(self):
        """获取市场情绪"""
        print("\n📰 市场情绪分析...")
        
        fetcher = RealNewsFetcher()
        news = fetcher.fetch_all()
        
        if news:
            sentiment = fetcher.get_sentiment(news)
            total = len(news)
            
            positive_ratio = sentiment['positive'] / total * 100 if total else 0
            negative_ratio = sentiment['negative'] / total * 100 if total else 0
            
            result = {
                'total_news': total,
                'positive': sentiment['positive'],
                'negative': sentiment['negative'],
                'neutral': sentiment['neutral'],
                'positive_ratio': round(positive_ratio, 1),
                'negative_ratio': round(negative_ratio, 1),
                'sentiment': '乐观' if positive_ratio > negative_ratio else '悲观'
            }
            
            print(f"  新闻：{total} 条")
            print(f"  情绪：{result['sentiment']} (利好{positive_ratio:.1f}%)")
            
            return result
        
        return None
    
    def generate_daily_report(self):
        """生成每日分析报告"""
        print("\n📄 生成每日报告...")
        
        lhb = self.analyze_lhb_trend()
        sentiment = self.get_market_sentiment()
        
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat(),
            'lhb': lhb,
            'sentiment': sentiment,
            'summary': self._generate_summary(lhb, sentiment)
        }
        
        # 保存
        report_file = self.cache_dir / f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n摘要:\n{report['summary']}")
        
        return report
    
    def _generate_summary(self, lhb, sentiment):
        """生成摘要"""
        summary = []
        
        if lhb:
            summary.append(f"龙虎榜净买入{len(lhb['top_sectors'])}个板块，")
            if lhb['top_sectors']:
                summary.append(f"{lhb['top_sectors'][0]['name']}最热，")
        
        if sentiment:
            summary.append(f"市场情绪{sentiment['sentiment']}，")
            summary.append(f"利好新闻占{sentiment['positive_ratio']}%")
        
        return ''.join(summary) if summary else '数据不足'


if __name__ == "__main__":
    analyzer = EnhancedAnalyzer()
    analyzer.generate_daily_report()
