# -*- coding: utf-8 -*-
"""
免费龙虎榜数据 - 东方财富网

无需 API Key，直接抓取公开数据
"""

import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
import re


class FreeLHBFetcher:
    """免费龙虎榜抓取器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://data.eastmoney.com/stock/lhb/'
        }
        self.cache_dir = Path(__file__).parent.parent / "cache" / "lhb"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_daily(self, date=None):
        """
        抓取单日龙虎榜
        
        date: 日期字符串 YYYY-MM-DD，默认今天
        """
        if date is None:
            date = datetime.now().strftime('%Y%m%d')
        else:
            date = date.replace('-', '')
        
        try:
            # 东方财富龙虎榜 API
            url = "http://push2.eastmoney.com/api/qt/clist/get"
            params = {
                'pn': '1',
                'pz': '50',
                'po': '1',
                'np': '1',
                'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                'fltt': '2',
                'invt': '2',
                'fid': 'f3',
                'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',
                'fields': 'f12,f14,f2,f3,f4,f12,f14,f2,f3,f4,f10,f11,f13,f14,f15,f16,f17,f18,f20,f21,f22,f23,f24,f25,f26,f27,f28,f29,f30,f31,f32,f33,f34,f35,f36,f37,f38,f39,f40,f41,f42,f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65,f66,f67,f68,f69,f70,f71,f72,f73,f74,f75,f76,f77,f78,f79,f80,f81,f82,f83,f84,f85,f86,f87,f88,f89,f90,f91,f92,f93,f94,f95,f96,f97,f98,f99,f100',
                '_': str(int(datetime.now().timestamp() * 1000))
            }
            
            r = requests.get(url, params=params, headers=self.headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                lhb_list = []
                
                for item in data.get('data', {}).get('diff', []):
                    lhb_list.append({
                        'code': item.get('f12', ''),
                        'name': item.get('f14', ''),
                        'price': item.get('f2', 0),
                        'change': item.get('f3', 0),
                        'volume': item.get('f4', 0),
                        'amount': item.get('f17', 0),
                        'turnover': item.get('f37', 0),
                        'reason': self._get_reason(item.get('f29', '')),
                        'buy_amount': item.get('f21', 0),
                        'sell_amount': item.get('f22', 0),
                        'net_amount': item.get('f23', 0)
                    })
                
                self._save_cache(lhb_list, date)
                return lhb_list
                
        except Exception as e:
            print(f"龙虎榜抓取失败：{e}")
        
        return []
    
    def _get_reason(self, code):
        """解析上榜原因"""
        reasons = {
            '1': '连续三个交易日内收盘价涨幅偏离值累计达 20%',
            '2': '连续三个交易日内收盘价跌幅偏离值累计达 20%',
            '3': '连续三个交易日内日均换手率与前 5 日比值达 30 倍且连续 2 日涨停或跌停',
            '4': '当日收盘价涨幅偏离值达 7%',
            '5': '当日收盘价跌幅偏离值达 7%',
            '6': '当日振幅达 15%',
            '7': '当日换手率达 20%',
            '8': '当日价格振幅达 15% 的 ST 证券',
            '9': '当日换手率达 20% 的 ST 证券'
        }
        return reasons.get(str(code), '未知原因')
    
    def _save_cache(self, lhb_list, date):
        """保存缓存"""
        cache_file = self.cache_dir / f"lhb_{date}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({
                'date': date,
                'timestamp': datetime.now().isoformat(),
                'count': len(lhb_list),
                'data': lhb_list
            }, f, ensure_ascii=False, indent=2)
    
    def get_hot_stocks(self, lhb_list, top=10):
        """获取最活跃股票（净买入最多）"""
        sorted_list = sorted(lhb_list, key=lambda x: x.get('net_amount', 0), reverse=True)
        return sorted_list[:top]
    
    def get_institution_focus(self, lhb_list):
        """统计机构关注度"""
        institution_count = 0
        for stock in lhb_list:
            # 简单判断：净买入额大的可能是机构
            if abs(stock.get('net_amount', 0)) > 10000000:  # 1000 万以上
                institution_count += 1
        
        return {
            'total_stocks': len(lhb_list),
            'institution_focus': institution_count,
            'ratio': round(institution_count / len(lhb_list) * 100, 2) if lhb_list else 0
        }


if __name__ == "__main__":
    fetcher = FreeLHBFetcher()
    
    print("📊 抓取今日龙虎榜...")
    lhb = fetcher.fetch_daily()
    
    if lhb:
        print(f"✅ 共 {len(lhb)} 只股票上榜")
        
        print(f"\n净买入前 5:")
        hot = fetcher.get_hot_stocks(lhb, 5)
        for stock in hot:
            print(f"  {stock['code']} {stock['name']} 净买入：{stock['net_amount']/10000:.1f}万")
        
        inst = fetcher.get_institution_focus(lhb)
        print(f"\n机构关注度:")
        print(f"  上榜股票：{inst['total_stocks']} 只")
        print(f"  机构关注：{inst['institution_focus']} 只 ({inst['ratio']}%)")
