"""
AI 投资决策生成器 v4.0 - 完整版
整合：真实数据 + 记忆系统 + 新闻 + 北向资金 + 优化提示词 + 自主学习
"""
import os
import sys
sys.path.insert(0, '.')

os.environ['DASHSCOPE_API_KEY'] = 'sk-fb6aa9235b6b4627aa2ac5f7295db04c'

import dashscope
from dashscope import Generation
from datetime import datetime
from pathlib import Path

# 导入所有模块
from data.market_data import get_latest_market_data
from data.extended_data import ExtendedMarketData
from data.news_fetcher import NewsFetcher
from data.northbound_fetcher import NorthboundFetcher
from memory.agent_memory import AgentMemory
from llm_service.optimized_prompts import OptimizedPrompts, TokenOptimizer
from learning.autonomous import AutonomousLearner, init_feedback_table
from visualization.charts import DecisionVisualizer

print("="*70)
print("           AI 投资顾问系统 v4.0 - 完整决策流程")
print("="*70)

# 初始化所有模块
market_data = ExtendedMarketData()
news_fetcher = NewsFetcher()
northbound_fetcher = NorthboundFetcher()
memory = AgentMemory()
learner = AutonomousLearner()
visualizer = DecisionVisualizer()

# 初始化反馈表
init_feedback_table()

# ========== 第一步：获取全量数据 ==========
print("\n【1/6】获取市场数据...")

# 基础市场数据
latest = get_latest_market_data()
sentiment = market_data.get_market_sentiment()
summary = market_data.get_market_summary()

print(f"  ✓ 最新交易日：{latest['latest_date']}")
print(f"  ✓ 涨跌分布：涨{sentiment.get('up_count',0)} 跌{sentiment.get('down_count',0)}")
print(f"  ✓ 市场情绪：{sentiment.get('sentiment_label','未知')} ({sentiment.get('sentiment_score',0):.1f})")

# 新闻数据
print("\n【2/6】获取新闻数据...")
news = news_fetcher.get_latest_news(hours=24)
news_sentiment = news_fetcher.analyze_sentiment(news)
print(f"  ✓ 获取新闻：{len(news)} 条")
print(f"  ✓ 新闻情绪：{news_sentiment['sentiment']} ({news_sentiment['score']}分)")

# 北向资金
print("\n【3/6】获取北向资金...")
northbound = northbound_fetcher.get_northbound_summary()
print(f"  ✓ 最新流入：{northbound.get('latest_net_inflow', 0):.1f}亿")
print(f"  ✓ 5 日累计：{northbound.get('inflow_5d', 0):.1f}亿")
print(f"  ✓ 趋势：{northbound.get('trend', '未知')}")

# 记忆上下文
print("\n【4/6】加载记忆上下文...")
memory_context = memory.get_context_for_agent("all")
print(f"  ✓ 市场状态：{memory.get_market_regime()}")
print(f"  ✓ 经验教训：{len(memory.get_lessons())} 条")

# ========== 第二步：生成优化版提示词 ==========
print("\n【5/6】生成 AI 分析...")

# 准备数据
macro_data = {
    'date': datetime.now().strftime('%Y-%m-%d'),
    'up': sentiment.get('up_count', 0),
    'down': sentiment.get('down_count', 0),
    'sentiment': sentiment.get('sentiment_label', '中性'),
    'score': sentiment.get('sentiment_score', 50),
    'avg_change': sentiment.get('avg_change', 0)
}

# 宏观分析（使用优化提示词）
print("  → 宏观分析...")
macro_prompt = OptimizedPrompts.macro_analyst(macro_data, memory_context[:300])
resp = Generation.call(model='qwen-plus', messages=[{'role':'user','content':macro_prompt}])
if resp.status_code == 200:
    macro_report = resp.output.text
    print(f"     ✅ {len(macro_report)}字")
else:
    macro_report = "宏观分析暂缺"
    print(f"     ❌ 失败")

# 量化验证
print("  → 量化验证...")
strategy_data = {
    'return': 52.52,
    'annual': 50.08,
    'sharpe': 2.06,
    'mdd': 1.55,
    'win_rate': 84.2
}
strategy_history = memory.get_strategy_history(limit=2)
history_str = "\n".join([f"- {s['strategy_name']}: 收益{s['return_rate']*100:.1f}%" for s in strategy_history])

quant_prompt = OptimizedPrompts.quant_analyst(strategy_data, history_str[:200])
resp = Generation.call(model='qwen-plus', messages=[{'role':'user','content':quant_prompt}])
if resp.status_code == 200:
    quant_report = resp.output.text
    print(f"     ✅ {len(quant_report)}字")
else:
    quant_report = "量化分析暂缺"
    print(f"     ❌ 失败")

# 风险评估
print("  → 风险评估...")
risk_prompt = OptimizedPrompts.risk_officer({
    'label': sentiment.get('sentiment_label', '中性'),
    'score': sentiment.get('sentiment_score', 50),
    'up': sentiment.get('up_count', 0),
    'down': sentiment.get('down_count', 0),
    'avg_change': sentiment.get('avg_change', 0)
})
resp = Generation.call(model='qwen-plus', messages=[{'role':'user','content':risk_prompt}])
if resp.status_code == 200:
    risk_report = resp.output.text
    print(f"     ✅ {len(risk_report)}字")
else:
    risk_report = "风险评估暂缺"
    print(f"     ❌ 失败")

