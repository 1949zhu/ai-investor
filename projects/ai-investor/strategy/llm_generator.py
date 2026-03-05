"""
LLM 策略生成器

使用 AI 发现市场规律，生成可验证的交易策略
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from llm_service import get_llm_service
from llm_service.config import LLMConfig


class LLMStrategyGenerator:
    """
    LLM 策略生成器
    
    核心流程：
    1. 分析市场数据特征
    2. LLM 发现潜在规律
    3. 生成结构化策略
    4. 输出可回测验证的策略
    """
    
    def __init__(self, llm_service=None):
        """
        初始化
        
        Args:
            llm_service: LLM 服务实例（不传则使用默认配置）
        """
        if llm_service:
            self.llm = llm_service
        else:
            config = LLMConfig.get_service_config()
            self.llm = get_llm_service(**config)
        
        self.strategy_storage = Path(__file__).parent.parent / "storage" / "llm_strategies"
        self.strategy_storage.mkdir(parents=True, exist_ok=True)
    
    def generate_strategy(self, market_data: Dict, context: str = "") -> Dict:
        """
        生成交易策略
        
        Args:
            market_data: 市场数据（统计特征）
            context: 额外上下文
            
        Returns:
            策略配置（可回测验证）
        """
        prompt = self._build_strategy_prompt(market_data, context)
        
        print("🧠 LLM 正在分析市场规律...")
        strategy = self.llm.generate_json(prompt, schema=self._get_strategy_schema())
        
        # 验证和补充策略
        strategy = self._validate_strategy(strategy)
        
        # 保存策略
        self._save_strategy(strategy)
        
        return strategy
    
    def analyze_and_improve(self, strategy: Dict, backtest_result: Dict) -> Dict:
        """
        分析回测结果，提出改进建议
        
        Args:
            strategy: 原策略
            backtest_result: 回测结果
            
        Returns:
            改进后的策略
        """
        prompt = f"""请分析以下策略的回测结果，提出改进建议。

【原策略】
名称：{strategy.get('name', '未知')}
逻辑：{strategy.get('logic', '')}
买入条件：{strategy.get('entry_conditions', [])}
卖出条件：{strategy.get('exit_conditions', [])}

【回测结果】
总收益率：{backtest_result.get('total_return_pct', 0):.2f}%
年化收益：{backtest_result.get('annual_return_pct', 0):.2f}%
夏普比率：{backtest_result.get('sharpe_ratio', 0):.2f}
最大回撤：{backtest_result.get('max_drawdown_pct', 0):.2f}%
胜率：{backtest_result.get('win_rate_pct', 0):.1f}%
交易次数：{backtest_result.get('trade_count', 0)}
评估结果：{backtest_result.get('evaluation', 'UNKNOWN')}

请分析：
1. 策略成功的关键因素是什么？
2. 失败的主要原因是什么？
3. 如何改进策略参数或逻辑？
4. 具体的改进建议（可操作的）

请输出 JSON 格式：
{{
    "analysis": {{
        "success_factors": [...],
        "failure_reasons": [...],
        "improvement_direction": "..."
    }},
    "revised_parameters": {{
        "parameter_name": new_value
    }},
    "revised_conditions": {{
        "entry_conditions": [...],
        "exit_conditions": [...]
    }}
}}"""
        
        print("🧠 LLM 正在分析策略表现...")
        improvement = self.llm.generate_json(prompt)
        
        # 应用改进
        improved_strategy = self._apply_improvements(strategy, improvement)
        
        return improved_strategy
    
    def discover_patterns(self, stock_stats: List[Dict]) -> List[Dict]:
        """
        从股票统计数据中发现模式
        
        Args:
            stock_stats: 多只股票的统计特征
            
        Returns:
            发现的模式列表
        """
        prompt = f"""请分析以下股票数据，发现潜在的交易模式。

【股票统计数据】
{json.dumps(stock_stats[:10], ensure_ascii=False, indent=2)}
（共{len(stock_stats)}只股票，显示前 10 只）

请找出：
1. 高收益股票的共同特征
2. 可量化的买入信号
3. 可量化的卖出信号
4. 风险控制建议

输出 JSON 格式：
{{
    "patterns": [
        {{
            "name": "模式名称",
            "description": "模式描述",
            "characteristics": ["特征 1", "特征 2"],
            "entry_signal": "买入信号",
            "exit_signal": "卖出信号",
            "confidence": 0.8
        }}
    ],
    "summary": "总体发现"
}}"""
        
        print("🧠 LLM 正在发现市场模式...")
        result = self.llm.generate_json(prompt)
        
        return result.get('patterns', [])
    
    def _build_strategy_prompt(self, market_data: Dict, context: str) -> str:
        """构建策略生成提示词"""
        
        return f"""你是一个专业的量化交易策略师。请根据以下市场数据，设计一个可执行的投资策略。

【市场环境】
{context if context else "当前 A 股市场，适合短线和中线交易"}

【市场数据特征】
{json.dumps(market_data, ensure_ascii=False, indent=2) if market_data else "暂无具体数据，请基于一般市场规律"}

