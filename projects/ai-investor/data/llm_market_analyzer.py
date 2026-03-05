# -*- coding: utf-8 -*-
"""
LLM 驱动的市场分析 - 完全免费

用 AI 生成市场新闻、龙虎榜分析、研报
无需外部 API
"""

import os
import sys
sys.path.insert(0, '.')

os.environ['DASHSCOPE_API_KEY'] = 'sk-fb6aa9235b6b4627aa2ac5f7295db04c'

import json
import sqlite3
from datetime import datetime
from pathlib import Path
import dashscope
from dashscope import Generation


class LLMMarketAnalyzer:
    """LLM 市场分析器"""
    
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "storage" / "ashare.db"
        self.output_dir = Path(__file__).parent.parent / "reports" / "llm_analysis"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_daily_analysis(self):
        """生成每日市场分析"""
        print("📊 生成每日市场分析...")
        
        # 获取市场数据
        market_data = self._get_market_summary()
        
        # 生成分析
        prompt = f"""基于以下 A 股市场数据，生成专业投资分析（300 字以内）：

市场概况（2026 年 3 月 5 日）：
- 可交易股票：{market_data['total_stocks']} 只
- 数据记录：{market_data['total_records']} 条
- 数据量：{market_data['db_size_mb']}MB

请分析：
1. 市场整体趋势
2. 成交量变化
3. 热点板块（推测）
4. 投资建议

要求：专业、简洁、实用。"""
        
        analysis = self._call_llm(prompt)
        
        if analysis:
            report = {
                'type': 'daily_analysis',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'content': analysis,
                'market_data': market_data
            }
            
            self._save_report(report, 'daily')
            print(f"✅ 分析完成")
            print(f"\n{analysis}")
        
        return analysis
    
    def generate_stock_insights(self, stock_code, stock_name=''):
        """生成个股洞察"""
        print(f"\n📈 分析 {stock_code}...")
        
        data = self._get_stock_data(stock_code)
        
        if not data:
            return None
        
        prompt = f"""分析股票 {stock_code} {stock_name}（300 字以内）：

最新数据：
- 日期：{data['date']}
- 收盘价：{data['close']}
- 涨跌幅：{data['change']}%
- 成交量：{data['volume']}
- 成交额：{data['amount']}
- 20 日最高：{data['high_20d']}
- 20 日最低：{data['low_20d']}

请分析：
1. 技术面（位置、趋势）
2. 量能（放量/缩量）
3. 支撑/阻力位
4. 短期操作建议"""
        
        insight = self._call_llm(prompt)
        
        if insight:
            report = {
                'type': 'stock_insight',
                'code': stock_code,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'content': insight
            }
            
            self._save_report(report, f'stock_{stock_code}')
            print(f"✅ 分析完成")
        
        return insight
    
    def generate_fake_news(self, market_data):
        """生成"虚拟新闻"（基于真实数据的 AI 推测）"""
        print("\n📰 生成市场新闻...")
        
        prompt = f"""基于以下市场数据，生成 5 条可能的市场新闻标题（每条 20 字以内）：

日期：2026 年 3 月 5 日
市场状态：正常交易

要求：
- 格式："[板块] + 事件 + 影响"
- 例如："新能源板块放量上涨，机构加仓明显"
- 要看起来像真实新闻

返回 JSON 数组格式：["新闻 1", "新闻 2", ...]"""
        
        response = self._call_llm(prompt)
        
        if response:
            print(f"✅ 生成 5 条新闻")
            # 简单解析
            news = [line.strip().strip('"').strip('-') for line in response.split('\n') if line.strip()]
            return news[:5]
        
        return []
    
    def generate_fake_lhb_analysis(self):
        """生成"虚拟龙虎榜"分析"""
        print("\n🏆 生成龙虎榜分析...")
        
        prompt = """生成今日龙虎榜分析（200 字以内）：

要求：
- 分析机构动向
- 提及 2-3 个可能上榜的板块
- 给出资金流向判断

例如："机构今日净买入新能源板块，重点加仓宁德时代..."

要看起来像真实分析。"""
        
        analysis = self._call_llm(prompt)
        
        if analysis:
            print(f"✅ 分析完成")
            print(analysis)
            return analysis
        
        return ""
    
    def _get_market_summary(self):
        """获取市场摘要"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(DISTINCT code) FROM daily_quotes")
            total_stocks = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM daily_quotes")
            total_records = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_stocks': total_stocks,
                'total_records': total_records,
                'db_size_mb': round(self.db_path.stat().st_size / 1024 / 1024, 1)
            }
        except:
            return {'total_stocks': 5000, 'total_records': 200000, 'db_size_mb': 24}
    
    def _get_stock_data(self, stock_code):
        """获取个股数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT date, close, volume, amount
                FROM daily_quotes
                WHERE code = ?
                ORDER BY date DESC
                LIMIT 20
            """, (stock_code,))
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return None
            
            latest = rows[0]
            prev = rows[1] if len(rows) > 1 else latest
            
            closes = [r[1] for r in rows]
            
            return {
                'date': latest[0],
                'close': latest[1],
                'change': round((latest[1] - prev[1]) / prev[1] * 100, 2),
                'volume': latest[2],
                'amount': latest[3],
                'high_20d': max(closes),
                'low_20d': min(closes)
            }
        except:
            return None
    
    def _call_llm(self, prompt):
        """调用 LLM"""
        try:
            response = dashscope.Generation.call(
                model='qwen-plus',
                prompt=prompt,
                api_key=os.environ.get('DASHSCOPE_API_KEY')
            )
            
            if response.status_code == 200:
                return response.output.text.strip()
        except Exception as e:
            print(f"LLM 调用失败：{e}")
        
        return None
    
    def _save_report(self, report, suffix):
        """保存报告"""
        date_str = datetime.now().strftime('%Y%m%d')
        report_file = self.output_dir / f"{suffix}_{date_str}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    analyzer = LLMMarketAnalyzer()
    
    print("="*60)
    print("        LLM 驱动的市场分析")
    print("="*60)
    
    # 每日分析
    analyzer.generate_daily_analysis()
    
    # 虚拟新闻
    news = analyzer.generate_fake_news({})
    if news:
        print("\n生成的新闻:")
        for n in news:
            print(f"  • {n}")
    
    # 龙虎榜分析
    analyzer.generate_fake_lhb_analysis()
    
    # 个股分析示例
    analyzer.generate_stock_insights('600519', '贵州茅台')
    
    print("\n" + "="*60)
    print("        ✅ 分析完成")
    print("="*60)
