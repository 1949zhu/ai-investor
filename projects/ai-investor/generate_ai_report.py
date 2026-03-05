"""
完整 AI 投资决策 - 直接运行版
"""
import os
os.environ['DASHSCOPE_API_KEY'] = 'sk-fb6aa9235b6b4627aa2ac5f7295db04c'

import dashscope
from dashscope import Generation
from datetime import datetime

print("="*60)
print("AI 投资顾问 - 完整决策流程")
print("="*60)

# 1. 宏观分析
print("\n[1/4] 宏观分析...")
macro_prompt = """你是一位首席宏观经济分析师。请分析当前中国宏观经济和 A 股市场，包括：
1. 经济基本面（GDP、PMI、通胀）
2. 政策环境
3. 市场状态判断（牛/熊/震荡）
4. 配置建议

用中文输出专业报告。"""

resp = Generation.call(model='qwen-plus', messages=[{'role':'user','content':macro_prompt}])
if resp.status_code == 200:
    macro_report = resp.output.text
    print(f"     ✅ 完成 ({len(macro_report)} 字)")
else:
    macro_report = "宏观分析暂缺"
    print(f"     ❌ 失败")

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
    print(f"     ❌ 失败")

# 3. 风险评估
print("[3/4] 风险评估...")
risk_prompt = """你是一位风控官。请评估当前投资风险，包括：
1. 市场风险等级（低/中/高）
2. 仓位建议
3. 止损止盈设置
4. 压力测试结果

风险限制：最大回撤 15%，单股上限 20%，止损 8%，止盈 20%。"""

resp = Generation.call(model='qwen-plus', messages=[{'role':'user','content':risk_prompt}])
if resp.status_code == 200:
    risk_report = resp.output.text
    print(f"     ✅ 完成 ({len(risk_report)} 字)")
else:
    risk_report = "风险评估暂缺"
    print(f"     ❌ 失败")

# 4. CIO 决策
print("[4/4] CIO 综合决策...")
cio_prompt = f"""你是一位首席投资官。请综合以下三方报告做出投资决策：

【宏观分析】
{macro_report[:800]}

【量化验证】
{quant_report[:800]}

【风险评估】
{risk_report[:800]}

请生成完整投资决策报告，包括：
1. 执行摘要（市场判断、操作方向、仓位、置信度）
2. 今日操作建议（标的、操作、仓位、止损、止盈）
3. 决策理由
4. 风险提示

用中文输出，格式清晰。"""

resp = Generation.call(model='qwen-plus', messages=[{'role':'user','content':cio_prompt}])
if resp.status_code == 200:
    decision = resp.output.text
    print(f"     ✅ 完成 ({len(decision)} 字)")
else:
    decision = "决策暂缺"
    print(f"     ❌ 失败")

# 保存报告
report_file = f"reports/ai_investor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
report_content = f"""# AI 投资决策报告

**日期：** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**系统：** AI 投资顾问智能体

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
