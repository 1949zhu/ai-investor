"""
测试策略自优化功能
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from strategy.generator import StrategyGenerator
from backtest.engine import BacktestEngine
from optimizer.self_optimizer import StrategyOptimizer
from test_full_flow import generate_mock_data, run_simplified_backtest


def test_optimization():
    """测试策略优化流程"""
    print("=" * 60)
    print("策略自优化测试")
    print("=" * 60)
    
    # 初始化
    strategy_gen = StrategyGenerator()
    optimizer = StrategyOptimizer()
    
    # 生成测试数据
    print("\n生成测试数据...")
    test_symbols = ["000001", "000002", "600036"]
    all_data = {}
    for symbol in test_symbols:
        all_data[symbol] = generate_mock_data(symbol, days=252)
    
    # 获取一个策略进行优化
    strategies = strategy_gen.get_all_builtin_strategies()
    target_strategy = strategies[0]  # 均值回归策略
    
    print(f"\n优化目标策略：{target_strategy['name']}")
    
    # 定义简化回测函数
    def quick_backtest(strategy, symbols, start, end):
        from backtest.engine import BacktestEngine
        engine = BacktestEngine()
        engine.reset()
        return run_simplified_backtest(engine, strategy, all_data)
    
    # 执行优化
    best_strategy, history = optimizer.optimize(
        strategy=target_strategy,
        backtest_func=quick_backtest,
        symbols=test_symbols,
        start_date="20250101",
        end_date="20260304",
        max_iterations=3
    )
    
    # 保存优化历史
    optimizer.save_optimization_history(history)
    
    # 输出总结
    print("\n" + "=" * 60)
    print("优化总结")
    print("=" * 60)
    print(f"初始版本：V{target_strategy.get('version', 1)}")
    print(f"最佳版本：V{best_strategy.get('version', 1)}")
    print(f"优化次数：{len(history)}")
    
    if len(history) > 0:
        initial = history[0]['results']
        final_result = history[-1]['results']
        
        print(f"\n改进对比:")
        print(f"  收益率：{initial.get('total_return_pct', 0):.2f}% -> {final_result.get('total_return_pct', 0):.2f}%")
        print(f"  夏普比率：{initial.get('sharpe_ratio', 0):.2f} -> {final_result.get('sharpe_ratio', 0):.2f}")
        print(f"  最大回撤：{initial.get('max_drawdown_pct', 0):.2f}% -> {final_result.get('max_drawdown_pct', 0):.2f}%")
    
    print(f"\n优化备注：{best_strategy.get('optimization_notes', '无')}")
    
    return {
        'best_strategy': best_strategy,
        'history': history
    }


if __name__ == "__main__":
    result = test_optimization()
    print("\n[OK] 自优化测试完成")
