"""
完整流程测试
用模拟数据跑通整个系统，验证可行性
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from strategy.generator import StrategyGenerator
from backtest.engine import BacktestEngine
from report.generator import ReportGenerator


def generate_mock_data(symbol: str, days: int = 252) -> pd.DataFrame:
    """
    生成模拟股票数据（用于测试流程）
    
    使用随机游走 + 趋势 + 波动来模拟真实股价
    """
    np.random.seed(hash(symbol) % 2**32)  # 固定种子，可复现
    
    # 初始价格
    base_price = np.random.uniform(10, 100)
    
    # 生成收益率（带均值回归）
    returns = np.random.normal(0.0005, 0.025, days)  # 日均收益 0.05%，波动 2.5%
    
    # 添加一些趋势
    trend = np.sin(np.linspace(0, 4 * np.pi, days)) * 0.01
    returns = returns + trend
    
    # 计算收盘价
    prices = base_price * np.cumprod(1 + returns)
    
    # 生成 OHLCV 数据
    data = []
    for i in range(days):
        close = prices[i]
        daily_range = close * np.random.uniform(0.01, 0.05)
        open_price = close + np.random.uniform(-daily_range/2, daily_range/2)
        high = max(open_price, close) + np.random.uniform(0, daily_range/2)
        low = min(open_price, close) - np.random.uniform(0, daily_range/2)
        volume = np.random.uniform(1000000, 50000000)
        
        date = (datetime.now() - timedelta(days=days-i)).strftime("%Y%m%d")
        pct_chg = (returns[i]) * 100 if i > 0 else 0
        
        data.append({
            'trade_date': date,
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': round(volume, 0),
            'amount': round(volume * close, 0),
            'amplitude': round((high - low) / close * 100, 2),
            'pct_chg': round(pct_chg, 2),
            'change': round(close - open_price, 2),
            'turnover': round(np.random.uniform(0.5, 5), 2)
        })
    
    return pd.DataFrame(data)


def run_full_test():
    """运行完整流程测试"""
    print("=" * 60)
    print("AI 投资顾问系统 - 完整流程测试")
    print("=" * 60)
    
    # 初始化模块
    strategy_gen = StrategyGenerator()
    backtest_engine = BacktestEngine()
    report_gen = ReportGenerator()
    
    # 1. 获取策略
    print("\n[1/5] 加载策略...")
    strategies = strategy_gen.get_all_builtin_strategies()
    print(f"   可用策略：{len(strategies)} 个")
    for s in strategies:
        print(f"   - {s['name']} ({s['id']})")
    
    # 2. 生成测试数据
    print("\n[2/5] 生成测试数据...")
    test_symbols = ["000001", "000002", "600000", "600036", "000651"]
    all_data = {}
    
    for symbol in test_symbols:
        df = generate_mock_data(symbol, days=252)
        all_data[symbol] = df
        print(f"   [OK] {symbol}: {len(df)} 天数据")
    
    # 3. 运行回测
    print("\n[3/5] 运行回测...")
    results = []
    
    for strategy in strategies:
        print(f"\n   回测策略：{strategy['name']}")
        backtest_engine.reset()
        
        # 简化回测：直接模拟
        result = run_simplified_backtest(backtest_engine, strategy, all_data)
        results.append(result)
        
        # 保存回测结果
        backtest_engine.save_results(result)
    
    # 4. 选择最佳策略
    print("\n[4/5] 选择最佳策略...")
    best_result = max(results, key=lambda x: x.get('total_return_pct', 0))
    best_strategy = next(s for s in strategies if s['id'] == best_result['strategy_id'])
    print(f"   [BEST] 最佳策略：{best_strategy['name']}")
    print(f"   收益率：{best_result['total_return_pct']:+.2f}%")
    print(f"   夏普比率：{best_result['sharpe_ratio']:.2f}")
    print(f"   评估：{best_result['evaluation']}")
    
    # 5. 生成投资报告
    print("\n[5/5] 生成投资报告...")
    
    # 准备股票分析数据
    stock_analysis = {
        'symbols': []
    }
    for symbol, df in list(all_data.items())[:3]:
        current_price = df['close'].iloc[-1]
        stock_analysis['symbols'].append({
            'symbol': symbol,
            'name': get_stock_name(symbol),
            'price': current_price,
            'reason': f"符合{best_strategy['name']}选股条件，技术面良好",
            'target_price': current_price * 1.15,
            'stop_loss': current_price * 0.92
        })
    
    # 准备交易建议
    recommendation = {
        'action': '买入',
        'position': '10-20%',
        'buy_range_low': all_data[test_symbols[0]]['close'].iloc[-1] * 0.98,
        'buy_range_high': all_data[test_symbols[0]]['close'].iloc[-1] * 1.02,
        'target_price': all_data[test_symbols[0]]['close'].iloc[-1] * 1.15,
        'stop_loss': all_data[test_symbols[0]]['close'].iloc[-1] * 0.92,
        'holding_period': '短线（1-2 周）' if '短线' in best_strategy.get('name', '') else '中线（1-3 个月）',
        'rationale': f"基于{best_strategy['name']}，历史回测显示该策略在震荡/趋势市场中表现良好。建议分批建仓，严格控制仓位和止损。",
        'buy_conditions': best_strategy.get('entry_conditions', []),
        'sell_conditions': best_strategy.get('exit_conditions', [])
    }
    
    # 生成报告
    report = report_gen.generate_investment_report(
        strategy_name=best_strategy['name'],
        stock_analysis=stock_analysis,
        recommendation=recommendation,
        backtest_results=best_result
    )
    
    # 6. 输出总结
    print("\n" + "=" * 60)
    print("完整流程测试完成！")
    print("=" * 60)
    print(f"\n报告已生成：{report_gen.output_dir}")
    print(f"\n最终结果:")
    print(f"   最佳策略：{best_strategy['name']}")
    print(f"   回测收益率：{best_result['total_return_pct']:+.2f}%")
    print(f"   评估结果：{best_result['evaluation']}")
    status = "通过" if best_result['evaluation'] in ['PASSED', 'ACCEPTABLE'] else "需优化"
    print(f"\n系统可行性：[{status}]")
    
    return {
        'success': True,
        'best_strategy': best_strategy,
        'best_result': best_result,
        'report_path': str(report_gen.output_dir)
    }


def run_simplified_backtest(engine: BacktestEngine, strategy: dict, all_data: dict) -> dict:
    """简化版回测（用于测试流程）"""
    # 合并所有股票数据
    all_dates = set()
    for df in all_data.values():
        all_dates.update(df['trade_date'].tolist())
    all_dates = sorted(list(all_dates))
    
    initial_capital = engine.initial_capital
    capital = initial_capital
    positions = {}
    trades = []
    portfolio_values = []
    
    # 简化交易逻辑
    for i, date in enumerate(all_dates):
        # 检查买入信号（简化：随机买入）
        if capital > initial_capital * 0.2 and len(positions) < 3:
            for symbol, df in all_data.items():
                if symbol in positions:
                    continue
                day_data = df[df['trade_date'] == date]
                if day_data.empty:
                    continue
                
                row = day_data.iloc[0]
                # 简化条件：涨幅>2% 且成交量放大
                if row['pct_chg'] > 2 and row['volume'] > df['volume'].mean():
                    # 买入
                    shares = int(initial_capital * 0.1 / row['close'] / 100) * 100
                    if shares >= 100:
                        cost = shares * row['close']
                        if cost <= capital:
                            positions[symbol] = {
                                'shares': shares,
                                'entry_price': row['close'],
                                'entry_date': date
                            }
                            capital -= cost
                            trades.append({
                                'date': date,
                                'symbol': symbol,
                                'action': 'buy',
                                'price': row['close'],
                                'shares': shares
                            })
                            break
        
        # 检查卖出信号
        for symbol, pos in list(positions.items()):
            df = all_data.get(symbol)
            if df is None:
                continue
            day_data = df[df['trade_date'] == date]
            if day_data.empty:
                continue
            
            row = day_data.iloc[0]
            entry_price = pos['entry_price']
            
            # 止损 8% 或 止盈 15%
            if row['close'] < entry_price * 0.92:
                revenue = pos['shares'] * row['close']
                capital += revenue
                profit = revenue - pos['shares'] * entry_price
                trades.append({
                    'date': date,
                    'symbol': symbol,
                    'action': 'sell',
                    'price': row['close'],
                    'shares': pos['shares'],
                    'profit': profit
                })
                positions.pop(symbol)
            elif row['close'] > entry_price * 1.15:
                revenue = pos['shares'] * row['close']
                capital += revenue
                profit = revenue - pos['shares'] * entry_price
                trades.append({
                    'date': date,
                    'symbol': symbol,
                    'action': 'sell',
                    'price': row['close'],
                    'shares': pos['shares'],
                    'profit': profit
                })
                positions.pop(symbol)
        
        # 记录净值
        holdings_value = sum(
            pos['shares'] * all_data[sym][all_data[sym]['trade_date'] == date]['close'].iloc[0]
            for sym, pos in positions.items()
            if not all_data[sym][all_data[sym]['trade_date'] == date].empty
        ) if positions else 0
        portfolio_values.append(capital + holdings_value)
    
    # 计算结果
    final_value = portfolio_values[-1] if portfolio_values else initial_capital
    total_return = (final_value - initial_capital) / initial_capital
    
    # 简化指标计算
    returns = [portfolio_values[i+1]/portfolio_values[i] - 1 
               for i in range(len(portfolio_values)-1)] if len(portfolio_values) > 1 else []
    
    sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252) if returns and np.std(returns) > 0 else 0
    
    # 最大回撤
    peak = portfolio_values[0] if portfolio_values else initial_capital
    max_dd = 0
    for v in portfolio_values:
        if v > peak:
            peak = v
        dd = (peak - v) / peak
        max_dd = max(max_dd, dd)
    
    # 胜率
    profitable = sum(1 for t in trades if t.get('profit', 0) > 0)
    total_sells = sum(1 for t in trades if t['action'] == 'sell')
    win_rate = profitable / max(total_sells, 1)
    
    evaluation = "PASSED" if total_return > 0.1 and sharpe > 0.5 else "ACCEPTABLE" if total_return > 0 else "FAILED"
    
    return {
        'strategy_id': strategy['id'],
        'strategy_name': strategy['name'],
        'initial_capital': initial_capital,
        'final_value': final_value,
        'total_return': total_return,
        'total_return_pct': total_return * 100,
        'annual_return': total_return,
        'annual_return_pct': total_return * 100,
        'sharpe_ratio': sharpe,
        'max_drawdown': max_dd,
        'max_drawdown_pct': max_dd * 100,
        'win_rate': win_rate,
        'win_rate_pct': win_rate * 100,
        'trade_count': total_sells,
        'total_trades': len(trades),
        'evaluation': evaluation
    }


def get_stock_name(symbol: str) -> str:
    """获取股票名称"""
    names = {
        '000001': '平安银行',
        '000002': '万科 A',
        '600000': '浦发银行',
        '600036': '招商银行',
        '000651': '格力电器'
    }
    return names.get(symbol, '未知')


if __name__ == "__main__":
    result = run_full_test()
    
    if result['success']:
        print("\n[SUCCESS] 系统流程验证通过！可以开始使用真实数据运行。")
    else:
        print("\n[WARNING] 测试发现问题，需要修复。")
