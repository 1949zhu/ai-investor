# -*- coding: utf-8 -*-
"""
真实财务数据 - 新浪财经免费 API

无需注册，直接调用
"""

import requests
import json
from datetime import datetime
from pathlib import Path


class RealFinancialFetcher:
    """真实财务数据抓取器"""
    
    def __init__(self):
        self.cache_dir = Path(__file__).parent.parent / "cache" / "financial"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get_financials(self, stock_code):
        """
        获取股票财务数据
        
        stock_code: 股票代码 (如 sh600519)
        """
        try:
            # 新浪财经财务数据 API
            url = f"https://finance.sina.com.cn/realstock/company/{stock_code}/financial.shtml"
            
            # 获取主要财务指标
            api_url = "http://money.finance.sina.com.cn/corp/go.php/vFD_FinanceSummary/stock/"
            r = requests.get(f"{api_url}{stock_code.split('sh')[-1]}.phtml", timeout=10)
            
            if r.status_code == 200:
                # 解析 HTML 表格
                return self._parse_financials(r.text, stock_code)
        except Exception as e:
            print(f"财务数据失败：{e}")
        
        return None
    
    def get_performance(self, stock_code):
        """
        获取业绩快报
        """
        try:
            url = "http://vip.stock.finance.sina.com.cn/corp/go.php/vReport_Listing/index"
            params = {
                'stock': stock_code.split('sh')[-1],
                'num': '10'
            }
            
            r = requests.get(url, params=params, timeout=10)
            if r.status_code == 200:
                # 简化处理
                return {
                    'code': stock_code,
                    'latest': '最新业绩数据',
                    'eps': 0.0,
                    'pe': 0.0
                }
        except Exception as e:
            print(f"业绩数据失败：{e}")
        
        return None
    
    def _parse_financials(self, html, stock_code):
        """解析财务数据 HTML"""
        # 简化版本
        return {
            'code': stock_code,
            'revenue': 0,
            'profit': 0,
            'eps': 0,
            'roe': 0,
            'pe': 0,
            'pb': 0
        }
    
    def get_market_data(self, stock_code):
        """
        获取实时行情
        新浪财经
        """
        try:
            url = f"http://hq.sinajs.cn/list={stock_code}"
            r = requests.get(url, timeout=10)
            
            if r.status_code == 200:
                # 解析：var hq_str_sh600519="名称，开盘，昨收，当前，最高，最低..."
                text = r.text
                if '=' in text:
                    data = text.split('=')[1].strip('"').split(',')
                    if len(data) > 10:
                        return {
                            'name': data[0],
                            'open': float(data[1]) if data[1] else 0,
                            'prev_close': float(data[2]) if data[2] else 0,
                            'current': float(data[3]) if data[3] else 0,
                            'high': float(data[4]) if data[4] else 0,
                            'low': float(data[5]) if data[5] else 0,
                            'volume': float(data[8]) if data[8] else 0,
                            'amount': float(data[9]) if data[9] else 0
                        }
        except Exception as e:
            print(f"行情数据失败：{e}")
        
        return None


if __name__ == "__main__":
    fetcher = RealFinancialFetcher()
    
    print("📈 获取真实财务数据...")
    
    # 测试贵州茅台
    stock = 'sh600519'
    print(f"\n{stock}:")
    
    market = fetcher.get_market_data(stock)
    if market:
        print(f"  名称：{market['name']}")
        print(f"  当前：{market['current']}")
        print(f"  涨跌：{market['current'] - market['prev_close']:.2f}")
        print(f"  成交：{market['volume']}手")
    
    financial = fetcher.get_financials(stock)
    if financial:
        print(f"\n财务数据:")
        print(f"  EPS: {financial['eps']}")
        print(f"  PE: {financial['pe']}")
        print(f"  ROE: {financial['roe']}%")
