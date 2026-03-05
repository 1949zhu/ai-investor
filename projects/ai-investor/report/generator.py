"""
投资报告生成器
生成专业的投资研究报告和交易建议
"""

from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class ReportGenerator:
    """
    投资报告生成器
    
    生成内容包括：
    1. 市场分析报告
    2. 个股研究报告
    3. 交易建议报告
    4. 持仓跟踪报告
    """
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_investment_report(self, 
                                   strategy_name: str,
                                   stock_analysis: Dict,
                                   recommendation: Dict,
                                   backtest_results: Optional[Dict] = None) -> str:
        """
        生成完整的投资建议报告
        
        Args:
            strategy_name: 使用的策略名称
            stock_analysis: 股票分析数据
            recommendation: 交易建议
            backtest_results: 回测结果（可选）
            
        Returns:
            报告内容（Markdown 格式）
        """
        report_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        report = f"""# 📈 投资研究报告

**报告日期：** {report_date}
**策略名称：** {strategy_name}

---

## 📋 执行摘要

本报告基于 AI 分析生成的投资策略，结合历史数据回测验证，为投资者提供专业的选股和交易建议。

"""
        
        # 回测结果展示
        if backtest_results:
            report += self._format_backtest_summary(backtest_results)
        
        # 股票分析
        report += self._format_stock_analysis(stock_analysis)
        
        # 交易建议
        report += self._format_recommendation(recommendation)
        
        # 风险提示
        report += self._format_risk_warning()
        
        # 保存报告
        filename = f"investment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"投资报告已生成：{filepath}")
        return report
    
    def _format_backtest_summary(self, results: Dict) -> str:
        """格式化回测结果摘要"""
        evaluation_emoji = {
            "PASSED": "✅",
            "ACCEPTABLE": "⚠️",
            "FAILED": "❌",
            "NO_DATA": "⚪"
        }
        
        return f"""## 🧪 策略回测验证

| 指标 | 数值 |
|------|------|
| 回测收益率 | {results.get('total_return_pct', 0):+.2f}% |
| 年化收益 | {results.get('annual_return_pct', 0):+.2f}% |
| 夏普比率 | {results.get('sharpe_ratio', 0):.2f} |
| 最大回撤 | {results.get('max_drawdown_pct', 0):.2f}% |
| 胜率 | {results.get('win_rate_pct', 0):.1f}% |
| 交易次数 | {results.get('trade_count', 0)} |
| 评估结果 | {evaluation_emoji.get(results.get('evaluation', ''), '?')} {results.get('evaluation', 'N/A')} |

> 💡 **策略可信度：** {"高" if results.get('evaluation') == 'PASSED' else "中" if results.get('evaluation') == 'ACCEPTABLE' else "低"}

---

"""
    
    def _format_stock_analysis(self, analysis: Dict) -> str:
        """格式化股票分析"""
        symbols = analysis.get('symbols', [])
        
        content = """## 🔍 选股分析

"""
        
        if not symbols:
            content += "暂无具体选股标的。\n\n"
        else:
            content += "### 推荐标的\n\n"
            for i, stock in enumerate(symbols, 1):
                content += f"""**{i}. {stock.get('symbol', '')} - {stock.get('name', '')}**

- **当前价格：** ¥{stock.get('price', 0):.2f}
- **推荐理由：** {stock.get('reason', 'N/A')}
- **目标价位：** ¥{stock.get('target_price', 0):.2f}
- **止损价位：** ¥{stock.get('stop_loss', 0):.2f}

"""
        
        content += "---\n\n"
        return content
    
    def _format_recommendation(self, rec: Dict) -> str:
        """格式化交易建议"""
        return f"""## 💼 交易建议

### 操作策略

| 项目 | 建议 |
|------|------|
| **操作方向** | {rec.get('action', '观望')} |
| **建议仓位** | {rec.get('position', '0%')} |
| **买入区间** | ¥{rec.get('buy_range_low', 0):.2f} - ¥{rec.get('buy_range_high', 0):.2f} |
| **目标价位** | ¥{rec.get('target_price', 0):.2f} |
| **止损价位** | ¥{rec.get('stop_loss', 0):.2f} |
| **持有周期** | {rec.get('holding_period', 'N/A')} |

### 操作思路

{rec.get('rationale', '暂无详细说明')}

### 关键条件

**买入条件：**
{self._format_conditions(rec.get('buy_conditions', []))}

**卖出条件：**
{self._format_conditions(rec.get('sell_conditions', []))}

---

"""
    
    def _format_conditions(self, conditions: List[str]) -> str:
        """格式化条件列表"""
        if not conditions:
            return "- 暂无具体条件"
        return "\n".join([f"- {c}" for c in conditions])
    
    def _format_risk_warning(self) -> str:
        """格式化风险提示"""
        return """## ⚠️ 风险提示

1. **市场风险**：股市有风险，投资需谨慎。本报告仅供参考，不构成投资建议。
2. **策略风险**：历史回测表现不代表未来收益，策略可能失效。
3. **执行风险**：实际交易可能受流动性、滑点等因素影响。
4. **信息时效**：本报告基于报告日期前的数据，市场情况可能已发生变化。

**建议投资者：**
- 根据自身风险承受能力决策
- 做好仓位管理和风险控制
- 定期跟踪策略表现，及时调整
- 不要将所有资金投入单一策略

---

*本报告由 AI 投资顾问系统自动生成*
"""
    
    def generate_daily_summary(self, market_data: Dict, portfolio: Dict) -> str:
        """生成每日市场摘要"""
        date = datetime.now().strftime("%Y-%m-%d")
        
        report = f"""# 📊 每日市场摘要

**日期：** {date}

## 市场概览

{market_data.get('overview', '暂无数据')}

## 持仓跟踪

{self._format_portfolio_summary(portfolio)}

## 今日信号

{market_data.get('signals', '暂无交易信号')}

---

*每日摘要由 AI 投资顾问系统自动生成*
"""
        
        return report
    
    def _format_portfolio_summary(self, portfolio: Dict) -> str:
        """格式化持仓摘要"""
        if not portfolio:
            return "当前无持仓"
        
        content = "| 股票代码 | 名称 | 持仓数量 | 成本价 | 当前价 | 盈亏 | 盈亏率 |\n"
        content += "|---------|------|---------|-------|-------|------|--------|\n"
        
        for pos in portfolio.get('positions', []):
            profit = (pos.get('current_price', 0) - pos.get('cost_price', 0)) * pos.get('shares', 0)
            profit_pct = profit / (pos.get('cost_price', 1) * pos.get('shares', 1)) * 100
            content += f"| {pos.get('symbol', '')} | {pos.get('name', '')} | {pos.get('shares', 0)} | {pos.get('cost_price', 0):.2f} | {pos.get('current_price', 0):.2f} | {profit:+,.0f} | {profit_pct:+.2f}% |\n"
        
        content += f"\n**总盈亏：** {portfolio.get('total_profit', 0):+,.0f} ({portfolio.get('total_profit_pct', 0):+.2f}%)"
        
        return content


