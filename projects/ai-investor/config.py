"""
配置文件
"""

from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 数据存储
DATA_CONFIG = {
    'db_path': PROJECT_ROOT / "storage" / "ashare.db",
    'data_dir': PROJECT_ROOT / "data" / "raw",
}

# 策略配置
STRATEGY_CONFIG = {
    'strategies_file': PROJECT_ROOT / "storage" / "strategies.json",
    'builtin_strategies': [
        'mean_reversion',
        'momentum',
        'value'
    ]
}

# 回测配置
BACKTEST_CONFIG = {
    'initial_capital': 1000000,  # 初始资金 100 万
    'default_start_date': '20230101',
    'default_end_date': '20241231',
    'benchmark': '000001'  # 沪深 300
}

# 风控配置
RISK_CONFIG = {
    'max_position_pct': 0.3,  # 单只股票最大仓位 30%
    'max_total_position': 0.95,  # 最大总仓位 95%
    'default_stop_loss': 0.10,  # 默认止损 10%
    'default_take_profit': 0.20,  # 默认止盈 20%
}

# 报告配置
REPORT_CONFIG = {
    'output_dir': PROJECT_ROOT / "reports",
    'format': 'markdown',
    'include_charts': True,
}

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'dir': PROJECT_ROOT / "logs",
}
