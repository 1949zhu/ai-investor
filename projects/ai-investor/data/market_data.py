"""
获取真实市场数据
"""

import sqlite3
from pathlib import Path
from datetime import datetime


def get_latest_market_data(db_path: str = None):
    """获取最新市场数据"""
    if db_path is None:
        db_path = Path(__file__).parent.parent / "storage" / "ashare.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取最新交易日
    cursor.execute("SELECT MAX(trade_date) FROM daily_quotes")
    latest_date = cursor.fetchone()[0]
    
    # 获取上证指数近 5 日数据
    cursor.execute("""
        SELECT trade_date, open, high, low, close, volume
        FROM daily_quotes 
        WHERE symbol = '000001.SH'
        ORDER BY trade_date DESC 
        LIMIT 5
    """)
    index_data = cursor.fetchall()
    
    # 获取市场统计数据
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT symbol) as stock_count,
            AVG(close) as avg_price,
            COUNT(*) as total_records
        FROM daily_quotes 
        WHERE trade_date = ?
    """, (latest_date,))
    stats = cursor.fetchone()
    
    # 获取涨跌分布
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN pct_chg > 0 THEN 1 ELSE 0 END) as up,
            SUM(CASE WHEN pct_chg < 0 THEN 1 ELSE 0 END) as down,
            SUM(CASE WHEN ABS(pct_chg) < 0.01 THEN 1 ELSE 0 END) as flat
        FROM daily_quotes 
        WHERE trade_date = ?
    """, (latest_date,))
    distribution = cursor.fetchone()
    
    conn.close()
    
    return {
        "latest_date": latest_date,
        "stock_count": stats[0] if stats else 0,
        "avg_price": stats[1] if stats else 0,
        "index_5days": list(reversed(index_data)),  # 按时间正序
        "up_count": distribution[0] if distribution else 0,
        "down_count": distribution[1] if distribution else 0,
        "flat_count": distribution[2] if distribution else 0,
        "current_date": datetime.now().strftime("%Y-%m-%d")
    }


if __name__ == "__main__":
    data = get_latest_market_data()
    print(f"最新交易日：{data['latest_date']}")
    print(f"当前日期：{data['current_date']}")
    print(f"股票数量：{data['stock_count']}")
    print(f"涨跌分布：涨{data['up_count']} 跌{data['down_count']} 平{data['flat_count']}")
    print(f"\n上证指数近 5 日:")
    for row in data['index_5days']:
        print(f"  {row[0]}: 开{row[1]:.2f} 收{row[4]:.2f} 量{row[5]:.0f}")
