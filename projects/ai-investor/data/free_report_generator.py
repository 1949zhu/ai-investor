# -*- coding: utf-8 -*-
"""
免费研报生成 - 用 LLM 分析已有数据

无需外部 API，用 AI 生成专业分析
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


class FreeReportGenerator:
    """免费研报生成器"""
    
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "storage" / "ashare.db"
        self.reports_dir = Path(__file__).parent.parent / "reports" / "research"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_stock_report(self, stock_code, stock_name=None):
        """
        为单只股票生成研报
        
        stock_code: 股票代码
        stock_name: 股票名称（可选）
        """
        # 获取股票数据
        stock_data = self._get_stock_data(stock_code)
        
        if not stock_data:
            return None
        
        # 用 LLM 生成研报
        report = self._llm_generate_report(stock_code, stock_data)
        
        if report:
            self._save_report(stock_code, report)
        
        return report
    
    def _get_stock_data(self, stock_code):
        """从数据库获取股票数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 获取最新数据
            cursor.execute("""
                SELECT date, open, high, low, close, volume, amount
                FROM daily_quotes
                WHERE code = ?
                ORDER BY date DESC
                LIMIT 30
            """, (stock_code,))
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return None
            
            # 计算指标
            latest = rows[0]
            prev = rows[1] if len(rows) > 1 else latest
            
            data = {
                'code': stock_code,
                'latest_date': latest[0],
                'price': latest[5],
                'change': round((latest[5] - prev[5]) / prev[5] * 100, 2) if prev[5] else 0,
                'volume': latest[6],
                'amount': latest[7],
                'high_30d': max(r[2] for r in rows),
                'low_30d': min(r[3] for r in rows),
                'avg_volume': sum(r[6] for r in rows) / len(rows)
            }
            
            return data
            
        except Exception as e:
            print(f"获取股票数据失败：{e}")
            return None
    
    def _llm_generate_report(self, stock_code, data):
        """用 LLM 生成研报"""
        prompt = f"""请为以下股票生成简短的投资分析报告（200 字以内）：

股票代码：{stock_code}
最新价格：{data['price']}
涨跌幅：{data['change']}%
30 日最高：{data['high_30d']}
30 日最低：{data['low_30d']}
成交量：{data['volume']}
成交额：{data['amount']}

请分析：
1. 技术面（价格位置、趋势）
2. 成交量（是否放量）
3. 短期建议（买入/持有/观望）

只返回分析内容，不要其他格式。"""
        
        try:
            response = dashscope.Generation.call(
                model='qwen-plus',
                prompt=prompt,
                api_key=os.environ.get('DASHSCOPE_API_KEY')
            )
            
            if response.status_code == 200:
                return {
                    'code': stock_code,
                    'content': response.output.text.strip(),
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            print(f"LLM 生成失败：{e}")
        
        return None
    
    def _save_report(self, stock_code, report):
        """保存研报"""
        date_str = datetime.now().strftime('%Y%m%d')
        report_file = self.reports_dir / f"report_{stock_code}_{date_str}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    
    def generate_market_summary(self):
        """生成市场整体分析"""
        prompt = """请分析当前 A 股市场整体情况（基于 2026 年 3 月）：

1. 市场情绪（乐观/悲观/中性）
2. 主要风险点
3. 投资机会
4. 配置建议

请给出专业、简洁的分析（300 字以内）。"""
        
        try:
            response = dashscope.Generation.call(
                model='qwen-plus',
                prompt=prompt,
                api_key=os.environ.get('DASHSCOPE_API_KEY')
            )
            
            if response.status_code == 200:
                report = {
                    'type': 'market_summary',
                    'content': response.output.text.strip(),
                    'timestamp': datetime.now().isoformat()
                }
                
                # 保存
                report_file = self.reports_dir / f"market_{datetime.now().strftime('%Y%m%d')}.json"
                with open(report_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)
                
                return report
                
        except Exception as e:
            print(f"市场摘要生成失败：{e}")
        
        return None


if __name__ == "__main__":
    generator = FreeReportGenerator()
    
    print("📄 生成免费研报...")
    
    # 生成市场摘要
    print("\n【市场摘要】")
    market = generator.generate_market_summary()
    if market:
        print(market['content'][:100] + "...")
    
    # 生成个股研报示例
    print("\n【个股研报】")
    report = generator.generate_stock_report('600519')
    if report:
        print(f"股票代码：{report['code']}")
        print(report['content'])
