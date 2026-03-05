# -*- coding: utf-8 -*-
"""
真实龙虎榜数据 - 东方财富网免费 API

无需注册，直接调用
"""

import requests
import json
from datetime import datetime
from pathlib import Path


class RealLHBFetcher:
    """真实龙虎榜抓取器"""
    
    def __init__(self):
        self.cache_dir = Path(__file__).parent.parent / "cache" / "lhb"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_today(self):
        """
        获取今日龙虎榜
        东方财富网公开数据
        """
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
                'fields': 'f12,f14,f2,f3,f4,f10,f11,f13,f15,f16,f17,f18,f20,f21,f22,f23,f24,f25',
                '_': str(int(datetime.now().timestamp() * 1000))
            }
            
            r = requests.get(url, params=params, timeout=10)
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
                        'buy_amount': item.get('f21', 0),
                        'sell_amount': item.get('f22', 0),
                        'net_amount': item.get('f23', 0),
                        'reason_code': item.get('f29', '')
                    })
                
                self._save_cache(lhb_list)
                return lhb_list
        except Exception as e:
            print(f"龙虎榜失败：{e}")
        
        return []
    
    def _save_cache(self, lhb_list):
        """保存缓存"""
        cache_file = self.cache_dir / f"lhb_{datetime.now().strftime('%Y%m%d')}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'timestamp': datetime.now().isoformat(),
                'count': len(lhb_list),
                'data': lhb_list
            }, f, ensure_ascii=False, indent=2)
    
    def get_top_buy(self, lhb_list, top=10):
        """净买入前 10"""
        sorted_list = sorted(lhb_list, key=lambda x: x.get('net_amount', 0), reverse=True)
        return sorted_list[:top]
    
    def get_top_sell(self, lhb_list, top=10):
        """净卖出前 10"""
        sorted_list = sorted(lhb_list, key=lambda x: x.get('net_amount', 0))
        return sorted_list[:top]
    
    def get_stats(self, lhb_list):
        """统计信息"""
        if not lhb_list:
            return {'total': 0}
        
        total_buy = sum(s.get('buy_amount', 0) for s in lhb_list)
        total_sell = sum(s.get('sell_amount', 0) for s in lhb_list)
        
        return {
            'total': len(lhb_list),
            'total_buy': total_buy,
            'total_sell': total_sell,
            'net': total_buy - total_sell
        }


if __name__ == "__main__":
    fetcher = RealLHBFetcher()
    
    print("📊 获取真实龙虎榜...")
    lhb = fetcher.fetch_today()
    
    if lhb:
        print(f"✅ 共 {len(lhb)} 只股票")
        
        print(f"\n净买入前 5:")
        top_buy = fetcher.get_top_buy(lhb, 5)
        for stock in top_buy:
            print(f"  {stock['code']} {stock['name']} 净买入 {stock['net_amount']/10000:.1f}万")
        
        stats = fetcher.get_stats(lhb)
        print(f"\n统计:")
        print(f"  总买入：{stats['total_buy']/100000000:.2f}亿")
        print(f"  总卖出：{stats['total_sell']/100000000:.2f}亿")
        print(f"  净额：{stats['net']/100000000:.2f}亿")
    else:
        print("⚠️ 今日无龙虎榜数据（可能休市）")
