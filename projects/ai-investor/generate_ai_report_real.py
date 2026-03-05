"""
完整 AI 投资决策 - 使用真实市场数据
"""
import os
import sys
sys.path.insert(0, '.')

os.environ['DASHSCOPE_API_KEY'] = 'sk-fb6aa9235b6b4627aa2ac5f7295db04c'

import dashscope
from dashscope import Generation
from datetime import datetime
from pathlib import Path

# 导入真实数据
sys.path.insert(0, str(Path(__file__).parent))
from data.market_data import get_latest_market_data

print("="*60)
print("AI 投资顾问 - 完整决策流程 (真实数据版)")
print("="*60)

# 获取真实市场数据
print("\n获取真实市场数据...")
market_data = get_latest_market_data()
print(f"  最新交易日：{market_data['latest_date']}")
print(f"  股票数量：{market_data['stock_count']}")
print(f"  涨跌分布：涨{market_data['up_count']} 跌{market_data['down_count']}")

# 1. 宏观分析 - 基于真实数据
print("\n[1/4] 宏观分析...")

# 获取上证指数数据
index_str = ""
for row in market_data['index_5days']:
    index_str += f"    {row[0]}: 开{row[1]:.2f} 收{row[4]:.2f} 高{row[2]:.2f} 低{row[3]:.2f}\n"

macro_prompt = f"""你是一位首席宏观经济分析师。请分析当前中国宏观经济和 A 股市场。

**当前日期：** {datetime.now().strftime('%Y-%m-%d')}
**最新交易日：** {market_data['latest_date']}

**真实市场数据：**
- 可交易股票数量：{market_data['stock_count']} 只
- 涨跌分布：上涨{market_data['up_count']}只 / 下跌{market_data['down_count']}只

**上证指数近 5 日走势：**
{index_str}

请基于以上真实数据分析：
1. 市场状态判断（牛/熊/震荡）
2. 市场情绪（基于涨跌分布）
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
quant_prompt = """你是一位量化分析师。请分析以下策略回测结果：
策略：均值回归策略
- 总收益率：+52.52%
- 年化收益：+50.08%
- 夏普比率：2.06
- 最大回撤：1.55%
- 胜率：84.2%

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
**市场数据：** 上涨{market_data['up_count']}只 / 下跌{market_data['down_count']}只

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
cio_prompt = f"""你是一位首席投资官。请综合以下三方报告做出投资决策。

**当前日期：** {datetime.now().strftime('%Y-%m-%d')}
**最新交易日：** {market_data['latest_date']}

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
report_file = f"reports/ai_investor_real_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
report_content = f"""# AI 投资决策报告（真实数据版）

**日期：** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**系统：** AI 投资顾问智能体
**数据源：** 真实 A 股市场数据

---

## 市场数据快照

| 指标 | 数值 |
|------|------|
| 当前日期 | {datetime.now().strftime('%Y-%m-%d')} |
| 最新交易日 | {market_data['latest_date']} |
| 可交易股票 | {market_data['stock_count']} 只 |
| 涨跌分布 | 涨{market_data['up_count']} / 跌{market_data['down_count']} / 平{market_data['flat_count']} |

### 上证指数近 5 日
{index_str}

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
"""

with open(report_file, 'w', encoding='utf-8') as f:
    f.write(report_content)

print(f"\n{'='*60}")
print(f"AI 决策完成！")
print(f"报告：{report_file}")
print(f"{'='*60}")
