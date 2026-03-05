"""
新闻数据获取 - 多渠道财经新闻
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path


class NewsFetcher:
    """财经新闻获取器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
        }
        self.cache_dir = Path(__file__).parent.parent / "cache" / "news"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_sina_news(self, limit: int = 20) -> List[Dict]:
        """新浪财经新闻"""
        try:
            # 新浪财经滚动新闻 API
            url = "https://feed.mix.sina.com.cn/api/roll/get"
            params = {
                'pageid': '100',
                'lid': '2420',  # 财经新闻
                'k': '',
                'num': limit,
                'page': '1',
                'r': '0.1'
            }
            
            resp = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get('result') and data['result'].get('data'):
                    news_list = []
                    for item in data['result']['data'][:limit]:
                        news_list.append({
                            'source': 'sina',
                            'title': item.get('title', ''),
                            'url': item.get('url', ''),
                            'time': item.get('ctime', ''),
                            'intro': item.get('intro', '')[:200]
                        })
                    return news_list
        except Exception as e:
            print(f"新浪财经获取失败：{e}")
        
        return []
    
    def fetch_eastmoney_news(self, limit: int = 20) -> List[Dict]:
        """东方财富新闻"""
        try:
            url = "https://api.eastmoney.com/v1/news/list"
            params = {
                'filter': '0',
                'pageindex': '1',
                'pagesize': limit,
                'sort': '1',
                'type': '1'
            }
            
            resp = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get('Data'):
                    news_list = []
                    for item in data['Data'][:limit]:
                        news_list.append({
                            'source': 'eastmoney',
                            'title': item.get('Title', ''),
                            'url': f"https://news.eastmoney.com/news/{item.get('ID', '')}.html",
                            'time': item.get('ShowTime', ''),
                            'intro': item.get('Brief', '')[:200]
                        })
                    return news_list
        except Exception as e:
            print(f"东方财富获取失败：{e}")
        
        return []
    
    def fetch_caixin_news(self, limit: int = 20) -> List[Dict]:
        """财新网新闻"""
        try:
            url = "https://api.caixin.com/api/content/list"
            params = {
                'columnid': '0',
                'num': limit,
                'page': '1'
            }
            
            resp = requests.get(url, params=params, headers=self.headers, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get('data') and data['data'].get('list'):
                    news_list = []
                    for item in data['data']['list'][:limit]:
                        news_list.append({
                            'source': 'caixin',
                            'title': item.get('title', ''),
                            'url': item.get('content_url', ''),
                            'time': item.get('update_time', ''),
                            'intro': item.get('summary', '')[:200]
                        })
                    return news_list
        except Exception as e:
            print(f"财新网获取失败：{e}")
        
        return []
    
    def fetch_all_news(self, limit_per_source: int = 10) -> List[Dict]:
        """获取所有来源的新闻"""
        all_news = []
        
        # 新浪财经
        sina_news = self.fetch_sina_news(limit_per_source)
        all_news.extend(sina_news)
        print(f"  新浪财经：{len(sina_news)} 条")
        
        # 东方财富
        em_news = self.fetch_eastmoney_news(limit_per_source)
        all_news.extend(em_news)
        print(f"  东方财富：{len(em_news)} 条")
        
        # 财新网
        caixin_news = self.fetch_caixin_news(limit_per_source)
        all_news.extend(caixin_news)
        print(f"  财新网：{len(caixin_news)} 条")
        
        # 按时间排序
        all_news.sort(key=lambda x: x.get('time', ''), reverse=True)
        
        # 缓存
        self._save_cache(all_news)
        
        return all_news
    
    def _save_cache(self, news: List[Dict]):
        """保存新闻缓存"""
        cache_file = self.cache_dir / f"news_{datetime.now().strftime('%Y%m%d_%H')}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({
                'fetched_at': datetime.now().isoformat(),
                'count': len(news),
                'news': news
            }, f, ensure_ascii=False, indent=2)
    
    def get_latest_news(self, hours: int = 24) -> List[Dict]:
        """获取指定时间内的新闻"""
        # 先尝试从缓存加载
        cache_files = sorted(self.cache_dir.glob("news_*.json"), reverse=True)
        
        if cache_files:
            try:
                with open(cache_files[0], 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    fetched_at = datetime.fromisoformat(data['fetched_at'])
                    if datetime.now() - fetched_at < timedelta(hours=hours):
                        return data['news']
            except:
                pass
        
        # 缓存过期或不存在，重新获取
        return self.fetch_all_news()
    
    def analyze_sentiment(self, news_list: List[Dict]) -> Dict:
        """简单分析新闻情绪（基于关键词）"""
        positive_words = ['上涨', '利好', '增长', '突破', '创新高', '复苏', '回暖', '强势']
        negative_words = ['下跌', '利空', '下滑', '暴跌', '创新低', '风险', '衰退', '疲软']
        
        positive_count = 0
        negative_count = 0
        
        for news in news_list:
            title = news.get('title', '') + ' ' + news.get('intro', '')
            for word in positive_words:
                if word in title:
                    positive_count += 1
                    break
            for word in negative_words:
                if word in title:
                    negative_count += 1
                    break
        
        total = positive_count + negative_count
        if total == 0:
            sentiment = '中性'
            score = 50
        else:
            score = positive_count / total * 100
            if score > 60:
                sentiment = '乐观'
            elif score > 40:
                sentiment = '中性'
            else:
                sentiment = '悲观'
        
        return {
            'total_news': len(news_list),
            'positive': positive_count,
            'negative': negative_count,
            'neutral': len(news_list) - positive_count - negative_count,
            'sentiment': sentiment,
            'score': score
        }


if __name__ == "__main__":
    print("测试新闻获取...")
    
    fetcher = NewsFetcher()
    
    # 获取新闻
    print("\n获取最新新闻...")
    news = fetcher.get_latest_news(hours=24)
    print(f"共获取 {len(news)} 条新闻\n")
    
    # 显示前 10 条
    print("最新新闻:")
    for i, n in enumerate(news[:10], 1):
        print(f"  {i}. [{n['source']}] {n['title'][:50]}...")
        print(f"     时间：{n['time']}")
        print(f"     链接：{n['url'][:60]}...")
    
    # 情绪分析
    print("\n情绪分析:")
    sentiment = fetcher.analyze_sentiment(news)
    for k, v in sentiment.items():
        print(f"  {k}: {v}")
