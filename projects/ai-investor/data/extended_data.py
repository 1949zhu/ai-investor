"""
扩展市场数据 - 资金流、北向数据、市场情绪
"""

import sqlite3
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class ExtendedMarketData:
    """扩展市场数据获取"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "storage" / "ashare.db"
        self.db_path = db_path
    
    def get_market_sentiment(self) -> Dict:
        """获取市场情绪指标"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取最新交易日
        cursor.execute("SELECT MAX(trade_date) FROM daily_quotes")
        latest_date = cursor.fetchone()[0]
        
        if not latest_date:
            conn.close()
            return {}
        
        # 涨跌分布
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN pct_chg > 0 THEN 1 ELSE 0 END) as up,
                SUM(CASE WHEN pct_chg < 0 THEN 1 ELSE 0 END) as down,
                SUM(CASE WHEN ABS(pct_chg) < 0.01 THEN 1 ELSE 0 END) as flat,
                COUNT(*) as total
            FROM daily_quotes 
            WHERE trade_date = ?
        """, (latest_date,))
        dist = cursor.fetchone()
        
        # 涨跌幅分布
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN pct_chg > 0.09 THEN 1 ELSE 0 END) as limit_up,
                SUM(CASE WHEN pct_chg < -0.09 THEN 1 ELSE 0 END) as limit_down,
                SUM(CASE WHEN pct_chg > 0.05 THEN 1 ELSE 0 END) as up_5,
                SUM(CASE WHEN pct_chg < -0.05 THEN 1 ELSE 0 END) as down_5,
                AVG(pct_chg) as avg_change,
                SUM(volume) as total_volume,
                SUM(amount) as total_amount
            FROM daily_quotes 
            WHERE trade_date = ?
        """, (latest_date,))
        stats = cursor.fetchone()
        
        conn.close()
        
        # 计算情绪指标
        total = dist[3] if dist[3] else 1
        up_ratio = (dist[0] or 0) / total
        limit_up_ratio = ((stats[0] or 0) / total) if total else 0
        
        # 情绪得分 (0-100)
        sentiment_score = (
            up_ratio * 40 +  # 上涨占比
            limit_up_ratio * 30 +  # 涨停占比
            (1 - ((stats[5] or 0) / 1e12)) * 10  # 成交量因子（简化）
        )
        sentiment_score = min(100, max(0, sentiment_score * 100))
        
        return {
            "trade_date": latest_date,
            "up_count": dist[0] or 0,
            "down_count": dist[1] or 0,
            "flat_count": dist[2] or 0,
            "total_count": total,
            "limit_up": stats[0] or 0,
            "limit_down": stats[1] or 0,
            "up_5pct": stats[2] or 0,
            "down_5pct": stats[3] or 0,
            "avg_change": (stats[4] or 0) * 100,  # 转为百分比
            "total_volume": stats[5] or 0,
            "total_amount": stats[6] or 0,
            "up_ratio": up_ratio,
            "sentiment_score": sentiment_score,
            "sentiment_label": self._label_sentiment(sentiment_score)
        }
    
    def _label_sentiment(self, score: float) -> str:
        """情绪标签"""
        if score >= 80:
            return "极度乐观"
        elif score >= 60:
            return "乐观"
        elif score >= 40:
            return "中性"
        elif score >= 20:
            return "悲观"
        else:
            return "极度悲观"
    
    def get_index_data(self, index_code: str = "000001.SH", days: int = 20) -> List[Dict]:
        """获取指数数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT trade_date, open, high, low, close, volume, amount, pct_chg
            FROM daily_quotes 
            WHERE symbol = ?
            ORDER BY trade_date DESC
            LIMIT ?
        """, (index_code, days))
        
        data = [
            {
                "date": r[0],
                "open": r[1],
                "high": r[2],
                "low": r[3],
                "close": r[4],
                "volume": r[5],
                "amount": r[6],
                "change_pct": r[7]
            }
            for r in cursor.fetchall()
        ]
        
        conn.close()
        return list(reversed(data))  # 正序
    
    def get_sector_performance(self, top_n: int = 10) -> List[Dict]:
        """获取行业表现（简化版，基于股票代码前缀）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取最新交易日
        cursor.execute("SELECT MAX(trade_date) FROM daily_quotes")
        latest_date = cursor.fetchone()[0]
        
        # 按行业统计（简化：按股票代码分组）
        cursor.execute("""
            SELECT 
                SUBSTR(symbol, 0, 4) as sector,
                COUNT(*) as stock_count,
                AVG(pct_chg) * 100 as avg_change,
                SUM(CASE WHEN pct_chg > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as up_ratio
            FROM daily_quotes 
            WHERE trade_date = ?
            GROUP BY SUBSTR(symbol, 0, 4)
            ORDER BY avg_change DESC
            LIMIT ?
        """, (latest_date, top_n))
        
        sectors = [
            {
                "sector_code": r[0],
                "stock_count": r[1],
                "avg_change": r[2],
                "up_ratio": r[3]
            }
            for r in cursor.fetchall()
        ]
        
        conn.close()
        return sectors
    
    def get_top_stocks(self, by: str = "change", top_n: int = 10) -> List[Dict]:
        """获取涨跌幅榜"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取最新交易日
        cursor.execute("SELECT MAX(trade_date) FROM daily_quotes")
        latest_date = cursor.fetchone()[0]
        
        if by == "change":
            order = "pct_chg DESC"
        elif by == "volume":
            order = "volume DESC"
        elif by == "amount":
            order = "amount DESC"
        else:
            order = "pct_chg DESC"
        
        cursor.execute(f"""
            SELECT symbol, trade_date, close, pct_chg * 100, volume, amount
            FROM daily_quotes 
            WHERE trade_date = ?
            ORDER BY {order}
            LIMIT ?
        """, (latest_date, top_n))
        
        stocks = [
            {
                "symbol": r[0],
                "date": r[1],
                "close": r[2],
                "change_pct": r[3],
                "volume": r[4],
                "amount": r[5]
            }
            for r in cursor.fetchall()
        ]
        
        conn.close()
        return stocks
    
    def get_market_summary(self) -> Dict:
        """获取市场摘要"""
        sentiment = self.get_market_sentiment()
        
        # 上证指数数据
        index_data = self.get_index_data("000001.SH", days=5)
        
        # 涨跌榜
        top_gainers = self.get_top_stocks("change", top_n=5)
        top_losers = self.get_top_stocks("change", top_n=5)
        # 反向取跌幅榜
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(trade_date) FROM daily_quotes")
        latest_date = cursor.fetchone()[0]
        cursor.execute(f"""
            SELECT symbol, close, pct_chg * 100
            FROM daily_quotes 
            WHERE trade_date = '{latest_date}'
            ORDER BY pct_chg ASC
            LIMIT 5
        """)
        top_losers = [
            {"symbol": r[0], "close": r[1], "change_pct": r[2]}
            for r in cursor.fetchall()
        ]
        conn.close()
        
        return {
            "trade_date": sentiment.get("trade_date"),
            "sentiment": {
                "score": sentiment.get("sentiment_score"),
                "label": sentiment.get("sentiment_label"),
                "up_ratio": sentiment.get("up_ratio")
            },
            "market_breadth": {
                "up": sentiment.get("up_count"),
                "down": sentiment.get("down_count"),
                "flat": sentiment.get("flat_count"),
                "total": sentiment.get("total_count")
            },
            "index_5days": index_data,
            "top_gainers": top_gainers,
            "top_losers": top_losers
        }


if __name__ == "__main__":
    print("测试扩展市场数据...")
    
    data = ExtendedMarketData()
    
    # 市场情绪
    print("\n=== 市场情绪 ===")
    sentiment = data.get_market_sentiment()
    for k, v in sentiment.items():
        print(f"  {k}: {v}")
    
    # 市场摘要
    print("\n=== 市场摘要 ===")
    summary = data.get_market_summary()
    print(f"  交易日：{summary['trade_date']}")
    print(f"  情绪：{summary['sentiment']['label']} ({summary['sentiment']['score']:.1f})")
    print(f"  涨跌比：{summary['market_breadth']['up']}:{summary['market_breadth']['down']}")
    
    if summary['index_5days']:
        print(f"\n  上证指数 (最新): {summary['index_5days'][-1]['close']:.2f}")
    
    print(f"\n  涨幅榜:")
    for s in summary['top_gainers'][:3]:
        print(f"    {s['symbol']}: {s['change_pct']:.2f}%")
    
    print(f"\n  跌幅榜:")
    for s in summary['top_losers'][:3]:
        print(f"    {s['symbol']}: {s['change_pct']:.2f}%")
