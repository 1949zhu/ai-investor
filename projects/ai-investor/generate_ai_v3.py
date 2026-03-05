"""
完整 AI 投资决策 - v3.0 (扩展数据 + 记忆系统)
"""
import os
import sys
sys.path.insert(0, '.')

os.environ['DASHSCOPE_API_KEY'] = 'sk-fb6aa9235b6b4627aa2ac5f7295db04c'

import dashscope
from dashscope import Generation
from datetime import datetime
from pathlib import Path

# 导入模块
from data.market_data import get_latest_market_data
from data.extended_data import ExtendedMarketData
from memory.agent_memory import AgentMemory

print("="*60)
print("AI 投资顾问 v3.0 - 完整决策流程")
print("="*60)

# 初始化
market_data = ExtendedMarketData()
memory = AgentMemory()

# 获取真实市场数据
print("\n获取市场数据...")
latest = get_latest_market_data()
sentiment = market_data.get_market_sentiment()
summary = market_data.get_market_summary()

print(f"  最新交易日：{latest['latest_date']}")
print(f"  涨跌分布：涨{sentiment.get('up_count',0)} 跌{sentiment.get('down_count',0)}")
print(f"  市场情绪：{sentiment.get('sentiment_label','未知')} ({sentiment.get('sentiment_score',0):.1f})")

# 获取记忆上下文
print("\n加载记忆上下文...")
memory_context = memory.get_context_for_agent("all")
print(f"  {memory_context[:200]}..." if len(memory_context) > 200 else f"  {memory_context}")

# 1. 宏观分析
print("\n[1/4] 宏观分析...")

# 构建指数数据字符串
index_str = ""
if summary.get('index_5days'):
    for row in summary['index_5days'][-5:]:
        if row.get('close'):
            index_str += f"    {row['date']}: 收{row['close']:.2f} 涨{row.get('change_pct',0)*100:.2f}%\n"

macro_prompt = f"""你是一位首席宏观经济分析师。请分析当前 A 股市场。

**当前日期：** {datetime.now().strftime('%Y-%m-%d')}
**最新交易日：** {latest['latest_date']}

**市场数据：**
- 可交易股票：{latest.get('stock_count', '未知')} 只
- 涨跌分布：上涨{sentiment.get('up_count',0)} / 下跌{sentiment.get('down_count',0)} / 平{sentiment.get('flat_count',0)}
- 市场情绪：{sentiment.get('sentiment_label','未知')} (得分：{sentiment.get('sentiment_score',0):.1f}/100)
- 平均涨幅：{sentiment.get('avg_change',0):.2f}%
- 涨停：{sentiment.get('limit_up',0)} 只 | 跌停：{sentiment.get('limit_down',0)} 只

**上证指数近 5 日：**
{index_str if index_str else '    数据暂缺'}

**历史记忆：**
{memory_context}

请基于以上数据分析：
1. 市场状态判断（牛/熊/震荡）
2. 市场情绪分析
3. 配置建议

用中文输出专业报告。"""

resp = Generation.call(model='qwen-plus', messages=[{'role':'user','content':macro_prompt}])
if resp.status_code == 200:
    macro_report = resp.output.text
    print(f"     ✅ 完成 ({len(macro_report)} 字)")
else:
    macro_report = "宏观分析暂缺"
    print(f"     ❌ 失败：{resp.status_code}")

# 2. 量化验证
print("[2/4] 量化验证...")

# 获取策略历史
strategy_history = memory.get_strategy_history(limit=3)
strategy_str = ""
for s in strategy_history:
    strategy_str += f"- {s['strategy_name']}: 收益{s['return_rate']*100:.1f}% 夏普{s['sharpe_ratio']:.2f} 回撤{s['max_drawdown']*100:.2f}%\n"

quant_prompt = f"""你是一位量化分析师。请评估策略。

**策略回测结果：**
- 均值回归策略
- 总收益率：+52.52%
- 年化收益：+50.08%
- 夏普比率：2.06
- 最大回撤：1.55%
- 胜率：84.2%

**策略历史绩效：**
{strategy_str if strategy_str else '暂无历史记录'}

请评估策略可信度（0-100 分）并给出建议。"""