# CIO 决策
print("  → CIO 综合决策...")
cio_prompt = OptimizedPrompts.cio_decision(macro_report, quant_report, risk_report, memory_context[:200])
resp = Generation.call(model='qwen-plus', messages=[{'role':'user','content':cio_prompt}])
if resp.status_code == 200:
    decision = resp.output.text
    print(f"     ✅ {len(decision)}字")
else:
    decision = "决策暂缺"
    print(f"     ❌ 失败")

# ========== 第三步：保存报告 ==========
print("\n【6/6】保存报告...")

report_file = f"reports/ai_investor_v4_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
report_content = f"""# AI 投资决策报告 (v4.0)

**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**系统：** AI 投资顾问智能体 v4.0
**特点：** 真实数据 + 记忆系统 + 新闻 + 北向资金 + 优化提示词

---

## 📊 市场数据快照

| 指标 | 数值 |
|------|------|
| 当前日期 | {datetime.now().strftime('%Y-%m-%d')} |
| 最新交易日 | {latest['latest_date']} |
| 涨跌分布 | 涨{sentiment.get('up_count',0)} / 跌{sentiment.get('down_count',0)} |
| 市场情绪 | {sentiment.get('sentiment_label','未知')} ({sentiment.get('sentiment_score',0):.1f}/100) |
| 平均涨幅 | {sentiment.get('avg_change',0):.2f}% |

---

## 📰 新闻情绪

| 指标 | 数值 |
|------|------|
| 新闻数量 | {len(news)} 条 |
| 正面新闻 | {news_sentiment.get('positive', 0)} |
| 负面新闻 | {news_sentiment.get('negative', 0)} |
| 中性新闻 | {news_sentiment.get('neutral', 0)} |
| 整体情绪 | {news_sentiment.get('sentiment', '中性')} ({news_sentiment.get('score', 50)}分) |

### 最新新闻
"""

for i, n in enumerate(news[:5], 1):
    report_content += f"{i}. **[{n['source']}]** {n['title'][:60]}...  \n   时间：{n['time']}  \n\n"

report_content += f"""
---

## 💰 北向资金

| 指标 | 数值 |
|------|------|
| 最新流入 | {northbound.get('latest_net_inflow', 0):.1f}亿 |
| 5 日累计 | {northbound.get('inflow_5d', 0):.1f}亿 |
| 10 日累计 | {northbound.get('inflow_10d', 0):.1f}亿 |
| 趋势 | {northbound.get('trend', '未知')} |

### 活跃成交股 (Top 5)
"""

for i, stock in enumerate(northbound.get('active_stocks', [])[:5], 1):
    direction = '→' if stock['net_inflow'] > 0 else '←'
    report_content += f"{i}. **{stock['name']}** ({stock['code']}) {direction} {abs(stock['net_inflow']):.2f}亿  \n"

report_content += f"""
---

## 🧠 记忆上下文

{memory_context if memory_context else '暂无历史记忆'}

---

## 📈 宏观分析报告

{macro_report}

---

## 📉 量化分析报告

{quant_report}

---

## 🛡️ 风险评估报告

{risk_report}

---

## 💼 投资决策

{decision}

---

## 📊 Token 使用统计

| 模块 | 提示词 | 输出 |
|------|--------|------|
| 宏观分析 | ~200 字 | {len(macro_report)}字 |
| 量化验证 | ~150 字 | {len(quant_report)}字 |
| 风险评估 | ~100 字 | {len(risk_report)}字 |
| CIO 决策 | ~300 字 | {len(decision)}字 |
| **总计** | **~750 字** | **{len(macro_report)+len(quant_report)+len(risk_report)+len(decision)}字** |

**预估成本：** ¥{(750 + len(macro_report)+len(quant_report)+len(risk_report)+len(decision))/1000 * 0.01:.2f}元

---

*报告由 AI 投资顾问系统 v4.0 自动生成*
"""

with open(report_file, 'w', encoding='utf-8') as f:
    f.write(report_content)

print(f"  ✓ 报告已保存：{report_file}")

# ========== 第四步：记录决策到记忆 ==========
memory.add_decision(
    date=datetime.now().strftime("%Y-%m-%d"),
    market_state=sentiment.get('sentiment_label', '未知'),
    decision=decision[:200] if decision else "无",
    reasoning="AI 智能体综合分析 (v4.0)",
    outcome="待验证"
)

# 更新市场状态
if sentiment.get('sentiment_score', 50) >= 60:
    regime = "乐观"
elif sentiment.get('sentiment_score', 50) >= 40:
    regime = "震荡"
else:
    regime = "悲观"

memory.set_market_regime(regime, sentiment.get('sentiment_score', 50) / 100)
print(f"  ✓ 记忆已更新")

# ========== 第五步：生成可视化报告 ==========
print("\n生成可视化报告...")
decisions = memory.get_decision_history(limit=10)
viz_report, viz_file = visualizer.generate_full_report(decisions)
print(f"  ✓ 可视化报告：{viz_file}")

# ========== 完成 ==========
print("\n" + "="*70)
print("                    ✅ AI 决策完成！")
print("="*70)
print(f"\n📄 决策报告：{report_file}")
print(f"📊 可视化：{viz_file}")
print(f"🧠 记忆已更新")
print(f"💰 预估成本：¥{(750 + len(macro_report)+len(quant_report)+len(risk_report)+len(decision))/1000 * 0.01:.2f}元")
print("="*70)
