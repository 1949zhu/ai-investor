"""
填充测试数据到数据库，让 Web 界面有内容显示
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import random
import json

BASE_PATH = Path(__file__).parent
STORAGE_PATH = BASE_PATH / "storage"

# 填充 agent_memory.db
print("填充 agent_memory.db...")
db_path = STORAGE_PATH / "agent_memory.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 插入决策记录
decisions = [
    ("2026-03-05", "震荡市", "买入中国平安 (601318.SH)", "低估值 + 高股息防御", "收益 2.5%", "收益 2.5%，符合预期"),
    ("2026-03-04", "乐观", "买入贵州茅台 (600519.SH)", "消费复苏趋势", "收益 5.2%", "收益 5.2%，超预期"),
    ("2026-03-03", "悲观", "减仓避险", "市场情绪转差", "避免损失 3%", "成功避险"),
    ("2026-03-02", "震荡市", "持有观望", "方向不明", "收益 0%", "正确判断"),
    ("2026-03-01", "乐观", "买入宁德时代 (300750.SZ)", "新能源反弹", "收益 3.8%", "收益良好"),
]

for d in decisions:
    cursor.execute("""
        INSERT OR REPLACE INTO decision_log 
        (date, market_state, decision, reasoning, outcome, reflection, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (*d, datetime.now().isoformat()))

conn.commit()
conn.close()
print(f"  ✓ 插入 {len(decisions)} 条决策记录")

# 填充 problems.db
print("填充 problems.db...")
db_path = STORAGE_PATH / "problems.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 插入问题
problems = [
    ("新闻数据源失效，无法获取市场新闻", "data", "medium", "API 受限或反爬", "identified"),
    ("龙虎榜数据缺失", "capability", "high", "需要接入新数据源", "identified"),
]

for p in problems:
    cursor.execute("""
        INSERT OR REPLACE INTO problems 
        (problem, category, severity, root_cause, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (*p, datetime.now().isoformat()))

# 插入能力缺口
gaps = [
    ("龙虎榜数据接入", "机构动向是重要参考", "high", "A 股 龙虎榜 数据 API"),
    ("研报数据接入", "券商研报提供专业分析", "medium", "券商 研报 数据 API Python"),
    ("更完善的回测框架", "验证策略有效性", "medium", "股票 回测框架 Python backtrader"),
]

for g in gaps:
    cursor.execute("""
        INSERT OR REPLACE INTO capability_gaps 
        (capability, why_needed, priority, search_query, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (*g, datetime.now().isoformat()))

# 插入改进记录
improvements = [
    ("优化 LLM 提示词", "before", "after", "节省 74% Token", 1),
    ("接入北向资金数据", "before", "after", "新增数据源", 1),
    ("添加自主进化引擎", "before", "after", "系统可自主运行", 1),
]

for i in improvements:
    cursor.execute("""
        INSERT OR REPLACE INTO improvements 
        (improvement, before_state, after_state, impact, verified, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (*i, datetime.now().isoformat()))

conn.commit()
conn.close()
print("  ✓ 插入问题、能力缺口、改进记录")

# 更新 scheduler.json
print("更新 scheduler.json...")
config_path = BASE_PATH / "config" / "scheduler.json"
config_path.parent.mkdir(parents=True, exist_ok=True)

config = {
    "enabled": True,
    "check_interval_hours": 4,
    "full_analysis_interval_hours": 24,
    "alert_enabled": True,
    "last_check": datetime.now().isoformat(),
    "last_full_analysis": datetime.now().isoformat(),
    "run_count": 15
}

with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

print("  ✓ 更新运行次数：15")

print("\n✅ 测试数据填充完成！")
print("\n现在刷新浏览器 http://localhost:5000 应该能看到数据了！")