【策略要求】
1. 策略逻辑清晰，可解释
2. 买入/卖出条件可量化
3. 有明确的风险控制
4. 适合 A 股市场特性

请输出一个完整的策略，包含：
- 策略名称（简洁描述性）
- 策略描述（一句话说明）
- 核心逻辑（详细解释）
- 买入条件（可量化的技术指标）
- 卖出条件（止盈/止损）
- 仓位管理规则
- 风险控制参数
- 适用市场类型

输出格式（严格 JSON）：
{{
    "name": "策略名称",
    "description": "一句话描述",
    "logic": "详细逻辑说明",
    "entry_conditions": ["条件 1", "条件 2"],
    "exit_conditions": ["条件 1", "条件 2"],
    "position_sizing": {{
        "method": "fixed_percent",
        "percent": 0.1
    }},
    "risk_management": {{
        "stop_loss": 0.08,
        "take_profit": 0.15,
        "max_position": 0.2
    }},
    "parameters": {{
        "indicator1": value1,
        "indicator2": value2
    }},
    "applicable_market": "A 股",
    "trading_style": "短线/中线"
}}"""
    
    def _get_strategy_schema(self) -> dict:
        """策略 JSON Schema"""
        return {
            "type": "object",
            "required": ["name", "description", "logic", "entry_conditions", "exit_conditions"],
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "logic": {"type": "string"},
                "entry_conditions": {"type": "array", "items": {"type": "string"}},
                "exit_conditions": {"type": "array", "items": {"type": "string"}},
                "position_sizing": {"type": "object"},
                "risk_management": {"type": "object"},
                "parameters": {"type": "object"}
            }
        }
    
    def _validate_strategy(self, strategy: Dict) -> Dict:
        """验证策略完整性"""
        # 补充默认值
        strategy.setdefault('id', datetime.now().strftime("%Y%m%d%H%M%S"))
        strategy.setdefault('created_at', datetime.now().isoformat())
        strategy.setdefault('status', 'pending_backtest')
        strategy.setdefault('applicable_market', 'A 股')
        strategy.setdefault('trading_style', '短线')
        
        # 默认风控参数
        if 'risk_management' not in strategy:
            strategy['risk_management'] = {
                'stop_loss': 0.08,
                'take_profit': 0.15,
                'max_position': 0.2
            }
        
        return strategy
    
    def _apply_improvements(self, strategy: Dict, improvement: Dict) -> Dict:
        """应用改进建议"""
        improved = strategy.copy()
        
        # 更新参数
        if 'revised_parameters' in improvement:
            improved.setdefault('parameters', {}).update(improvement['revised_parameters'])
        
        # 更新条件
        if 'revised_conditions' in improvement:
            if 'entry_conditions' in improvement['revised_conditions']:
                improved['entry_conditions'] = improvement['revised_conditions']['entry_conditions']
            if 'exit_conditions' in improvement['revised_conditions']:
                improved['exit_conditions'] = improvement['revised_conditions']['exit_conditions']
        
        # 标记为改进版本
        improved['version'] = strategy.get('version', 1) + 1
        improved['improved_at'] = datetime.now().isoformat()
        improved['status'] = 'pending_backtest'
        
        return improved
    
    def _save_strategy(self, strategy: Dict):
        """保存策略到文件"""
        strategy_file = self.strategy_storage / f"{strategy['id']}.json"
        with open(strategy_file, 'w', encoding='utf-8') as f:
            json.dump(strategy, f, ensure_ascii=False, indent=2)
        print(f"  📁 策略已保存：{strategy_file.name}")
    
    def load_strategies(self) -> List[Dict]:
        """加载所有 LLM 生成的策略"""
        strategies = []
        for file in self.strategy_storage.glob("*.json"):
            with open(file, 'r', encoding='utf-8') as f:
                strategies.append(json.load(f))
        return strategies
    
    def get_strategy_by_id(self, strategy_id: str) -> Optional[Dict]:
        """根据 ID 获取策略"""
        strategy_file = self.strategy_storage / f"{strategy_id}.json"
        if strategy_file.exists():
            with open(strategy_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None


if __name__ == "__main__":
    # 测试 LLM 策略生成
    print("=" * 60)
    print("LLM 策略生成器测试")
    print("=" * 60)
    
    generator = LLMStrategyGenerator()
    
    # 模拟市场数据
    market_data = {
        "market_trend": "震荡上行",
        "volatility": "中等",
        "avg_daily_change": 0.02,
        "avg_volume_change": 1.3,
        "sector_rotation": "快速",
        "description": "当前市场呈现震荡上行趋势，板块轮动较快，适合均值回归和动量策略"
    }
    
    # 生成策略
    print("\n生成新策略...\n")
    strategy = generator.generate_strategy(market_data)
    
    print("\n" + "=" * 60)
    print("生成的策略:")
    print("=" * 60)
    print(f"名称：{strategy['name']}")
    print(f"描述：{strategy['description']}")
    print(f"逻辑：{strategy['logic']}")
    print(f"买入条件：{strategy['entry_conditions']}")
    print(f"卖出条件：{strategy['exit_conditions']}")
    print(f"风控：{strategy.get('risk_management', {})}")
