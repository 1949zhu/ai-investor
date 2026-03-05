"""
A 股数据获取模块
使用 AkShare 获取股票行情、财务、宏观数据
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
from typing import Optional, List
import time


class AShareDataFetcher:
    """A 股数据获取器"""
    
    def __init__(self, db_path: str = "storage/ashare.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 日线行情表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_quotes (
                symbol TEXT,
                trade_date TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                amount REAL,
                amplitude REAL,
                pct_chg REAL,
                change REAL,
                turnover REAL,
                PRIMARY KEY (symbol, trade_date)
            )
        ''')
        
        # 股票基本信息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_info (
                symbol TEXT PRIMARY KEY,
                name TEXT,
                list_date TEXT,
                delist_date TEXT,
                status TEXT,
                exchange TEXT,
                board TEXT,
                industry TEXT,
                updated_at TEXT
            )
        ''')
        
        # 策略回测结果表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backtest_results (
                strategy_id TEXT PRIMARY KEY,
                strategy_name TEXT,
                start_date TEXT,
                end_date TEXT,
                total_return REAL,
                annual_return REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                win_rate REAL,
                trade_count INTEGER,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_stock_list(self) -> pd.DataFrame:
        """获取 A 股股票列表"""
        print("获取 A 股股票列表...")
        df = ak.stock_info_a_code_name()
        df['updated_at'] = datetime.now().isoformat()
        return df
    
    def get_daily_quotes(self, symbol: str, start_date: str, end_date: str, retries: int = 3) -> pd.DataFrame:
        """
        获取个股日线行情（带重试机制）
        
        Args:
            symbol: 股票代码 (如：000001)
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            retries: 重试次数
        """
        for attempt in range(retries):
            try:
                df = ak.stock_zh_a_hist(
                    symbol=symbol,
                    period="daily",
                    start_date=start_date,
                    end_date=end_date,
                    adjust="qfq"  # 前复权
                )
                if not df.empty:
                    # 标准化列名
                    df = df.rename(columns={
                        '日期': 'trade_date',
                        '开盘': 'open',
                        '最高': 'high',
                        '最低': 'low',
                        '收盘': 'close',
                        '成交量': 'volume',
                        '成交额': 'amount',
                        '振幅': 'amplitude',
                        '涨跌幅': 'pct_chg',
                        '涨跌额': 'change',
                        '换手率': 'turnover'
                    })
                return df
            except Exception as e:
                if attempt < retries - 1:
                    print(f"获取 {symbol} 数据失败 (尝试 {attempt+1}/{retries})，重试中...")
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    print(f"获取 {symbol} 数据失败：{e}")
        return pd.DataFrame()
    
    def save_daily_quotes(self, symbol: str, df: pd.DataFrame):
        """保存日线数据到数据库"""
        if df.empty:
            return
        
        conn = sqlite3.connect(self.db_path)
        
        for _, row in df.iterrows():
            conn.execute('''
                INSERT OR REPLACE INTO daily_quotes 
                (symbol, trade_date, open, high, low, close, volume, amount, 
                 amplitude, pct_chg, change, turnover)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                row.get('日期', ''),
                row.get('开盘', 0),
                row.get('最高', 0),
                row.get('最低', 0),
                row.get('收盘', 0),
                row.get('成交量', 0),
                row.get('成交额', 0),
                row.get('振幅', 0),
                row.get('涨跌幅', 0),
                row.get('涨跌额', 0),
                row.get('换手率', 0)
            ))
        
        conn.commit()
        conn.close()
    
    def save_stock_info(self, df: pd.DataFrame):
        """保存股票基本信息"""
        conn = sqlite3.connect(self.db_path)
        
        for _, row in df.iterrows():
            conn.execute('''
                INSERT OR REPLACE INTO stock_info 
                (symbol, name, list_date, delist_date, status, exchange, board, industry, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row.get('code', ''),
                row.get('name', ''),
                row.get('list_date', ''),
                row.get('delist_date', ''),
                row.get('status', ''),
                row.get('exchange', ''),
                row.get('board', ''),
                row.get('industry', ''),
                row.get('updated_at', '')
            ))
        
        conn.commit()
        conn.close()
    
    def fetch_all_stocks_data(self, limit: int = 100):
        """
        批量获取股票数据（用于初始化）
        
        Args:
            limit: 获取的股票数量限制
        """
        # 获取股票列表
        stock_list = self.get_stock_list()
        print(f"共获取到 {len(stock_list)} 只股票")
        
        # 获取最近一年的数据
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
        
        # 保存股票信息
        self.save_stock_info(stock_list)
        
        # 获取前 N 只股票的行情数据
        count = 0
        for _, row in stock_list.head(limit).iterrows():
            symbol = row.get('code', '')
            if not symbol:
                continue
            
            print(f"[{count+1}/{limit}] 获取 {symbol} - {row.get('name', '')} 的数据...")
            df = self.get_daily_quotes(symbol, start_date, end_date)
            if not df.empty:
                self.save_daily_quotes(symbol, df)
                count += 1
            
            # 避免请求过快
            time.sleep(0.5)
        
        print(f"完成！成功获取 {count} 只股票的数据")
    
    def get_stock_quotes_from_db(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """从数据库获取股票行情"""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT * FROM daily_quotes WHERE symbol = ?"
        params = [symbol]
        
        if start_date:
            query += " AND trade_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND trade_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY trade_date"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df


if __name__ == "__main__":
    # 测试
    fetcher = AShareDataFetcher()
    
    # 获取股票列表
    stock_list = fetcher.get_stock_list()
    print(f"\n股票列表前 10 条:")
    print(stock_list.head(10))
    
    # 保存股票信息
    fetcher.save_stock_info(stock_list)
    print("\n股票信息已保存")
    
    # 获取单只股票数据测试
    test_symbol = "000001"
    print(f"\n获取 {test_symbol} 的行情数据...")
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
    df = fetcher.get_daily_quotes(test_symbol, start_date, end_date)
    print(df.head())
    
    # 保存到数据库
    fetcher.save_daily_quotes(test_symbol, df)
    print("数据已保存到数据库")
