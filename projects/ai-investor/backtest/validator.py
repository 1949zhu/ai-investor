"""
回测验证框架 - 验证 AI 决策的准确性
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sys

sys.path.insert(0, str(Path(__file__).parent))


class BacktestValidator:
    """AI 决策回测验证"""
    
    def __init__(self, db_path: str = None, memory_db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "storage" / "ashare.db"
        if memory_db_path is None:
            memory_db_path = Path(__file__).parent.parent / "storage" / "agent_memory.db"
        
        self.db_path = db_path
        self.memory_db_path = memory_db_path
    
    def get_decision_history(self, limit: int = 20) -> List[Dict]:
        """获取历史决策记录"""
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, date, market_state, decision, reasoning, outcome, reflection, created_at
            FROM decision_log
            ORDER BY date DESC, id DESC
            LIMIT ?
        """, (limit,))
        
        decisions = [
            {
                "id": r[0],
                "date": r[1],
                "market_state": r[2],
                "decision": r[3],
                "reasoning": r[4],
                "outcome": r[5],
                "reflection": r[6],
                "created_at": r[7]
            }
            for r in cursor.fetchall()
        ]
        
        conn.close()
        return decisions
    
    def simulate_decision(self, symbol: str, decision_date: str, 
                          action: str = "buy", hold_days: int = 5) -> Dict:
        """模拟决策回测"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取决策日期的收盘价
        cursor.execute("""
            SELECT close, trade_date
            FROM daily_quotes
            WHERE symbol = ? AND trade_date <= ?
            ORDER BY trade_date DESC
            LIMIT 1
        """, (symbol, decision_date))
        
        entry_data = cursor.fetchone()
        if not entry_data:
            conn.close()
            return {"error": "未找到入场数据"}
        
        entry_price = entry_data[0]
        actual_entry_date = entry_data[1]
        
        # 获取持有期后的收盘价
        cursor.execute("""
            SELECT close, trade_date
            FROM daily_quotes
            WHERE symbol = ? AND trade_date > ?
            ORDER BY trade_date
            LIMIT 1 OFFSET ?
        """, (symbol, actual_entry_date, hold_days - 1))
        
        exit_data = cursor.fetchone()
        
        if not exit_data:
            # 使用最新可用数据
            cursor.execute("""
                SELECT close, trade_date
                FROM daily_quotes
                WHERE symbol = ?
                ORDER BY trade_date DESC
                LIMIT 1
            """, (symbol,))
            exit_data = cursor.fetchone()
        
        exit_price = exit_data[0] if exit_data else entry_price
        exit_date = exit_data[1] if exit_data else actual_entry_date
        
        # 计算收益
        if entry_price and exit_price and entry_price > 0:
            return_rate = (exit_price - entry_price) / entry_price
        else:
            return_rate = 0
        
        conn.close()
        
        return {
            "symbol": symbol,
            "action": action,
            "entry_date": actual_entry_date,
            "entry_price": entry_price,
            "exit_date": exit_date,
            "exit_price": exit_price,
            "hold_days": hold_days,
            "return_rate": return_rate,
            "return_pct": return_rate * 100
        }
    
    def validate_past_decisions(self, hold_days: int = 5) -> List[Dict]:
        """验证历史决策"""
        decisions = self.get_decision_history(limit=50)
        results = []
        
        for dec in decisions:
            if dec['outcome'] != "待验证":
                # 已有结果，跳过
                continue
            
            # 解析决策中的股票代码
            decision_text = dec['decision']
            symbols = self._extract_symbols(decision_text)
            
            if not symbols:
                continue
            
            # 模拟回测
            for symbol in symbols[:3]:  # 最多回测前 3 个标的
                result = self.simulate_decision(
                    symbol=symbol,
                    decision_date=dec['date'],
                    hold_days=hold_days
                )
                
                if 'error' not in result:
                    results.append({
                        "decision_id": dec['id'],
                        "decision_date": dec['date'],
                        "decision": dec['decision'][:100],
                        "symbol": result['symbol'],
                        "return_rate": result['return_rate'],
                        "return_pct": result['return_pct'],
                        "hold_days": result['hold_days']
                    })
        
        return results
    
    def _extract_symbols(self, text: str) -> List[str]:
        """从决策文本中提取股票代码"""
        import re
        # 匹配 A 股代码格式
        patterns = [
            r'(\d{6}\.SH)',
            r'(\d{6}\.SZ)',
            r'(\d{6})',
            r'\((\d{6})\)'
        ]
        
        symbols = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) == 6:
                    # 判断市场
                    if match.startswith('6'):
                        symbols.append(f"{match}.SH")
                    elif match.startswith('0') or match.startswith('3'):
                        symbols.append(f"{match}.SZ")
                    else:
                        symbols.append(match)
        
        return list(set(symbols))[:5]
    
    def get_strategy_stats(self) -> Dict:
        """获取策略统计"""
        results = self.validate_past_decisions()
        
        if not results:
            return {"error": "暂无回测数据"}
        
        returns = [r['return_rate'] for r in results]
        winning_trades = sum(1 for r in returns if r > 0)
        
        return {
            "total_trades": len(results),
            "winning_trades": winning_trades,
            "losing_trades": len(results) - winning_trades,
            "win_rate": winning_trades / len(results) if results else 0,
            "avg_return": sum(returns) / len(returns) if returns else 0,
            "max_return": max(returns) if returns else 0,
            "min_return": min(returns) if returns else 0,
            "total_return": sum(returns),
            "trades": results
        }
    
    def update_decision_outcomes(self):
        """批量更新决策结果"""
        results = self.validate_past_decisions()
        
        conn = sqlite3.connect(self.memory_db_path)
        cursor = conn.cursor()
        
        # 按 decision_id 分组
        decision_results = {}
        for r in results:
            dec_id = r['decision_id']
            if dec_id not in decision_results:
                decision_results[dec_id] = []
            decision_results[dec_id].append(r)
        
        # 更新每个决策
        for dec_id, trades in decision_results.items():
            avg_return = sum(t['return_rate'] for t in trades) / len(trades)
            outcome = f"平均收益 {avg_return*100:.2f}%"
            reflection = f"共{len(trades)}笔交易，胜率{sum(1 for t in trades if t['return_rate']>0)/len(trades)*100:.1f}%"
            
            cursor.execute("""
                UPDATE decision_log
                SET outcome = ?, reflection = ?
                WHERE id = ?
            """, (outcome, reflection, dec_id))
        
        conn.commit()
        conn.close()
        
        return len(decision_results)
    
    def generate_validation_report(self, output_path: str = None) -> str:
        """生成验证报告"""
        if output_path is None:
            output_path = Path(__file__).parent.parent / "reports" / f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        stats = self.get_strategy_stats()
        
        report = f"""# AI 决策验证报告

