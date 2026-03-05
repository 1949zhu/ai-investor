"""
A 股数据获取模块 - BaoStock 版本
使用 BaoStock 获取真实股票行情数据（免费、无需 token）
官网：http://baostock.com
"""

import baostock as bs
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import time
from typing import Optional, List


class BaoStockDataFetcher:
    """BaoStock A 股数据获取器"""
    
    def __init__(self, db_path: str = "storage/ashare.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 登录 BaoStock
        self._login()
        self._init_db()
    
    def _login(self):
        """登录 BaoStock"""
        lg = bs.login()
        if lg.error_code == '0':
            print("✅ BaoStock 登录成功")
        else:
            print(f"⚠️ BaoStock 登录提示：{lg.error_msg}")
    
    def _logout(self):
        """登出 BaoStock"""
        bs.logout()
    
    def _init_db(self):
        """初始化数据库表结构"""
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
        
        conn.commit()
        conn.close()
    
    def get_stock_list(self) -> pd.DataFrame:
        """获取 A 股股票列表"""
        print("获取 A 股股票列表...")
        
        all_stocks = []
        
        # 获取上证 50 成分股（高质量大盘股）
        rs = bs.query_sz50_stocks()
        if rs.error_code == '0':
            df = rs.get_data()
            all_stocks.append(df)
            print(f"  上证 50: {len(df)} 只")
        
        # 获取沪深 300 成分股
        rs = bs.query_hs300_stocks()
        if rs.error_code == '0':
            df = rs.get_data()
            all_stocks.append(df)
            print(f"  沪深 300: {len(df)} 只")
        
        # 获取中证 500 成分股
        rs = bs.query_zz500_stocks()
        if rs.error_code == '0':
            df = rs.get_data()
            all_stocks.append(df)
            print(f"  中证 500: {len(df)} 只")
        
        if not all_stocks:
            print("未获取到股票数据")
            return pd.DataFrame()
        
        # 合并并去重
        df = pd.concat(all_stocks, ignore_index=True)
        df = df.drop_duplicates(subset=['code'])
        
        # 提取纯数字代码
        df['symbol'] = df['code'].str.replace('sh.', '').str.replace('sz.', '')
        df['name'] = df['code_name']
        
        print(f"  总计：{len(df)} 只股票")
        
        return df
    
    def get_stock_basic_info(self, symbol: str) -> dict:
        """获取股票基本信息"""
        # 转换代码格式
        if symbol.startswith('6'):
            code = f"sh.{symbol}"
        else:
            code = f"sz.{symbol}"
        
        rs = bs.query_stock_basic(code)
        if rs.error_code == '0':
            df = rs.get_data()
            if not df.empty:
                row = df.iloc[0]
                return {
                    'symbol': symbol,
                    'name': row.get('stockName', symbol),
                    'list_date': row.get('launchDate', ''),
                    'status': '上市',
                    'exchange': 'SH' if symbol.startswith('6') else 'SZ',
                    'industry': row.get('industry', '')
                }
        return {'symbol': symbol, 'name': symbol}
    
    def get_daily_quotes(self, symbol: str, start_date: str, end_date: str, retries: int = 3) -> pd.DataFrame:
        """
        获取个股日线行情（带重试机制）
        
        Args:
            symbol: 股票代码 (如：000001)
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            retries: 重试次数
        """
        # 转换代码格式
        if symbol.startswith('6'):
            code = f"sh.{symbol}"
        else:
            code = f"sz.{symbol}"
        
        # 转换日期格式
        start = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]}"
        end = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]}"
        
        for attempt in range(retries):
            try:
                # 获取日线数据（前复权）
                # BaoStock 不提供 turnover，用基础参数
                rs = bs.query_history_k_data_plus(
                    code,
                    "date,open,high,low,close,volume,amount",
                    start_date=start,
                    end_date=end,
                    frequency="d",
                    adjustflag="3"  # 前复权
                )
                
                if rs.error_code != '0':
                    raise Exception(rs.error_msg)
                
                df = rs.get_data()
                
                if not df.empty:
                    # 标准化列名
                    df = df.rename(columns={
                        'date': 'trade_date',
                        'open': 'open',
                        'high': 'high',
                        'low': 'low',
                        'close': 'close',
                        'volume': 'volume',
                        'amount': 'amount'
                    })
                    
                    # 转换日期格式为 YYYYMMDD
                    df['trade_date'] = pd.to_datetime(df['trade_date']).dt.strftime('%Y%m%d')
                    
                    # 转换数值列为 float（BaoStock 返回字符串）
                    numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'amount']
                    for col in numeric_cols:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    
                    # 计算涨跌幅
                    df['pct_chg'] = df['close'].pct_change() * 100
                    df['change'] = df['close'] - df['open']
                    
                    # 计算振幅
                    df['amplitude'] = (df['high'] - df['low']) / df['low'] * 100
                    
                    # 换手率设为 0（BaoStock 不提供）
                    df['turnover'] = 0.0
                    
                    return df
                
                return pd.DataFrame()
                
            except Exception as e:
                if attempt < retries - 1:
                    print(f"获取 {symbol} 数据失败 (尝试 {attempt+1}/{retries})，重试中...")
                    time.sleep(2 ** attempt)
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
                row.get('trade_date', ''),
                float(row.get('open', 0) or 0),
                float(row.get('high', 0) or 0),
                float(row.get('low', 0) or 0),
                float(row.get('close', 0) or 0),
                float(row.get('volume', 0) or 0),
                float(row.get('amount', 0) or 0),
                float(row.get('amplitude', 0) or 0),
                float(row.get('pct_chg', 0) or 0),
                float(row.get('change', 0) or 0),
                float(row.get('turnover', 0) or 0)
            ))
        
        conn.commit()
        conn.close()
    
    def save_stock_info(self, df: pd.DataFrame):
        """保存股票基本信息"""
        conn = sqlite3.connect(self.db_path)
        
        for _, row in df.iterrows():
            symbol = str(row.get('code', row.get('symbol', '')))
            if not symbol or len(symbol) != 6:
                continue
            
            # 获取详细信息
            info = self.get_stock_basic_info(symbol)
            
            conn.execute('''
                INSERT OR REPLACE INTO stock_info 
                (symbol, name, list_date, delist_date, status, exchange, board, industry, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                info.get('name', symbol),
                info.get('list_date', ''),
                '',
                info.get('status', '上市'),
                info.get('exchange', 'SZ' if symbol.startswith('0') or symbol.startswith('3') else 'SH'),
                '主板',
                info.get('industry', ''),
                datetime.now().isoformat()
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
        if stock_list.empty:
            print("❌ 无法获取股票列表")
            return
        
        print(f"共获取到 {len(stock_list)} 只股票")
        
        # 获取最近一年的数据
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
        
        # 保存股票信息
        self.save_stock_info(stock_list)
        
        # 获取前 N 只股票的行情数据
        count = 0
        for _, row in stock_list.head(limit).iterrows():
            symbol = str(row.get('code', row.get('symbol', ''))).zfill(6)
            if not symbol or len(symbol) != 6:
                continue
            
            # 获取股票名称
            info = self.get_stock_basic_info(symbol)
            name = info.get('name', symbol)
            
            print(f"[{count+1}/{limit}] 获取 {symbol} - {name} 的数据...")
            
            df = self.get_daily_quotes(symbol, start_date, end_date)
            
            if not df.empty:
                self.save_daily_quotes(symbol, df)
                count += 1
                print(f"  ✅ 成功获取 {len(df)} 条记录")
            else:
                print(f"  ⚠️ 无数据")
            
            # 避免请求过快
            time.sleep(0.1)
        
        print(f"\n完成！成功获取 {count}/{limit} 只股票的数据")
        
        # 登出
        self._logout()
    
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
    print("=" * 50)
    print("BaoStock 数据获取器测试")
    print("=" * 50)
    
    # 测试股票
    test_symbols = ["000001", "600000", "300750"]
    
    fetcher = BaoStockDataFetcher()
    
    # 获取股票列表
    stock_list = fetcher.get_stock_list()
    if not stock_list.empty:
        print(f"\n股票列表前 10 条:")
        print(stock_list[['code']].head(10))
    
    # 测试获取单只股票数据
    for symbol in test_symbols:
        print(f"\n获取 {symbol} 的行情数据...")
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        df = fetcher.get_daily_quotes(symbol, start_date, end_date)
        
        if not df.empty:
            print(f"成功获取 {len(df)} 条记录")
            print(df[['trade_date', 'close', 'pct_chg']].tail())
            
            # 保存到数据库
            fetcher.save_daily_quotes(symbol, df)
            print("数据已保存到数据库")
        else:
            print("无数据返回")
    
    fetcher._logout()
