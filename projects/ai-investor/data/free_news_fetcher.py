# -*- coding: utf-8 -*-
"""
免费新闻数据抓取 - 无需 API Key

数据源：
1. 东方财富网
2. 新浪财经
3. 财联社
"""

import requests
from datetime import datetime
from bs4 import BeautifulSoup
import json
from pathlib import Path


class FreeNewsFetcher:
    """免费新闻抓取器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.cache_dir = Path(__file__).parent.parent / "cache" / "news"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_eastmoney(self, limit=20):
        """东方财富网 - 滚动新闻"""
        try:
            url = "http://api.eastmoney.com/news/getGlobalNewsList"
            params = {
                'pageindex': 1,
                'pagesize': limit,
                'sortcode': 'UpdateTime',
                'order': 'desc'
            }
            
            r = requests.get(url, params=params, headers=self.headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                news_list = []
                for item in data.get('Data', [])[:limit]:
                    news_list.append({
                        'title': item.get('Title', ''),
                        'content': item.get('Content', ''),
                        'source': '东方财富',
                        'time': item.get('UpdateTime', ''),
                        'url': item.get('Url', '')
                    })
                return news_list
        except Exception as e:
            print(f"东方财富抓取失败：{e}")
        
        return []
    
    def fetch_sina(self, limit=20):
        """新浪财经 - 财经新闻"""
        try:
            url = "https://feed.mix.sina.com.cn/api/roll/get"
            params = {
                'pageid': '100',
                'lid': '2404',
                'num': limit,
                'page': '1'
            }
            
            r = requests.get(url, params=params, headers=self.headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                news_list = []
                for item in data.get('data', {}).get('list', [])[:limit]:
                    news_list.append({
                        'title': item.get('title', ''),
                        'content': item.get('description', ''),
                        'source': '新浪财经',
                        'time': item.get('ctime', ''),
                        'url': item.get('url', '')
                    })
                return news_list
        except Exception as e:
            print(f"新浪财经抓取失败：{e}")
        
        return []
    
    def fetch_cailian(self, limit=20):
        """财联社 - 电报"""
        try:
            url = "https://www.cls.cn/v1/roll/get_roll_list"
            params = {
                'app': 'CailianPress',
                'category': 'telegraph',
                'last_time': int(datetime.now().timestamp())
            }
            
            r = requests.get(url, params=params, headers=self.headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                news_list = []
                for item in data.get('data', {}).get('roll_data', [])[:limit]:
                    news_list.append({
                        'title': item.get('title', ''),
                        'content': item.get('brief', ''),
                        'source': '财联社',
                        'time': item.get('ctime', ''),
                        'url': f"https://www.cls.cn/detail/{item.get('id', '')}"
                    })
                return news_list
        except Exception as e:
            print(f"财联社抓取失败：{e}")
        
        return []
    
    def fetch_all(self, limit_per_source=10):
        """抓取所有来源"""
        print("📰 抓取免费新闻...")
        
        all_news = []
        
        # 东方财富
        print("  - 东方财富网...")
        eastmoney = self.fetch_eastmoney(limit_per_source)
        all_news.extend(eastmoney)
        print(f"    ✓ {len(eastmoney)} 条")
        
        # 新浪财经
        print("  - 新浪财经...")
        sina = self.fetch_sina(limit_per_source)
        all_news.extend(sina)
        print(f"    ✓ {len(sina)} 条")
        
        # 财联社
        print("  - 财联社...")
        cailian = self.fetch_cailian(limit_per_source)
        all_news.extend(cailian)
        print(f"    ✓ {len(cailian)} 条")
        
        # 保存缓存
        self._save_cache(all_news)
        
        print(f"\n✅ 共抓取 {len(all_news)} 条新闻")
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
    
    def get_sentiment_keywords(self, news_list):
        """简单情感分析（基于关键词）"""
        positive = ['上涨', '利好', '增长', '突破', '创新高', '业绩', '盈利', '分红']
        negative = ['下跌', '利空', '下滑', '亏损', '暴跌', '风险', '监管', '处罚']
        
        sentiment = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for news in news_list:
            title = news.get('title', '') + news.get('content', '')
            
            pos_count = sum(1 for word in positive if word in title)
            neg_count = sum(1 for word in negative if word in title)
            
            if pos_count > neg_count:
                sentiment['positive'] += 1
            elif neg_count > pos_count:
                sentiment['negative'] += 1
            else:
                sentiment['neutral'] += 1
        
        return sentiment


if __name__ == "__main__":
    fetcher = FreeNewsFetcher()
    news = fetcher.fetch_all()
    
    if news:
        print(f"\n最新 5 条:")
        for n in news[:5]:
            print(f"  [{n['source']}] {n['title'][:40]}")
        
        sentiment = fetcher.get_sentiment_keywords(news)
        print(f"\n情感分析:")
        print(f"  利好：{sentiment['positive']} 条")
        print(f"  利空：{sentiment['negative']} 条")
        print(f"  中性：{sentiment['neutral']} 条")