resp = Generation.call(model='qwen-plus', messages=[{'role':'user','content':quant_prompt}])
if resp.status_code == 200:
    quant_report = resp.output.text
    print(f"     ✅ 完成 ({len(quant_report)} 字)")
else:
    quant_report = "量化分析暂缺"
    print(f"     ❌ 失败：{resp.status_code}")

# 3. 风险评估
print("[3/4] 风险评估...")

risk_prompt = f"""你是一位风控官。请评估当前投资风险。

**当前日期：** {datetime.now().strftime('%Y-%m-%d')}
**市场情绪：** {sentiment.get('sentiment_label','未知')} ({sentiment.get('sentiment_score',0):.1f}/100)
**涨跌分布：** 上涨{sentiment.get('up_count',0)} / 下跌{sentiment.get('down_count',0)}
**平均涨幅：** {sentiment.get('avg_change',0):.2f}%

请评估：
1. 市场风险等级（低/中/高）
2. 仓位建议
3. 止损止盈设置

风险限制：最大回撤 15%，单股上限 20%，止损 8%，止盈 20%。"""

resp = Generation.call(model='qwen-plus', messages=[{'role':'user','content':risk_prompt}])
if resp.status_code == 200:
    risk_report = resp.output.text
    print(f"     ✅ 完成 ({len(risk_report)} 字)")
else:
    risk_report = "风险评估暂缺"
    print(f"     ❌ 失败：{resp.status_code}")

# 4. CIO 决策
print("[4/4] CIO 综合决策...")

cio_prompt = f"""你是一位首席投资官。请综合以下报告做出投资决策。

**当前日期：** {datetime.now().strftime('%Y-%m-%d')}

【宏观分析】
{macro_report[:1000]}

【量化验证】
{quant_report[:800]}

【风险评估】
{risk_report[:800]}

请生成完整投资决策报告，包括：
1. 执行摘要（市场判断、操作方向、仓位、置信度）
2. 今日操作建议（具体标的、操作、仓位、止损、止盈）
3. 决策理由
4. 风险提示

用中文输出，格式清晰。"""

resp = Generation.call(model='qwen-plus', messages=[{'role':'user','content':cio_prompt}])
if resp.status_code == 200:
    decision = resp.output.text
    print(f"     ✅ 完成 ({len(decision)} 字)")
else:
    decision = "决策暂缺"
    print(f"     ❌ 失败：{resp.status_code}")

# 保存报告
report_file = f"reports/ai_investor_v3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
report_content = f"""# AI 投资决策报告 (v3.0)

**日期：** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**系统：** AI 投资顾问智能体 v3.0
**数据源：** 真实 A 股市场数据 + 扩展情绪指标 + 智能体记忆

---

## 市场数据快照

| 指标 | 数值 |
|------|------|
| 当前日期 | {datetime.now().strftime('%Y-%m-%d')} |
| 最新交易日 | {latest['latest_date']} |
| 可交易股票 | {latest.get('stock_count', '未知')} 只 |
| 涨跌分布 | 涨{sentiment.get('up_count',0)} / 跌{sentiment.get('down_count',0)} / 平{sentiment.get('flat_count',0)} |
| 市场情绪 | {sentiment.get('sentiment_label','未知')} ({sentiment.get('sentiment_score',0):.1f}/100) |
| 平均涨幅 | {sentiment.get('avg_change',0):.2f}% |
| 涨停/跌停 | {sentiment.get('limit_up',0)} / {sentiment.get('limit_down',0)} |

### 上证指数近 5 日
{index_str if index_str else '数据暂缺'}

---

## 宏观分析报告

{macro_report}

---

## 量化分析报告

{quant_report}

---

## 风险评估报告

{risk_report}

---

## 投资决策

{decision}

---

## 附录：智能体记忆上下文

{memory_context}
"""

with open(report_file, 'w', encoding='utf-8') as f:
    f.write(report_content)

# 记录决策到记忆
memory.add_decision(
    date=datetime.now().strftime("%Y-%m-%d"),
    market_state=sentiment.get('sentiment_label', '未知'),
    decision=decision[:200] if decision else "无",
    reasoning="AI 智能体综合分析",
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

print(f"\n{'='*60}")
print(f"AI 决策完成！")
print(f"报告：{report_file}")
print(f"记忆已更新")
print(f"{'='*60}")
