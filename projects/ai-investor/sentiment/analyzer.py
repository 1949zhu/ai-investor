"""
市场情绪分析器

使用 AI 分析市场情绪，辅助投资决策

数据源：
- 财经新闻（新浪/东方财富/同花顺）
- 社交媒体
- 市场评论
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_service import get_llm_service
from llm_service.config import LLMConfig
from news.fetcher import FinancialNewsFetcher


class SentimentAnalyzer:
    """
    市场情绪分析器
    
    分析：
    - 财经新闻情绪（实时获取）
    - 社交媒体情绪
    - 市场整体 sentiment
    """
    
    def __init__(self, llm_service=None, news_fetcher=None):
        if llm_service:
            self.llm = llm_service
        else:
            config = LLMConfig.get_service_config()
            self.llm = get_llm_service(**config)
        
        self.news_fetcher = news_fetcher or FinancialNewsFetcher()
        
        self.storage = Path(__file__).parent.parent / "storage" / "sentiment_history"
        self.storage.mkdir(parents=True, exist_ok=True)
    
    def analyze_realtime_news_sentiment(self, limit: int = 30) -> Dict:
        """
        分析实时新闻情绪
        
        Args:
            limit: 获取新闻数量
            
        Returns:
            情绪分析结果（包含状态信息）
        """
        print("  📰 获取实时财经新闻...")
        
        # 获取实时新闻
        news_list = self.news_fetcher.fetch_all_news(limit_per_source=limit//3)
        
        if not news_list:
            # 返回错误状态，不降级
            return {
                'status': 'error',
                'error': '无法获取实时新闻',
                'error_details': '所有新闻数据源获取失败',
                'overall_sentiment': None,
                'sentiment_label': None,
                'confidence': None,
                'hot_topics': [],
                'risk_alerts': [],
                'summary': '新闻 API 不可用，无法进行情绪分析',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'realtime_news'
            }
        
        # 提取标题
        headlines = [news.get('title', '') for news in news_list[:limit]]
        
        print(f"  📊 分析 {len(headlines)} 条新闻标题...")
        
        # 使用 LLM 分析情绪
        result = self.analyze_news_sentiment(headlines)
        
        # 检查 LLM 是否失败
        if result.get('status') == 'error':
            return result
        
        result['source'] = 'realtime_news'
        result['news_count'] = len(news_list)
        result['news_sources'] = list(set(n.get('source', '') for n in news_list))
        result['status'] = 'success'
        
        # 保存结果
        self._save_result(result)
        
        return result
    
    def analyze_news_sentiment(self, news_headlines: List[str]) -> Dict:
        """
        分析新闻情绪
        
        Args:
            news_headlines: 新闻标题列表
            
        Returns:
            情绪分析结果
        """
        prompt = f"""请分析以下财经新闻标题的市场情绪。

【新闻标题】
{json.dumps(news_headlines, ensure_ascii=False, indent=2)}

请分析：
1. 整体市场情绪（乐观/悲观/中性）
2. 情绪分数（-1 到 1，越正越乐观）
3. 热点话题及情绪
4. 潜在风险点

输出 JSON 格式：
{{
    "overall_sentiment": 0.5,
    "sentiment_label": "谨慎乐观",
    "confidence": 0.8,
    "hot_topics": [
        {{"topic": "话题", "sentiment": 0.6, "mentions": 10}}
    ],
    "risk_alerts": ["风险 1", "风险 2"],
    "summary": "情绪分析总结"
}}"""
        
        print("🧠 LLM 正在分析新闻情绪...")
        result = self.llm.generate_json(prompt)
        
        result['date'] = datetime.now().strftime('%Y-%m-%d')
        result['source'] = 'news'
        
        # 保存结果
        self._save_result(result)
        
        return result
    
    def analyze_market_commentary(self, commentary: str) -> Dict:
        """
        分析市场评论
        
        Args:
            commentary: 市场评论文本
            
        Returns:
            情绪分析结果
        """
        prompt = f"""请分析以下市场评论的情绪和观点。

【市场评论】
{commentary[:2000]}  （截取前 2000 字）

请分析：
1. 作者对市场的态度（乐观/悲观/中性）
2. 情绪强度（1-10 分）
3. 主要观点摘要
4. 投资建议倾向

输出 JSON 格式：
{{
    "sentiment": 0.6,
    "sentiment_label": "乐观",
    "intensity": 7,
    "key_points": ["观点 1", "观点 2"],
    "recommendation": "买入/持有/卖出",
    "confidence": 0.8
}}"""
        
        print("🧠 LLM 正在分析市场评论...")
        result = self.llm.generate_json(prompt)
        
        result['date'] = datetime.now().strftime('%Y-%m-%d')
        result['source'] = 'commentary'
        
        return result
    
    def analyze_social_sentiment(self, social_posts: List[Dict]) -> Dict:
        """
        分析社交媒体情绪
        
        Args:
            social_posts: 社交媒体帖子列表
            格式：[{"text": "...", "likes": 100, "comments": 50}]
            
        Returns:
            情绪分析结果
        """
        # 提取文本
        texts = [post.get('text', '') for post in social_posts[:20]]  # 限制数量
        
        prompt = f"""请分析以下社交媒体帖子反映的市场情绪。

