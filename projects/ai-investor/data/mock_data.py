"""
生成模拟 A 股数据（用于测试和演示）
当无法获取真实数据时使用
"""

import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta
from pathlib import Path


def generate_mock_stock_data(symbol: str, name: str, base_price: float, days: int = 365):
    """生成模拟股票数据"""
    random.seed(hash(symbol) % 2**32)  # 可重复的随机性
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    data = []
    price = base_price
    
    current_date = start_date
    while current_date <= end_date:
        # 跳过周末
        if current_date.weekday() < 5:
            # 随机波动 -3% 到 +3%
            change_pct = random.uniform(-0.03, 0.03)
            price = price * (1 + change_pct)
            
            # 确保价格在合理范围
            price = max(1.0, min(price, base_price * 3))
            
            open_price = price * (1 + random.uniform(-0.01, 0.01))
            high_price = max(open_price, price) * (1 + random.uniform(0, 0.02))
            low_price = min(open_price, price) * (1 - random.uniform(0, 0.02))
            volume = random.randint(1000000, 100000000)
            amount = volume * price
            amplitude = (high_price - low_price) / low_price * 100
            pct_chg = change_pct * 100
            change = price - open_price
            turnover = random.uniform(0.5, 10.0)
            
            data.append({
                'symbol': symbol,
                'trade_date': current_date.strftime('%Y%m%d'),
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(price, 2),
                'volume': volume,
                'amount': amount,
                'amplitude': round(amplitude, 2),
                'pct_chg': round(pct_chg, 2),
                'change': round(change, 2),
                'turnover': round(turnover, 2)
            })
        
        current_date += timedelta(days=1)
    
    return pd.DataFrame(data)


def populate_mock_database(db_path: str = "storage/ashare.db"):
    """填充模拟数据到数据库"""
    db_path = Path(db_path)
    
    # 定义一些真实股票的基本信息
    stocks = [
        ("000001", "平安银行", 12.5),
        ("000002", "万科 A", 8.2),
        ("600000", "浦发银行", 9.8),
        ("600036", "招商银行", 35.6),
        ("000651", "格力电器", 42.3),
    ]
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for symbol, name, base_price in stocks:
        print(f"生成 {symbol} - {name} 的模拟数据...")
        
        # 生成数据
        df = generate_mock_stock_data(symbol, name, base_price)
        
        # 插入数据库
        for _, row in df.iterrows():
            cursor.execute('''
                INSERT OR REPLACE INTO daily_quotes 
                (symbol, trade_date, open, high, low, close, volume, amount, 
                 amplitude, pct_chg, change, turnover)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['symbol'], row['trade_date'], row['open'], row['high'],
                row['low'], row['close'], row['volume'], row['amount'],
                row['amplitude'], row['pct_chg'], row['change'], row['turnover']
            ))
        
        # 保存股票信息
        cursor.execute('''
            INSERT OR REPLACE INTO stock_info 
            (symbol, name, list_date, delist_date, status, exchange, board, industry, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (symbol, name, "20000101", "", "上市", "SZ" if symbol.startswith('0') else "SH", "主板", "金融", datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ 完成！已生成 {len(stocks)} 只股票的模拟数据")


if __name__ == "__main__":
    populate_mock_database()
