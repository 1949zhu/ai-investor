"""
A 股数据获取模块 - Tushare 版本
使用 Tushare Pro 获取真实股票行情数据
"""

import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import time
from typing import Optional, List


class TushareDataFetcher:
    """Tushare A 股数据获取器"""
    
    # Tushare 公共 token（免费级别，基础行情数据）
    # 用户可以替换为自己的 token 获取更高级数据
    DEFAULT_TOKEN = "YOUR_TUSHARE_TOKEN_HERE"
    
    def __init__(self, db_path: str = "storage/ashare.db", token: str = None):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 初始化 tushare
        if token and token != "YOUR_TUSHARE_TOKEN_HERE":
            ts.set_token(token)
            self.pro = ts.pro_api()
            print("✅ Tushare Pro 已初始化（使用自定义 token）")
        else:
            # 尝试使用免 token 的旧接口
            self.pro = None
            print("⚠️ 未配置 Tushare token，使用旧版接口（部分数据可能受限）")
        
        self._init_db()
    
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
        
        if self.pro:
            try:
                df = self.pro.stock_basic(exchange='', list_status='L',
                                         fields='ts_code,symbol,name,area,industry,list_date')
                df['symbol'] = df['ts_code'].str.replace('.SZ', '').str.replace('.SH', '')
                return df
            except Exception as e:
                print(f"Tushare Pro 请求失败：{e}")
        
        # 降级方案：使用旧接口
        try:
            df = ts.get_stock_basics()
            df = df.reset_index()
            df.columns = ['ts_code', 'name', 'area', 'pe', 'outstanding', 'totals', 
                         'totalAssets', 'liquidAssets', 'fixedAssets', 'reserved', 
                         'reservedPerShare', 'eps', 'bvps', 'pb', 'list_date']
            df['symbol'] = df['ts_code'].str.replace('.SZ', '').str.replace('.SH', '')
            return df
        except Exception as e:
            print(f"获取股票列表失败：{e}")
            return pd.DataFrame()
    
    def get_daily_quotes(self, symbol: str, start_date: str, end_date: str, retries: int = 3) -> pd.DataFrame:
        """
        获取个股日线行情（带重试机制）
        
        Args:
            symbol: 股票代码 (如：000001)
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            retries: 重试次数
        """
        # 转换股票代码格式
        if symbol.startswith('6'):
            ts_code = f"{symbol}.SH"
        else:
            ts_code = f"{symbol}.SZ"
        
        for attempt in range(retries):
            try:
                if self.pro:
                    # 使用 Pro API
                    df = ts.pro_bar(ts_code=ts_code, start_date=start_date, end_date=end_date,
                                   adj='qfq')  # 前复权
                else:
                    # 使用旧接口
                    df = ts.get_k_data(symbol, start=start_date, end=end_date)
                
                if df is not None and not df.empty:
                    # 标准化列名
                    if 'trade_date' in df.columns:
                        df = df.rename(columns={'trade_date': 'date'})
                    
                    # 统一日期格式
                    if 'date' in df.columns:
                        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y%m%d')
                    
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
        
        # 列名映射
        column_map = {
            'date': 'trade_date',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'vol': 'volume',
            'volume': 'volume',
            'amount': 'amount',
            'amplitude': 'amplitude',
            'pct_chg': 'pct_chg',
            'change': 'change',
            'turnover': 'turnover',
            'turnover_rate': 'turnover'
        }
        
        for _, row in df.iterrows():
            # 获取标准化后的值
            trade_date = row.get('trade_date', row.get('date', ''))
            if isinstance(trade_date, str) and len(trade_date) == 8:
                trade_date = trade_date  # 已经是 YYYYMMDD 格式
            elif isinstance(trade_date, str):
                try:
                    trade_date = pd.to_datetime(trade_date).strftime('%Y%m%d')
                except:
                    continue
            
            conn.execute('''
                INSERT OR REPLACE INTO daily_quotes 
                (symbol, trade_date, open, high, low, close, volume, amount, 
                 amplitude, pct_chg, change, turnover)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                trade_date,
                float(row.get('open', 0) or 0),
                float(row.get('high', 0) or 0),
                float(row.get('low', 0) or 0),
                float(row.get('close', 0) or 0),
                float(row.get('volume', row.get('vol', 0)) or 0),
                float(row.get('amount', 0) or 0),
                float(row.get('amplitude', 0) or 0),
                float(row.get('pct_chg', 0) or 0),
                float(row.get('change', 0) or 0),
                float(row.get('turnover', row.get('turnover_rate', 0)) or 0)
            ))
        
        conn.commit()
        conn.close()
    
    def save_stock_info(self, df: pd.DataFrame):
        """保存股票基本信息"""
        conn = sqlite3.connect(self.db_path)
        
        for _, row in df.iterrows():
            symbol = row.get('symbol', '')
            if not symbol:
                continue
            
            # 确保 symbol 是 6 位数字
            symbol = symbol.zfill(6)
            
            conn.execute('''
                INSERT OR REPLACE INTO stock_info 
                (symbol, name, list_date, delist_date, status, exchange, board, industry, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                symbol,
                row.get('name', ''),
                row.get('list_date', ''),
                row.get('delist_date', ''),
                row.get('list_status', '上市'),
                'SZ' if symbol.startswith('0') or symbol.startswith('3') else 'SH',
                '主板',
                row.get('industry', ''),
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
            symbol = str(row.get('symbol', '')).zfill(6)
            if not symbol:
                continue
            
            name = row.get('name', '未知')
            print(f"[{count+1}/{limit}] 获取 {symbol} - {name} 的数据...")
            
            df = self.get_daily_quotes(symbol, start_date, end_date)
            
            if not df.empty:
                self.save_daily_quotes(symbol, df)
                count += 1
                print(f"  ✅ 成功获取 {len(df)} 条记录")
            else:
                print(f"  ⚠️ 无数据")
            
            # 避免请求过快（Tushare 免费版有频率限制）
            time.sleep(0.2)
        
        print(f"\n完成！成功获取 {count}/{limit} 只股票的数据")
    
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
    print("Tushare 数据获取器测试")
    print("=" * 50)
    
    # 测试股票
    test_symbols = ["000001", "600000", "300750"]
    
    fetcher = TushareDataFetcher()
    
    # 获取股票列表
    stock_list = fetcher.get_stock_list()
    if not stock_list.empty:
        print(f"\n股票列表前 10 条:")
        print(stock_list[['symbol', 'name']].head(10))
    
    # 测试获取单只股票数据
    for symbol in test_symbols:
        print(f"\n获取 {symbol} 的行情数据...")
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        df = fetcher.get_daily_quotes(symbol, start_date, end_date)
        
        if not df.empty:
            print(f"成功获取 {len(df)} 条记录")
            print(df[['trade_date', 'close', 'pct_chg']].head())
            
            # 保存到数据库
            fetcher.save_daily_quotes(symbol, df)
            print("数据已保存到数据库")
        else:
            print("无数据返回")