if __name__ == "__main__":
    # 测试报告生成
    generator = ReportGenerator()
    
    # 示例数据
    stock_analysis = {
        'symbols': [
            {
                'symbol': '000001',
                'name': '平安银行',
                'price': 12.50,
                'reason': '技术面超卖，基本面稳健，符合均值回归策略',
                'target_price': 14.00,
                'stop_loss': 11.50
            }
        ]
    }
    
    recommendation = {
        'action': '买入',
        'position': '10%',
        'buy_range_low': 12.30,
        'buy_range_high': 12.70,
        'target_price': 14.00,
        'stop_loss': 11.50,
        'holding_period': '中线（1-3 个月）',
        'rationale': '该股票目前处于低位，估值合理，技术面出现超卖信号。根据均值回归策略，预期有 12% 的上涨空间。',
        'buy_conditions': ['股价在 12.30-12.70 区间', '成交量放大'],
        'sell_conditions': ['达到目标价 14.00', '跌破止损价 11.50', '持有超过 3 个月']
    }
    
    backtest_results = {
        'total_return_pct': 25.5,
        'annual_return_pct': 30.2,
        'sharpe_ratio': 1.5,
        'max_drawdown_pct': 12.3,
        'win_rate_pct': 65.0,
        'trade_count': 20,
        'evaluation': 'PASSED'
    }
    
    report = generator.generate_investment_report(
        strategy_name="均值回归策略",
        stock_analysis=stock_analysis,
        recommendation=recommendation,
        backtest_results=backtest_results
    )
    
    print("\n报告预览:")
    print(report[:2000] + "...")
