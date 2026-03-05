"""
LLM 策略自优化器

使用 AI 分析策略表现，自动提出改进建议
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_service import get_llm_service
from llm_service.config import LLMConfig


class LLMOptimizer:
    """
    LLM 策略优化器
    
    核心功能：
    1. 分析失败策略原因
    2. 提出具体改进建议
    3. 生成优化后策略版本
    4. 追踪优化历史
    """
    
    def __init__(self, llm_service=None):
        if llm_service:
            self.llm = llm_service
        else:
            config = LLMConfig.get_service_config()
            self.llm = get_llm_service(**config)
        
        self.optimization_history = Path(__file__).parent.parent / "storage" / "optimization_history"
        self.optimization_history.mkdir(parents=True, exist_ok=True)
    
    def analyze_failure(self, strategy: Dict, backtest_result: Dict) -> Dict:
        """
        分析策略失败原因
        
        Args:
            strategy: 策略配置
            backtest_result: 回测结果
            
        Returns:
            失败分析报告
        """
        evaluation = backtest_result.get('evaluation', 'UNKNOWN')
        
        prompt = f"""请深入分析以下策略的失败原因。

【策略信息】
名称：{strategy.get('name', '未知')}
逻辑：{strategy.get('logic', '')}
买入条件：{json.dumps(strategy.get('entry_conditions', []), ensure_ascii=False)}
卖出条件：{json.dumps(strategy.get('exit_conditions', []), ensure_ascii=False)}
参数：{json.dumps(strategy.get('parameters', {}), ensure_ascii=False)}

【回测结果】
总收益：{backtest_result.get('total_return_pct', 0):.2f}%
年化：{backtest_result.get('annual_return_pct', 0):.2f}%
夏普：{backtest_result.get('sharpe_ratio', 0):.2f}
最大回撤：{backtest_result.get('max_drawdown_pct', 0):.2f}%
胜率：{backtest_result.get('win_rate_pct', 0):.1f}%
交易次数：{backtest_result.get('trade_count', 0)}
评估：{evaluation}

请深度分析：
1. 策略逻辑本身是否有缺陷？
2. 参数设置是否合理？
3. 买入/卖出时机是否有问题？
4. 风险控制是否充分？
5. 是否过拟合或欠拟合？
6. 市场环境是否适合该策略？

输出 JSON 格式：
{{
    "root_causes": [
        {{
            "category": "逻辑/参数/风控/其他",
            "issue": "具体问题描述",
            "severity": "high/medium/low",
            "evidence": "支持证据"
        }}
    ],
    "primary_failure_reason": "最主要失败原因",
    "market_mismatch": "市场不匹配说明",
    "improvement_priority": ["优先改进 1", "优先改进 2"],
    "recommendation": "继续优化/放弃策略"
}}"""
        
        print("🧠 LLM 正在分析失败原因...")
        analysis = self.llm.generate_json(prompt)
        
        analysis['strategy_id'] = strategy.get('id', 'unknown')
        analysis['analysis_date'] = datetime.now().isoformat()
        
        # 保存分析
        self._save_analysis(analysis)
        
        return analysis
    
    def suggest_improvements(self, strategy: Dict, failure_analysis: Dict) -> Dict:
        """
        基于失败分析提出改进建议
        
        Args:
            strategy: 原策略
            failure_analysis: 失败分析结果
            
        Returns:
            改进后的策略
        """
        prompt = f"""基于以下失败分析，请提出具体的策略改进方案。

【原策略】
{json.dumps(strategy, ensure_ascii=False, indent=2)}

【失败分析】
主要原因：{failure_analysis.get('primary_failure_reason', '')}
根本原因：
{json.dumps(failure_analysis.get('root_causes', []), ensure_ascii=False, indent=2)}
改进优先级：{failure_analysis.get('improvement_priority', [])}

请提出具体的改进方案：
1. 如何调整策略逻辑？
2. 如何优化参数？
3. 如何改进买入/卖出条件？
4. 如何加强风险控制？
5. 是否需要增加过滤条件？

输出 JSON 格式：
{{
    "revised_strategy": {{
        "name": "改进版策略名称",
        "logic": "改进后的逻辑",
        "entry_conditions": [...],
        "exit_conditions": [...],
        "parameters": {{}},
        "risk_management": {{}}
    }},
    "changes_made": [
        {{
            "change": "改动描述",
            "reason": "改动原因",
            "expected_impact": "预期效果"
        }}
    ],
    "hypothesis": "改进假设",
    "validation_plan": "验证计划"
}}"""
        
        print("🧠 LLM 正在生成改进方案...")
        improvement = self.llm.generate_json(prompt)
        
        # 补充元数据
        improvement['version'] = strategy.get('version', 1) + 1
        improvement['previous_version'] = strategy.get('id')
        improvement['improved_at'] = datetime.now().isoformat()
        
        # 保存改进版本
        self._save_improvement(improvement)
        
        return improvement
    
    def optimize_parameters(self, strategy: Dict, backtest_history: List[Dict]) -> Dict:
        """
        基于历史回测优化参数
        
        Args:
            strategy: 策略配置
            backtest_history: 多次回测历史
            
        Returns:
            优化后的参数配置
        """
        prompt = f"""请基于以下回测历史，优化策略参数。

