"""
策略自优化模块

核心功能：
1. 分析回测结果，识别策略弱点
2. 自动调整策略参数
3. 重新回测验证
4. 迭代优化直到达到预期效果
"""

import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import copy


class StrategyOptimizer:
    """
    策略自优化器
    
    优化流程：
    1. 评估当前策略表现
    2. 识别问题（收益低/回撤大/胜率低）
    3. 调整参数
    4. 重新回测
    5. 对比结果，保留改进
    6. 迭代直到达标或达到最大迭代次数
    """
    
    def __init__(self):
        self.optimization_history = []
        self.target_metrics = {
            'min_total_return': 0.15,      # 目标总收益 15%
            'min_sharpe': 0.8,             # 目标夏普比率 0.8
            'max_drawdown': 0.20,          # 最大回撤不超过 20%
            'min_win_rate': 0.45           # 目标胜率 45%
        }
    
    def evaluate_strategy(self, results: Dict) -> Dict:
        """
        评估策略表现，识别弱点
        
        Returns:
            评估报告，包含问题和改进建议
        """
        evaluation = {
            'overall_score': 0,
            'issues': [],
            'suggestions': [],
            'metrics_analysis': {}
        }
        
        # 分析各项指标
        total_return = results.get('total_return', 0)
        sharpe = results.get('sharpe_ratio', 0)
        max_dd = results.get('max_drawdown', 0)
        win_rate = results.get('win_rate', 0)
        
        # 收益分析
        if total_return < self.target_metrics['min_total_return']:
            evaluation['issues'].append({
                'type': 'low_return',
                'severity': 'high',
                'current': total_return,
                'target': self.target_metrics['min_total_return'],
                'description': f'收益率偏低 ({total_return*100:.1f}% < {self.target_metrics["min_total_return"]*100:.0f}%)'
            })
            evaluation['suggestions'].append('考虑放宽买入条件或提高止盈比例')
        else:
            evaluation['metrics_analysis']['return'] = 'good'
        
        # 夏普比率分析
        if sharpe < self.target_metrics['min_sharpe']:
            evaluation['issues'].append({
                'type': 'low_sharpe',
                'severity': 'medium',
                'current': sharpe,
                'target': self.target_metrics['min_sharpe'],
                'description': f'风险收益比偏低 (夏普 {sharpe:.2f} < {self.target_metrics["min_sharpe"]:.1f})'
            })
            evaluation['suggestions'].append('考虑优化止损策略或降低仓位')
        else:
            evaluation['metrics_analysis']['sharpe'] = 'good'
        
        # 回撤分析
        if max_dd > self.target_metrics['max_drawdown']:
            evaluation['issues'].append({
                'type': 'high_drawdown',
                'severity': 'high',
                'current': max_dd,
                'target': self.target_metrics['max_drawdown'],
                'description': f'回撤过大 ({max_dd*100:.1f}% > {self.target_metrics["max_drawdown"]*100:.0f}%)'
            })
            evaluation['suggestions'].append('需要加强止损控制，考虑降低单笔仓位')
        else:
            evaluation['metrics_analysis']['drawdown'] = 'good'
        
        # 胜率分析
        if win_rate < self.target_metrics['min_win_rate']:
            evaluation['issues'].append({
                'type': 'low_win_rate',
                'severity': 'medium',
                'current': win_rate,
                'target': self.target_metrics['min_win_rate'],
                'description': f'胜率偏低 ({win_rate*100:.1f}% < {self.target_metrics["min_win_rate"]*100:.0f}%)'
            })
            evaluation['suggestions'].append('考虑优化选股条件，提高信号质量')
        else:
            evaluation['metrics_analysis']['win_rate'] = 'good'
        
        # 计算综合得分
        scores = []
        if total_return >= self.target_metrics['min_total_return']:
            scores.append(1.0)
        else:
            scores.append(total_return / self.target_metrics['min_total_return'])
        
        if sharpe >= self.target_metrics['min_sharpe']:
            scores.append(1.0)
        else:
            scores.append(sharpe / self.target_metrics['min_sharpe'])
        
        if max_dd <= self.target_metrics['max_drawdown']:
            scores.append(1.0)
        else:
            scores.append(self.target_metrics['max_drawdown'] / max_dd)
        
        if win_rate >= self.target_metrics['min_win_rate']:
            scores.append(1.0)
        else:
            scores.append(win_rate / self.target_metrics['min_win_rate'])
        
        evaluation['overall_score'] = sum(scores) / len(scores)
        
        return evaluation
    
    def generate_optimized_strategy(self, strategy: Dict, evaluation: Dict) -> Dict:
        """
        根据评估结果生成优化后的策略
        
        Args:
            strategy: 原策略
            evaluation: 评估报告
            
        Returns:
            优化后的策略
        """
        optimized = copy.deepcopy(strategy)
        params = optimized.get('parameters', {})
        risk_mgmt = optimized.get('risk_management', {})
        
        issues = [i['type'] for i in evaluation.get('issues', [])]
        
        # 针对收益低：放宽买入条件，提高止盈
        if 'low_return' in issues:
            if 'entry_threshold' in params:
                params['entry_threshold'] = params['entry_threshold'] * 0.8  # 降低买入阈值 20%
            if 'take_profit' in risk_mgmt:
                risk_mgmt['take_profit'] = risk_mgmt['take_profit'] * 1.2  # 提高止盈 20%
            
            optimized['optimization_notes'] = '放宽买入条件，提高止盈目标'
        
        # 针对夏普比率低：优化仓位管理
        if 'low_sharpe' in issues:
            if 'position_sizing' in optimized:
                if 'percent' in optimized['position_sizing']:
                    optimized['position_sizing']['percent'] = optimized['position_sizing']['percent'] * 0.8
            risk_mgmt['max_position'] = risk_mgmt.get('max_position', 0.3) * 0.9
            
            optimized['optimization_notes'] = (optimized.get('optimization_notes', '') + 
                                               '; 降低仓位，优化风险收益比')
        
        # 针对回撤大：加强止损
        if 'high_drawdown' in issues:
            if 'stop_loss' in risk_mgmt:
                risk_mgmt['stop_loss'] = risk_mgmt['stop_loss'] * 0.8  # 收紧止损 20%
            if 'max_position' in risk_mgmt:
                risk_mgmt['max_position'] = risk_mgmt['max_position'] * 0.85
            
            optimized['optimization_notes'] = (optimized.get('optimization_notes', '') + 
                                               '; 收紧止损，降低仓位')
        
        # 针对胜率低：优化选股条件
        if 'low_win_rate' in issues:
            if 'ma_period' in params:
                params['ma_period'] = int(params['ma_period'] * 1.2)  # 延长均线周期
            if 'volume_multiplier' in params:
                params['volume_multiplier'] = params['volume_multiplier'] * 1.2
            
            optimized['optimization_notes'] = (optimized.get('optimization_notes', '') + 
                                               '; 优化选股条件，提高信号质量')
        
        optimized['parameters'] = params
        optimized['risk_management'] = risk_mgmt
        optimized['version'] = optimized.get('version', 1) + 1
        optimized['status'] = 'pending_backtest'
        
        return optimized
    
    def optimize(self, strategy: Dict, backtest_func, 
                 symbols: List[str], start_date: str, end_date: str,
                 max_iterations: int = 5) -> Tuple[Dict, List[Dict]]:
        """
        执行策略优化
        
        Args:
            strategy: 初始策略
            backtest_func: 回测函数
            symbols: 股票列表
            start_date: 开始日期
            end_date: 结束日期
            max_iterations: 最大迭代次数
            
        Returns:
            (最佳策略，优化历史)
        """
        print(f"\n开始优化策略：{strategy['name']}")
        print(f"目标：收益>{self.target_metrics['min_total_return']*100:.0f}%, "
              f"夏普>{self.target_metrics['min_sharpe']}, "
              f"回撤<{self.target_metrics['max_drawdown']*100:.0f}%")
        
        current_strategy = strategy
        best_strategy = strategy
        best_score = 0
        history = []
        
        for iteration in range(max_iterations):
            print(f"\n[迭代 {iteration+1}/{max_iterations}]")
            
            # 运行回测
            print("  运行回测...")
            results = backtest_func(current_strategy, symbols, start_date, end_date)
            
            # 评估
            print("  评估表现...")
            evaluation = self.evaluate_strategy(results)
            
            # 记录历史
            iteration_record = {
                'iteration': iteration + 1,
                'strategy': current_strategy,
                'results': results,
                'evaluation': evaluation,
                'timestamp': datetime.now().isoformat()
            }
            history.append(iteration_record)
            
            # 计算得分
            score = evaluation['overall_score']
            print(f"  综合得分：{score:.2f}")
            print(f"  收益率：{results.get('total_return_pct', 0):+.2f}%")
            print(f"  夏普比率：{results.get('sharpe_ratio', 0):.2f}")
            print(f"  最大回撤：{results.get('max_drawdown_pct', 0):.2f}%")
            print(f"  胜率：{results.get('win_rate_pct', 0):.1f}%")
            
            # 检查是否达标
            if score >= 1.0:
                print(f"\n[达标] 策略已达到预期效果！")
                best_strategy = current_strategy
                best_score = score
                break
            
            # 更新最佳策略
            if score > best_score:
                best_strategy = current_strategy
                best_score = score
            
            # 生成优化版本
            print("  生成优化版本...")
            next_strategy = self.generate_optimized_strategy(current_strategy, evaluation)
            
            # 检查是否有实质改进
            if next_strategy == current_strategy:
                print("  无法进一步优化，停止迭代")
                break
            
            current_strategy = next_strategy
        
        # 总结
        print(f"\n优化完成！")
        print(f"  最佳版本：V{best_strategy.get('version', 1)}")
        print(f"  最佳得分：{best_score:.2f}")
        print(f"  总迭代：{len(history)} 次")
        
        return best_strategy, history
    
    def save_optimization_history(self, history: List[Dict], 
                                   output_path: str = "storage/optimization_history.json"):
        """保存优化历史"""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        existing = []
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        
        existing.extend(history)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        
        print(f"优化历史已保存：{output_path}")
    
    def learn_from_history(self) -> Dict:
        """
        从历史优化中学习规律
        
        Returns:
            学习到的经验规则
        """
        path = Path("storage/optimization_history.json")
        if not path.exists():
            return {'rules': [], 'insights': []}
        
        with open(path, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        # 分析成功的优化模式
        successful = [h for h in history if h['evaluation']['overall_score'] >= 1.0]
        
        insights = {
            'successful_patterns': [],
            'failed_patterns': [],
            'recommendations': []
        }
        
        # 简单分析：统计哪些参数调整最常带来改进
        # TODO: 实现更复杂的模式识别
        
        return insights


if __name__ == "__main__":
    # 测试优化器
    optimizer = StrategyOptimizer()
    
    # 创建一个测试策略
    test_strategy = {
        'id': 'TEST001',
        'name': '测试策略',
        'parameters': {
            'ma_period': 20,
            'entry_threshold': 0.05,
            'exit_threshold': 0.05
        },
        'risk_management': {
            'stop_loss': 0.10,
            'take_profit': 0.15,
            'max_position': 0.2
        },
        'version': 1
    }
    
    # 模拟回测结果（逐步改进）
    mock_results = [
        {'total_return': 0.05, 'sharpe_ratio': 0.3, 'max_drawdown': 0.25, 'win_rate': 0.35},
        {'total_return': 0.08, 'sharpe_ratio': 0.5, 'max_drawdown': 0.20, 'win_rate': 0.40},
        {'total_return': 0.12, 'sharpe_ratio': 0.7, 'max_drawdown': 0.18, 'win_rate': 0.45},
        {'total_return': 0.18, 'sharpe_ratio': 0.9, 'max_drawdown': 0.15, 'win_rate': 0.50},
    ]
    
    print("测试策略优化器...")
    
    for i, results in enumerate(mock_results):
        print(f"\n[版本 {i+1}]")
        eval_result = optimizer.evaluate_strategy(results)
        print(f"综合得分：{eval_result['overall_score']:.2f}")
        print(f"问题：{len(eval_result['issues'])} 个")
        for issue in eval_result['issues']:
            print(f"  - {issue['description']}")
        
        if eval_result['overall_score'] >= 1.0:
            print("策略已达标！")
            break
