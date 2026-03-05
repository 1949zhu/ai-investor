# AI 投资顾问系统 - 当前状态

**版本：** v3.0
**最后更新：** 2026-03-05 20:30

---

## 📊 系统概览

```
┌─────────────────────────────────────────────────────────────┐
│                  AI 投资顾问系统 v3.0                        │
├─────────────────────────────────────────────────────────────┤
│  数据层          记忆层           智能体层       决策层      │
│  ┌──────┐      ┌──────────┐     ┌──────────┐  ┌────────┐  │
│  │SQLite│      │决策日志  │     │宏观分析师│  │        │  │
│  │数据库│─────→│经验教训  │────→│量化分析师│─→│CIO 决策│  │
│  │      │      │市场状态  │     │风控官    │  │        │  │
│  └──────┘      │策略绩效  │     └──────────┘  └────────┘  │
│       ↑         └──────────┘          ↑            │        │
│       │              ↑                │            │        │
│  真实数据      跨会话记忆          记忆上下文     报告      │
│  扩展情绪                          辅助分析      保存      │
│  回测验证                                        验证      │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ 已完成功能

### 1. 数据层

| 模块 | 文件 | 状态 | 说明 |
|------|------|------|------|
| 基础市场数据 | `data/market_data.py` | ✅ | 从 SQLite 获取真实 A 股数据 |
| 扩展市场数据 | `data/extended_data.py` | ✅ | 情绪指标、涨跌分布、排行榜 |
| 数据库 | `storage/ashare.db` | ✅ | 24MB, 真实 A 股历史数据 |

### 2. 记忆层

| 模块 | 文件 | 状态 | 说明 |
|------|------|------|------|
| 智能体记忆 | `memory/agent_memory.py` | ✅ | 跨会话记忆系统 |
| 决策日志 | `storage/agent_memory.db` | ✅ | 记录所有 AI 决策 |
| 经验教训 | - | ✅ | 累积投资经验 |
| 市场状态追踪 | - | ✅ | 记录市场 regime 变化 |
| 策略绩效 | - | ✅ | 记录策略历史表现 |

### 3. 智能体层

| 智能体 | 文件 | 状态 | 说明 |
|--------|------|------|------|
| 宏观分析师 | `agents/agents/macro.py` | ✅ | LLM 驱动，经济分析 |
| 量化分析师 | `agents/agents/quant.py` | ✅ | LLM 驱动，策略验证 |
| 风控官 | `agents/agents/risk.py` | ✅ | LLM 驱动，风险评估 |
| CIO | `agents/agents/cio.py` | ✅ | LLM 驱动，综合决策 |

### 4. 决策层

| 模块 | 文件 | 状态 | 说明 |
|------|------|------|------|
| LLM 服务 | `llm_service/` | ✅ | Dashscope Qwen-Plus |
| 报告生成 | `generate_ai_v3.py` | ✅ | v3.0 完整决策流程 |
| 报告存储 | `reports/` | ✅ | Markdown 格式 |

### 5. 回测验证

| 模块 | 文件 | 状态 | 说明 |
|------|------|------|------|
| 验证框架 | `backtest/validator.py` | ✅ | AI 决策回测验证 |
| 绩效统计 | - | ✅ | 胜率、收益、回撤 |
| 验证报告 | `reports/validation_*.md` | ✅ | 自动生成验证报告 |

---

## 📁 文件结构

```
projects/ai-investor/
├── agents/
│   ├── agents/
│   │   ├── macro.py       # 宏观分析师
│   │   ├── quant.py       # 量化分析师
│   │   ├── risk.py        # 风控官
│   │   └── cio.py         # CIO
│   ├── memory.py          # 智能体记忆基类
│   ├── crew.py            # 智能体协作
│   └── main.py            # 主入口
├── data/
│   ├── market_data.py     # 基础市场数据
│   └── extended_data.py   # 扩展市场数据
├── llm_service/
│   ├── __init__.py
│   ├── base.py            # LLM 基类
│   ├── dashscope.py       # Dashscope 接口
│   └── config.py          # 配置
├── memory/
│   └── agent_memory.py    # 智能体记忆系统
├── backtest/
│   └── validator.py       # 回测验证框架
├── reports/
│   ├── ai_investor_v3_*.md       # AI 决策报告
│   ├── ai_investor_real_*.md     # 真实数据报告
│   └── validation_*.md           # 验证报告
├── storage/
│   ├── ashare.db          # A 股市场数据 (24MB)
│   └── agent_memory.db    # 智能体记忆
├── generate_ai_v3.py      # v3.0 决策生成器
├── generate_ai_report.py  # v2.0 决策生成器
├── ROADMAP.md             # 进化路线图
└── status.md              # 系统状态 (本文件)
```

---

## 🚀 使用方式

### 运行完整决策流程

```bash
cd D:\openclaw\workspace\projects\ai-investor

# v3.0 (推荐) - 包含记忆和扩展数据
python generate_ai_v3.py

# 查看生成的报告
ls reports/*.md
```

### 查看记忆系统

```python
from memory.agent_memory import AgentMemory

memory = AgentMemory()

# 获取当前市场状态
regime = memory.get_market_regime()
print(f"当前市场：{regime['regime']}")

# 获取经验教训
lessons = memory.get_lessons(limit=5)
for l in lessons:
    print(f"- {l['lesson']}")

# 获取决策历史
decisions = memory.get_decision_history(limit=10)
```

### 回测验证

```python
from backtest.validator import BacktestValidator

validator = BacktestValidator()

# 验证历史决策
results = validator.validate_past_decisions()

# 获取策略统计
stats = validator.get_strategy_stats()
print(f"胜率：{stats['win_rate']*100:.1f}%")

# 生成验证报告
report_path = validator.generate_validation_report()
```

---

## 📈 性能指标

| 指标 | 当前值 | 目标 | 状态 |
|------|--------|------|------|
| 数据源数量 | 2 | 5+ | ⚠️ 需扩展 |
| 决策准确率 | 待验证 | >60% | ⏳ 收集中 |
| 记忆容量 | 2 条 | 100+ | ⏳ 增长中 |
| 支持市场 | 1 (A 股) | 3+ | ⚠️ 需扩展 |
| LLM 响应时间 | ~30s | <20s | ⚠️ 可优化 |
| 单次决策成本 | ¥0.20 | <¥0.10 | ⚠️ 需优化 |

---

## 🎯 下一步计划

### 短期 (本周)
- [ ] 接入新闻数据源
- [ ] 接入北向资金数据
- [ ] 优化 LLM 提示词减少 token 消耗
- [ ] 收集更多决策数据用于验证

### 中期 (2 周内)
- [ ] 实现自主学习机制
- [ ] 接入港股数据
- [ ] 优化智能体协作流程
- [ ] 添加决策可视化

### 长期 (1 个月内)
- [ ] 多市场支持 (港股/美股)
- [ ] 实盘对接测试
- [ ] 强化学习优化
- [ ] Web 界面

---

## 📝 版本历史

| 版本 | 日期 | 主要变更 |
|------|------|----------|
| v1.0 | 2026-03-05 | 基础智能体架构 |
| v2.0 | 2026-03-05 17:45 | 真实数据接入 |
| v3.0 | 2026-03-05 20:26 | 记忆系统 + 扩展数据 + 回测验证 |

---

*持续更新中...*