**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 回测统计

| 指标 | 数值 |
|------|------|
| 总交易数 | {stats.get('total_trades', 0)} |
| 盈利交易 | {stats.get('winning_trades', 0)} |
| 亏损交易 | {stats.get('losing_trades', 0)} |
| 胜率 | {stats.get('win_rate', 0)*100:.1f}% |
| 平均收益 | {stats.get('avg_return', 0)*100:.2f}% |
| 最大收益 | {stats.get('max_return', 0)*100:.2f}% |
| 最小收益 | {stats.get('min_return', 0)*100:.2f}% |
| 累计收益 | {stats.get('total_return', 0)*100:.2f}% |

---

## 交易明细

| 决策日期 | 标的 | 收益 | 持有天数 |
|----------|------|------|----------|
"""
        
        trades = stats.get('trades', [])
        for t in trades[:20]:  # 最多显示 20 笔
            report += f"| {t['decision_date']} | {t['symbol']} | {t['return_pct']:.2f}% | {t['hold_days']} |\n"
        
        report += f"""
---

## 分析结论

"""
        
        if stats.get('total_trades', 0) > 0:
            win_rate = stats.get('win_rate', 0)
            avg_return = stats.get('avg_return', 0)
            
            if win_rate > 0.6:
                report += "✅ **胜率优秀** (>60%)\n"
            elif win_rate > 0.45:
                report += "⚠️ **胜率一般** (45-60%)\n"
            else:
                report += "❌ **胜率偏低** (<45%)\n"
            
            if avg_return > 0.05:
                report += "✅ **平均收益优秀** (>5%)\n"
            elif avg_return > 0:
                report += "⚠️ **平均收益为正** (0-5%)\n"
            else:
                report += "❌ **平均收益为负**\n"
        else:
            report += "暂无足够数据进行统计分析。\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return str(output_path)


if __name__ == "__main__":
    print("测试回测验证框架...")
    
    validator = BacktestValidator()
    
    # 获取历史决策
    print("\n历史决策记录:")
    decisions = validator.get_decision_history(limit=5)
    for d in decisions:
        print(f"  [{d['date']}] {d['decision'][:50]}... → {d['outcome']}")
    
    # 验证历史决策
    print("\n验证历史决策...")
    results = validator.validate_past_decisions(hold_days=5)
    print(f"  找到 {len(results)} 笔可回测交易")
    
    # 获取统计
    print("\n策略统计:")
    stats = validator.get_strategy_stats()
    if 'error' not in stats:
        print(f"  总交易：{stats.get('total_trades', 0)}")
        print(f"  胜率：{stats.get('win_rate', 0)*100:.1f}%")
        print(f"  平均收益：{stats.get('avg_return', 0)*100:.2f}%")
    else:
        print(f"  {stats['error']}")
    
    # 生成报告
    print("\n生成验证报告...")
    report_path = validator.generate_validation_report()
    print(f"  报告已保存：{report_path}")