【社交媒体帖子】
{json.dumps(texts, ensure_ascii=False, indent=2)}

请分析：
1. 散户情绪（贪婪/恐惧/中性）
2. 热点股票/板块提及
3. 情绪趋势
4. 是否有极端情绪（过度贪婪或恐惧）

输出 JSON 格式：
{{
    "retail_sentiment": 0.4,
    "sentiment_label": "谨慎",
    "fear_greed_index": 45,
    "hot_stocks": ["股票 1", "股票 2"],
    "hot_sectors": ["板块 1", "板块 2"],
    "extreme_warning": false,
    "summary": "分析总结"
}}"""
        
        print("🧠 LLM 正在分析社交媒体情绪...")
        result = self.llm.generate_json(prompt)
        
        result['date'] = datetime.now().strftime('%Y-%m-%d')
        result['source'] = 'social'
        
        return result
    
    def get_sentiment_signal(self, sentiment_data: Dict) -> Dict:
        """
        将情绪数据转换为交易信号
        
        Args:
            sentiment_data: 情绪分析结果
            
        Returns:
            交易信号建议
        """
        prompt = f"""请根据以下情绪分析结果，生成交易信号建议。

【情绪数据】
{json.dumps(sentiment_data, ensure_ascii=False, indent=2)}

请给出：
1. 当前情绪处于什么区间？（极度悲观/悲观/中性/乐观/极度乐观）
2. 对应的仓位建议
3. 是否需要反向操作？（极度情绪时反向）
4. 具体操作建议

输出 JSON 格式：
{{
    "sentiment_zone": "中性",
    "position_suggestion": 0.5,
    "contrarian_signal": false,
    "action": "持有/加仓/减仓",
    "reasoning": "理由说明",
    "confidence": 0.7
}}"""
        
        print("🧠 LLM 正在生成情绪信号...")
        return self.llm.generate_json(prompt)
    
    def combine_sentiment_sources(self, sources: List[Dict]) -> Dict:
        """
        综合多个情绪源
        
        Args:
            sources: 多个情绪分析结果
            
        Returns:
            综合情绪指标
        """
        prompt = f"""请综合以下多个情绪源，生成统一的市场情绪指标。

【情绪源数据】
{json.dumps(sources, ensure_ascii=False, indent=2)}

请综合判断：
1. 整体市场情绪分数（-1 到 1）
2. 情绪标签
3. 各源的一致性如何？
4. 是否有分歧？如何解读？
5. 最终建议

输出 JSON 格式：
{{
    "composite_sentiment": 0.5,
    "sentiment_label": "谨慎乐观",
    "consensus": true,
    "divergence_notes": "",
    "confidence": 0.8,
    "recommendation": "建议",
    "summary": "综合分析"
}}"""
        
        print("🧠 LLM 正在综合情绪指标...")
        result = self.llm.generate_json(prompt)
        
        result['date'] = datetime.now().strftime('%Y-%m-%d')
        
        return result
    
    def _save_result(self, result: Dict):
        """保存情绪分析结果"""
        date_str = result.get('date', datetime.now().strftime('%Y-%m-%d'))
        file_path = self.storage / f"sentiment_{date_str}.json"
        
        # 如果文件存在，追加到列表
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                data.append(result)
            else:
                data = [data, result]
        else:
            data = [result]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_historical_sentiment(self, days: int = 7) -> List[Dict]:
        """获取历史情绪数据"""
        results = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            file_path = self.storage / f"sentiment_{date}.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        results.extend(data)
                    else:
                        results.append(data)
        return results


if __name__ == "__main__":
    # 测试情绪分析
    print("=" * 60)
    print("情绪分析器测试")
    print("=" * 60)
    
    analyzer = SentimentAnalyzer()
    
    # 模拟新闻标题
    news_headlines = [
        "央行降准 0.25 个百分点，释放长期资金约 1 万亿元",
        "A 股三大指数集体高开，券商股领涨",
        "美联储暗示暂停加息，全球市场反弹",
        "某科技巨头财报超预期，股价大涨 10%",
        "房地产市场政策放松，多城取消限购"
    ]
    
    print("\n分析新闻情绪...\n")
    result = analyzer.analyze_news_sentiment(news_headlines)
    
    print("\n" + "=" * 60)
    print("情绪分析结果:")
    print("=" * 60)
    print(f"整体情绪：{result.get('sentiment_label', 'N/A')}")
    print(f"情绪分数：{result.get('overall_sentiment', 0):.2f}")
    print(f"置信度：{result.get('confidence', 0):.2f}")
    print(f"热点话题：{result.get('hot_topics', [])}")
    print(f"风险提醒：{result.get('risk_alerts', [])}")
