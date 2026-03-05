# -*- coding: utf-8 -*-
"""
真实新闻数据 - 新浪财经免费 API

无需注册，直接调用
"""

import requests
import json
from datetime import datetime
from pathlib import Path


class RealNewsFetcher:
    """真实新闻抓取器"""
    
    def __init__(self):
        self.cache_dir = Path(__file__).parent.parent / "cache" / "news"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_sina_realtime(self, limit=30):
        """
        新浪财经 - 7x24 小时新闻
        """
        try:
            url = "https://finance.sina.com.cn/7x24"
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'text/html'
            }
            
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                # 简单解析 HTML
                news_list = []
                import re
                matches = re.findall(r'<li class="item.*?>.*?<h3>(.*?)</h3>.*?<span class="date">(.*?)</span>', r.text, re.DOTALL)
                
                for title, time in matches[:limit]:
                    title = re.sub(r'<.*?>', '', title).strip()
                    news_list.append({
                        'title': title,
                        'content': title,
                        'source': '新浪财经',
                        'time': time.strip(),
                        'url': ''
                    })
                
                if news_list:
                    self._save_cache(news_list)
                    return news_list
        except Exception as e:
            print(f"新浪财经失败：{e}")
        
        return []
    
    def fetch_eastmoney_news(self, limit=20):
        """
        东方财富网 - 个股新闻
        """
        try:
            url = "http://api.eastmoney.com/news/getGlobalNewsList"
            params = {
                'pageindex': 1,
                'pagesize': limit
            }
            
            r = requests.get(url, params=params, timeout=10)
            if r.status_code == 200:
                data = r.json()
                news_list = []
                
                for item in data.get('Data', []):
                    news_list.append({
                        'title': item.get('Title', ''),
                        'content': item.get('Content', ''),
                        'source': '东方财富',
                        'time': item.get('UpdateTime', ''),
                        'url': item.get('Url', '')
                    })
                
                return news_list
        except Exception as e:
            print(f"东方财富失败：{e}")
        
        return []
    
    def fetch_cnstock(self, limit=20):
        """
        上海证券报 - 中国证券网
        """
        try:
            url = "http://app.cnstock.com/api/waterfall"
            params = {
                'callback': 'jQuery',
                'colunms': 'xw',
                'page': '1',
                'pagesize': limit
            }
            
            r = requests.get(url, params=params, timeout=10)
            if r.status_code == 200:
                # 处理 JSONP
                text = r.text.replace('jQuery(', '').rstrip(')')
                data = json.loads(text)
                news_list = []
                
                for item in data.get('data', []):
                    news_list.append({
                        'title': item.get('Title', ''),
                        'content': item.get('Intro', ''),
                        'source': '上海证券报',
                        'time': item.get('UpdateTime', ''),
                        'url': item.get('Link', '')
                    })
                
                return news_list
        except Exception as e:
            print(f"上海证券报失败：{e}")
        
        return []
    
    def fetch_all(self):
        """抓取所有来源"""
        print("📰 抓取真实新闻...")
        
        all_news = []
        
        # 新浪财经
        print("  - 新浪财经...")
        sina = self.fetch_sina_realtime(20)
        all_news.extend(sina)
        print(f"    ✓ {len(sina)} 条")
        
        # 东方财富
        print("  - 东方财富...")
        eastmoney = self.fetch_eastmoney_news(15)
        all_news.extend(eastmoney)
        print(f"    ✓ {len(eastmoney)} 条")
        
        # 上海证券报
        print("  - 上海证券报...")
        cnstock = self.fetch_cnstock(15)
        all_news.extend(cnstock)
        print(f"    ✓ {len(cnstock)} 条")
        
        print(f"\n✅ 共抓取 {len(all_news)} 条真实新闻")
        return all_news
    
    def _save_cache(self, news_list):
        """保存缓存"""
        cache_file = self.cache_dir / f"news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'count': len(news_list),
                'news': news_list
            }, f, ensure_ascii=False, indent=2)
    
    def get_sentiment(self, news_list):
        """简单情感分析"""
        positive = ['上涨', '利好', '增长', '突破', '业绩', '盈利']
        negative = ['下跌', '利空', '下滑', '亏损', '风险', '监管']
        
        pos = sum(1 for n in news_list if any(w in n['title'] for w in positive))
        neg = sum(1 for n in news_list if any(w in n['title'] for w in negative))
        
        return {
            'positive': pos,
            'negative': neg,
            'neutral': len(news_list) - pos - neg
        }


if __name__ == "__main__":
    fetcher = RealNewsFetcher()
    news = fetcher.fetch_all()
    
    if news:
        print(f"\n最新 5 条:")
        for n in news[:5]:
            print(f"  [{n['source']}] {n['title'][:40]}")
        
        sentiment = fetcher.get_sentiment(news)
        print(f"\n情感分析:")
        print(f"  利好：{sentiment['positive']} 条")
        print(f"  利空：{sentiment['negative']} 条")
        print(f"  中性：{sentiment['neutral']} 条")
