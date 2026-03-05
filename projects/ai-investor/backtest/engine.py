"""
回测引擎
验证策略在历史数据上的表现
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import sqlite3


class BacktestEngine:
    """
    回测引擎
    
    功能：
    1. 加载历史数据
    2. 模拟交易执行
    3. 计算绩效指标
    4. 生成回测报告
    """
    
    def __init__(self, db_path: str = "storage/ashare.db"):
        self.db_path = Path(db_path)
        self.initial_capital = 1000000  # 初始资金 100 万
        self.capital = self.initial_capital
        self.positions = {}  # 持仓
        self.trades = []  # 交易记录
        self.portfolio_values = []  # 组合净值记录
    
    def load_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """从数据库加载股票数据"""
        conn = sqlite3.connect(self.db_path)
        query = """
            SELECT * FROM daily_quotes 
            WHERE symbol = ? AND trade_date >= ? AND trade_date <= ?
            ORDER BY trade_date
        """
        df = pd.read_sql_query(query, conn, params=[symbol, start_date, end_date])
        conn.close()
        return df
    
    def reset(self):
        """重置回测状态"""
        self.capital = self.initial_capital
        self.positions = {}
        self.trades = []
        self.portfolio_values = []
    
    def run_backtest(self, strategy: Dict, symbols: List[str], 
                     start_date: str, end_date: str) -> Dict:
        """
        运行回测
        
        Args:
            strategy: 策略配置
            symbols: 股票列表
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            回测结果
        """
        self.reset()
        
        print(f"\n开始回测策略：{strategy['name']}")
        print(f"时间范围：{start_date} - {end_date}")
        print(f"股票数量：{len(symbols)}")
        print(f"初始资金：{self.initial_capital:,.0f}")
        
        # 加载所有股票数据
        all_data = {}
        for symbol in symbols:
            df = self.load_data(symbol, start_date, end_date)
            if not df.empty:
                all_data[symbol] = df
        
        if not all_data:
            print("没有可用的数据")
            return self._generate_empty_result(strategy)
        
        # 获取所有交易日期
        all_dates = set()
        for df in all_data.values():
            all_dates.update(df['trade_date'].tolist())
        all_dates = sorted(list(all_dates))
        
        print(f"交易天数：{len(all_dates)}")
        
        # 逐日模拟交易
        for date in all_dates:
            self._simulate_day(date, all_data, strategy)
            self._record_portfolio_value(date)
        
        # 平仓所有持仓
        self._close_all_positions(all_dates[-1] if all_dates else end_date)
        
        # 计算绩效指标
        results = self._calculate_metrics(strategy)
        
        return results
    
    def _simulate_day(self, date: str, all_data: Dict, strategy: Dict):
        """模拟一天的交易"""
        # 检查卖出条件
        for symbol, position in list(self.positions.items()):
            if symbol not in all_data:
                continue
            df = all_data[symbol]
            day_data = df[df['trade_date'] == date]
            if day_data.empty:
                continue
            
            row = day_data.iloc[0]
            if self._check_exit_conditions(symbol, row, position, strategy):
                self._sell(symbol, row['close'], date)
        
        # 检查买入条件
        if self.capital > self.initial_capital * 0.1:  # 剩余资金>10%
            for symbol, df in all_data.items():
                day_data = df[df['trade_date'] == date]
                if day_data.empty:
                    continue
                
                row = day_data.iloc[0]
                if symbol not in self.positions:
                    if self._check_entry_conditions(symbol, row, df, strategy):
                        self._buy(symbol, row['close'], date)
    
    def _check_entry_conditions(self, symbol: str, row: pd.Series, 
                                 df: pd.DataFrame, strategy: Dict) -> bool:
        """检查买入条件"""
        conditions = strategy.get('entry_conditions', [])
        
        # 简化版条件检查（实际应该解析条件表达式）
        close = row.get('close', 0)
        pct_chg = row.get('pct_chg', 0) / 100 if 'pct_chg' in row else 0
        volume = row.get('volume', 0)
        
        # 计算均线
        if len(df) >= 20:
            ma20 = df['close'].rolling(20).mean().iloc[-1]
        else:
            ma20 = close
        
        # 简单实现几个条件
        for condition in conditions:
            if "close < MA20 * 0.95" in condition:
                if close >= ma20 * 0.95:
                    return False
            if "pct_chg > 0.05" in condition:
                if pct_chg <= 0.05:
                    return False
        
        return True
    
    def _check_exit_conditions(self, symbol: str, row: pd.Series, 
                                position: Dict, strategy: Dict) -> bool:
        """检查卖出条件"""
        close = row.get('close', 0)
        entry_price = position['entry_price']
        
        # 止损
        stop_loss = strategy.get('risk_management', {}).get('stop_loss', 0.1)
        if close < entry_price * (1 - stop_loss):
            print(f"  [{symbol}] 止损卖出：{entry_price:.2f} -> {close:.2f}")
            return True
        
        # 止盈
        take_profit = strategy.get('risk_management', {}).get('take_profit', 0.2)
        if close > entry_price * (1 + take_profit):
            print(f"  [{symbol}] 止盈卖出：{entry_price:.2f} -> {close:.2f}")
            return True
        
        return False
    
    def _buy(self, symbol: str, price: float, date: str):
        """买入"""
        # 计算可买数量（10% 仓位）
        position_value = self.initial_capital * 0.1
        shares = int(position_value / price / 100) * 100  # 100 股的整数倍
        
        if shares < 100:
            return
        
        cost = shares * price
        if cost > self.capital:
            shares = int(self.capital / price / 100) * 100
            cost = shares * price
        
        if shares < 100:
            return
        
        self.positions[symbol] = {
            'shares': shares,
            'entry_price': price,
            'entry_date': date,
            'cost': cost
        }
        self.capital -= cost
        
        self.trades.append({
            'date': date,
            'symbol': symbol,
            'action': 'buy',
            'price': price,
            'shares': shares,
            'amount': cost
        })
        
        print(f"  [{symbol}] 买入：{shares}股 @ {price:.2f}, 花费：{cost:,.0f}")
    
    def _sell(self, symbol: str, price: float, date: str):
        """卖出"""
        if symbol not in self.positions:
            return
        
        position = self.positions[symbol]
        shares = position['shares']
        revenue = shares * price
        
        profit = revenue - position['cost']
        profit_pct = profit / position['cost'] * 100
        
        self.positions.pop(symbol)
        self.capital += revenue
        
        self.trades.append({
            'date': date,
            'symbol': symbol,
            'action': 'sell',
            'price': price,
            'shares': shares,
            'amount': revenue,
            'profit': profit
        })
        
        print(f"  [{symbol}] 卖出：{shares}股 @ {price:.2f}, 收入：{revenue:,.0f}, 盈亏：{profit_pct:+.1f}%")
    
    def _close_all_positions(self, date: str):
        """平仓所有持仓"""
        for symbol in list(self.positions.keys()):
            # 用最新价格卖出（简化处理）
            self._sell(symbol, self.positions[symbol]['entry_price'], date)
    
    def _record_portfolio_value(self, date: str):
        """记录组合净值"""
        # 计算持仓市值
        holdings_value = 0
        # 简化处理，用买入价估算
        for pos in self.positions.values():
            holdings_value += pos['shares'] * pos['entry_price']
        
        total_value = self.capital + holdings_value
        self.portfolio_values.append({
            'date': date,
            'value': total_value,
            'capital': self.capital,
            'holdings': holdings_value
        })
    
    def _calculate_metrics(self, strategy: Dict) -> Dict:
        """计算绩效指标"""
        if not self.portfolio_values:
            return self._generate_empty_result(strategy)
        
        values = [pv['value'] for pv in self.portfolio_values]
        final_value = values[-1]
        
        # 总收益率
        total_return = (final_value - self.initial_capital) / self.initial_capital
        
        # 年化收益率（简化）
        days = len(self.portfolio_values)
        annual_return = (1 + total_return) ** (252 / max(days, 1)) - 1
        
        # 最大回撤
        peak = values[0]
        max_drawdown = 0
        for value in values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_drawdown = max(max_drawdown, drawdown)
        
        # 夏普比率（简化）
        returns = [values[i+1]/values[i] - 1 for i in range(len(values)-1)]
        if returns and np.std(returns) > 0:
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252)
        else:
            sharpe_ratio = 0
        
        # 胜率
        profitable_trades = sum(1 for t in self.trades if t.get('profit', 0) > 0)
        total_trades = len([t for t in self.trades if t['action'] == 'sell'])
        win_rate = profitable_trades / max(total_trades, 1)
        
        results = {
            'strategy_id': strategy.get('id', 'unknown'),
            'strategy_name': strategy.get('name', 'unknown'),
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'annual_return': annual_return,
            'annual_return_pct': annual_return * 100,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown * 100,
            'win_rate': win_rate,
            'win_rate_pct': win_rate * 100,
            'trade_count': total_trades,
            'total_trades': len(self.trades),
            'evaluation': self._evaluate_strategy(total_return, sharpe_ratio, max_drawdown)
        }
        
        self._print_results(results)
        
        return results
    
    def _evaluate_strategy(self, total_return: float, sharpe_ratio: float, 
                           max_drawdown: float) -> str:
        """评估策略是否达标"""
        # 简单评估标准
        if total_return > 0.2 and sharpe_ratio > 1.0 and max_drawdown < 0.2:
            return "PASSED"  # 优秀
        elif total_return > 0.1 and sharpe_ratio > 0.5 and max_drawdown < 0.3:
            return "ACCEPTABLE"  # 可接受
        else:
            return "FAILED"  # 需要优化
    
    def _generate_empty_result(self, strategy: Dict) -> Dict:
        """生成空结果"""
        return {
            'strategy_id': strategy.get('id', 'unknown'),
            'strategy_name': strategy.get('name', 'unknown'),
            'initial_capital': self.initial_capital,
            'final_value': self.initial_capital,
            'total_return': 0,
            'total_return_pct': 0,
            'annual_return': 0,
            'annual_return_pct': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'max_drawdown_pct': 0,
            'win_rate': 0,
            'win_rate_pct': 0,
            'trade_count': 0,
            'total_trades': 0,
            'evaluation': "NO_DATA"
        }
    
    def _print_results(self, results: Dict):
        """打印回测结果"""
        print("\n" + "=" * 50)
        print(f"策略：{results['strategy_name']}")
        print("=" * 50)
        print(f"初始资金：{results['initial_capital']:,.0f}")
        print(f"最终价值：{results['final_value']:,.0f}")
        print(f"总收益率：{results['total_return_pct']:+.2f}%")
        print(f"年化收益：{results['annual_return_pct']:+.2f}%")
        print(f"夏普比率：{results['sharpe_ratio']:.2f}")
        print(f"最大回撤：{results['max_drawdown_pct']:.2f}%")
        print(f"胜率：{results['win_rate_pct']:.1f}%")
        print(f"交易次数：{results['trade_count']}")
        print(f"评估结果：{results['evaluation']}")
        print("=" * 50)
    
    def save_results(self, results: Dict, output_path: str = "storage/backtest_results.json"):
        """保存回测结果"""
        import json
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        results_list = []
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                results_list = json.load(f)
        
        results_list.append(results)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(results_list, f, ensure_ascii=False, indent=2)
        
        print(f"回测结果已保存：{output_path}")


if __name__ == "__main__":
    # 测试回测引擎
    engine = BacktestEngine()
    
    # 获取内置策略
    from strategy.generator import StrategyGenerator
    generator = StrategyGenerator()
    strategies = generator.get_all_builtin_strategies()
    
    # 用单只股票测试
    test_symbols = ["000001"]
    start_date = "20240101"
    end_date = "20241231"
    
    for strategy in strategies[:1]:  # 只测试第一个策略
        results = engine.run_backtest(strategy, test_symbols, start_date, end_date)
        engine.save_results(results)