【原策略参数】
{json.dumps(strategy.get('parameters', {}), ensure_ascii=False, indent=2)}

【回测历史】
{json.dumps(backtest_history[-5:], ensure_ascii=False, indent=2)}
（显示最近 5 次回测）

请分析：
1. 哪些参数对结果影响最大？
2. 参数与收益的关系？
3. 最优参数区间是什么？
4. 是否存在过拟合风险？

输出 JSON 格式：
{{
    "optimized_parameters": {{}},
    "parameter_sensitivity": [
        {{"parameter": "参数名", "sensitivity": "high/medium/low", "optimal_range": "范围"}}
    ],
    "confidence": 0.8,
    "notes": "参数优化说明"
}}"""
        
        print("🧠 LLM 正在优化参数...")
        return self.llm.generate_json(prompt)
    
    def compare_strategies(self, strategies: List[Dict], backtests: List[Dict]) -> Dict:
        """
        对比多个策略
        
        Args:
            strategies: 策略列表
            backtests: 对应的回测结果
            
        Returns:
            对比分析报告
        """
        prompt = f"""请对比分析以下多个策略的表现。

【策略及回测】
{json.dumps([
    {"strategy": s, "backtest": b} 
    for s, b in zip(strategies, backtests)
], ensure_ascii=False, indent=2)}

请分析：
1. 哪个策略综合表现最好？为什么？
2. 各策略的优势和劣势？
3. 策略之间的相关性如何？
4. 是否适合组合使用？
5. 推荐哪个策略用于实盘？

输出 JSON 格式：
{{
    "best_strategy": "最佳策略 ID",
    "ranking": [
        {{"strategy": "策略名", "score": 85, "reason": "理由"}}
    ],
    "correlation_analysis": "相关性分析",
    "portfolio_suggestion": "组合建议",
    "final_recommendation": "最终推荐"
}}"""
        
        print("🧠 LLM 正在对比策略...")
        return self.llm.generate_json(prompt)
    
    def generate_optimization_report(self, optimization_history: List[Dict]) -> str:
        """
        生成优化报告
        
        Args:
            optimization_history: 优化历史
            
        Returns:
            优化报告文本
        """
        prompt = f"""请生成策略优化进度报告。

【优化历史】
{json.dumps(optimization_history[-10:], ensure_ascii=False, indent=2)}

请总结：
1. 优化迭代次数
2. 主要改进点
3. 性能提升幅度
4. 当前状态
5. 下一步计划

输出 Markdown 格式报告。"""
        
        print("🧠 LLM 正在生成优化报告...")
        return self.llm.generate(prompt)
    
    def _save_analysis(self, analysis: Dict):
        """保存分析报告"""
        file_path = self.optimization_history / f"analysis_{analysis.get('strategy_id', 'unknown')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    def _save_improvement(self, improvement: Dict):
        """保存改进版本"""
        strategy_id = improvement.get('revised_strategy', {}).get('name', 'unknown').replace(' ', '_')
        file_path = self.optimization_history / f"improvement_{strategy_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(improvement, f, ensure_ascii=False, indent=2)
    
    def get_optimization_history(self, strategy_id: str = None) -> List[Dict]:
        """获取优化历史"""
        results = []
        for file in self.optimization_history.glob("*.json"):
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if strategy_id is None or data.get('strategy_id') == strategy_id:
                    results.append(data)
        return sorted(results, key=lambda x: x.get('analysis_date', ''), reverse=True)


if __name__ == "__main__":
    # 测试自优化
    print("=" * 60)
    print("LLM 自优化器测试")
    print("=" * 60)
    
    optimizer = LLMOptimizer()
    
    # 模拟失败策略
    strategy = {
        "id": "MOM001",
        "name": "动量突破策略",
        "logic": "突破 20 日高点时买入",
        "entry_conditions": ["close > highest_high(20)", "volume > MA_volume * 2"],
        "exit_conditions": ["close < MA10", "close < entry_price * 0.90"],
        "parameters": {"lookback_period": 20, "volume_multiplier": 2}
    }
    
    backtest_result = {
        "total_return_pct": 6.20,
        "annual_return_pct": 5.96,
        "sharpe_ratio": 0.53,
        "max_drawdown_pct": 4.93,
        "win_rate_pct": 33.3,
        "trade_count": 9,
        "evaluation": "FAILED"
    }
    
    print("\n分析失败原因...\n")
    analysis = optimizer.analyze_failure(strategy, backtest_result)
    
    print("\n" + "=" * 60)
    print("失败分析结果:")
    print("=" * 60)
    print(f"主要原因：{analysis.get('primary_failure_reason', 'N/A')}")
    print(f"根本原因：{analysis.get('root_causes', [])}")
    print(f"改进优先级：{analysis.get('improvement_priority', [])}")
    print(f"建议：{analysis.get('recommendation', 'N/A')}")
