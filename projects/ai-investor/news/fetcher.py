"""
财经新闻获取器 - 多数据源稳定版

使用多个稳定数据源获取财经新闻：
1. 百度财经 API
2. 腾讯财经 API  
3. 雪球财经（公开数据）

API 失败时直接报错，不使用模拟数据
"""

import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class FinancialNewsFetcher:
    """
    财经新闻获取器（多数据源稳定版）
    """
    
    def __init__(self, cache_dir: str = None, cache_ttl_hours: int = 1):
        self.cache_dir = Path(cache_dir) if cache_dir else Path(__file__).parent.parent / "storage" / "news_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://finance.baidu.com/'
        }
    
    def fetch_baidu_finance(self, limit: int = 20) -> List[Dict]:
        """
        获取百度财经新闻
        
        使用百度财经 API
        """
        print("  📰 获取百度财经新闻...")
        
        try:
            import requests
            
            url = "https://finance.baidu.com/vapi/general/v1/get_news_list"
            params = {
                'pn': 0,
                'rn': limit,
                'type': 'general',
                'from': 'pc',
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                news_list = []
                
                # 解析百度财经响应
                result = data.get('Result', {})
                items = result.get('list', [])
                
                for item in items:
                    title = item.get('title', '')
                    if title:
                        news_list.append({
                            'title': title,
                            'url': item.get('url', ''),
                            'source': '百度财经',
                            'publish_time': item.get('ctime', datetime.now().isoformat()),
                            'content': item.get('abstract', ''),
                            'category': 'finance'
                        })
                
                if news_list:
                    self._save_to_cache('baidu', news_list)
                    print(f"    ✅ 获取 {len(news_list)} 条新闻")
                    return news_list
                else:
                    print(f"    ⚠️ 无新闻数据")
                    return []
            else:
                print(f"    ❌ 请求失败：HTTP {response.status_code}")
                return []
                
        except Exception as e:
            print(f"    ❌ 获取失败：{e}")
            return []
    
    def fetch_qq_finance(self, limit: int = 20) -> List[Dict]:
        """
        获取腾讯财经新闻
        
        使用腾讯财经 API
        """
        print("  📰 获取腾讯财经新闻...")
        
        try:
            import requests
            
            # 腾讯财经滚动新闻
            url = "https://r.inews.qq.com/gw/event/hot_ranking_list"
            params = {
                'page_size': limit,
                'page': 1,
                'id': 'finance',
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                news_list = []
                
                # 解析腾讯财经响应
                news_list_raw = data.get('news_list', [])
                
                for item in news_list_raw:
                    title = item.get('title', '')
                    if title:
                        news_list.append({
                            'title': title,
                            'url': f"https://new.qq.com/rain/a/{item.get('id', '')}",
                            'source': '腾讯财经',
                            'publish_time': datetime.fromtimestamp(item.get('timestamp', 0)).isoformat() if item.get('timestamp') else datetime.now().isoformat(),
                            'content': item.get('abstract', ''),
                            'category': 'finance'
                        })
                
                if news_list:
                    self._save_to_cache('qq', news_list)
                    print(f"    ✅ 获取 {len(news_list)} 条新闻")
                    return news_list
                else:
                    print(f"    ⚠️ 无新闻数据")
                    return []
            else:
                print(f"    ❌ 请求失败：HTTP {response.status_code}")
                return []
                
        except Exception as e:
            print(f"    ❌ 获取失败：{e}")
            return []
    
    def fetch_163_finance(self, limit: int = 20) -> List[Dict]:
        """
        获取网易财经新闻
        
        使用网易财经 API
        """
        print("  📰 获取网易财经新闻...")
        
        try:
            import requests
            
            # 网易财经新闻
            url = "https://money.163.com/special/0025808B/news_list.js"
            
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                # 网易返回 JSONP 格式
                text = response.text
                if 'var data=' in text:
                    json_str = text.replace('var data=', '').strip()
                    data = json.loads(json_str)
                    
                    news_list = []
                    items = data.get('data', [])
                    
                    for item in items[:limit]:
                        title = item.get('title', '')
                        if title:
                            news_list.append({
                                'title': title,
                                'url': item.get('docurl', ''),
                                'source': '网易财经',
                                'publish_time': item.get('ptime', datetime.now().isoformat()),
                                'content': item.get('digest', ''),
                                'category': 'finance'
                            })
                    
                    if news_list:
                        self._save_to_cache('163', news_list)
                        print(f"    ✅ 获取 {len(news_list)} 条新闻")
                        return news_list
                
                print(f"    ⚠️ 数据格式异常")
                return []
            else:
                print(f"    ❌ 请求失败：HTTP {response.status_code}")
                return []
                
        except Exception as e:
            print(f"    ❌ 获取失败：{e}")
            return []
    
    def fetch_all_news(self, limit_per_source: int = 15) -> List[Dict]:
        """
        获取所有可用数据源新闻
        
        Args:
            limit_per_source: 每个数据源获取数量
            
        Returns:
            合并的新闻列表
        """
        all_news = []
        failed_sources = []
        
        # 尝试各个数据源
        baidu_news = self.fetch_baidu_finance(limit_per_source)
        if baidu_news:
            all_news.extend(baidu_news)
        else:
            failed_sources.append('百度财经')
        
        qq_news = self.fetch_qq_finance(limit_per_source)
        if qq_news:
            all_news.extend(qq_news)
        else:
            failed_sources.append('腾讯财经')
        
        netease_news = self.fetch_163_finance(limit_per_source)
        if netease_news:
            all_news.extend(netease_news)
        else:
            failed_sources.append('网易财经')
        
        # 去重
        seen = set()
        unique_news = []
        for news in all_news:
            title = news.get('title', '')
            if title and title not in seen:
                seen.add(title)
                unique_news.append(news)
        
        # 按时间排序
        unique_news.sort(key=lambda x: x.get('publish_time', ''), reverse=True)
        
        # 报告状态
        if unique_news:
            print(f"\n  📊 成功获取 {len(unique_news)} 条唯一新闻")
            if failed_sources:
                print(f"  ⚠️ 部分数据源失败：{', '.join(failed_sources)}")
        else:
            print(f"\n  ❌ 所有数据源获取失败：{', '.join(failed_sources)}")
            print(f"  💡 建议：检查网络连接或稍后重试")
        
        return unique_news
    
    def fetch_stock_specific_news(self, symbol: str, limit: int = 10) -> List[Dict]:
        """获取个股相关新闻"""
        print(f"  📰 获取 {symbol} 相关新闻...")
        print(f"    ⚠️ 个股新闻 API 暂未实现")
        return []
    
    def _save_to_cache(self, source: str, news_list: List[Dict]):
        """保存到缓存"""
        cache_file = self.cache_dir / f"{source}_{datetime.now().strftime('%Y%m%d')}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(news_list, f, ensure_ascii=False, indent=2)
    
    def _load_from_cache(self, source: str, max_age_hours: int = 1) -> List[Dict]:
        """从缓存加载"""
        cache_file = self.cache_dir / f"{source}_{datetime.now().strftime('%Y%m%d')}.json"
        if cache_file.exists():
            file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if file_age <= timedelta(hours=max_age_hours):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        return []
    
    def get_status(self) -> Dict:
        """获取数据源状态"""
        return {
            'baidu': '可用' if self._test_source('baidu') else '不可用',
            'qq': '可用' if self._test_source('qq') else '不可用',
            '163': '可用' if self._test_source('163') else '不可用',
        }
    
    def _test_source(self, source: str) -> bool:
        """测试数据源是否可用"""
        try:
            if source == 'baidu':
                news = self.fetch_baidu_finance(limit=1)
                return len(news) > 0
            elif source == 'qq':
                news = self.fetch_qq_finance(limit=1)
                return len(news) > 0
            elif source == '163':
                news = self.fetch_163_finance(limit=1)
                return len(news) > 0
        except:
            pass
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("财经新闻获取器测试（多数据源稳定版）")
    print("=" * 60)
    
    fetcher = FinancialNewsFetcher()
    
    print("\n获取新闻...\n")
    news_list = fetcher.fetch_all_news(limit_per_source=10)
    
    if news_list:
        print("\n" + "=" * 60)
        print("新闻标题列表:")
        print("=" * 60)
        for i, news in enumerate(news_list[:15], 1):
            print(f"{i}. [{news.get('source', 'N/A')}] {news.get('title', 'N/A')}")
            print(f"   时间：{news.get('publish_time', 'N/A')}")
            print()
    else:
        print("\n❌ 无法获取新闻，请检查网络或 API 状态")
