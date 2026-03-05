# AI 投资顾问系统 - 完整文档

## 📊 系统概述

基于真实 A 股数据的智能投资分析系统，具备策略回测、报告生成、情绪分析等能力。

**核心理念：**
- 使用真实市场数据，不模拟
- 如实报告问题，不降级
- 模块化设计，易于扩展

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                   AI 投资顾问系统                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📊 数据层 (data/)                                      │
│     • BaoStock 数据获取                                  │
│     • 800 只 A 股，193,449 条日线行情                     │
│     • SQLite 数据库存储                                   │
│                                                         │
│  📈 策略层 (strategy/)                                  │
│     • 均值回归策略                                      │
│     • 动量突破策略                                      │
│     • 价值投资策略                                      │
│     • LLM 策略生成器（可选）                             │
│                                                         │
│  🔬 回测层 (backtest/)                                  │
│     • 多股票组合回测                                    │
│     • 绩效评估指标                                      │
│     • 交易记录追踪                                      │
│                                                         │
│  📝 报告层 (report/)                                    │
│     • 模板化报告生成                                    │
│     • LLM 增强报告（可选）                               │
│                                                         │
│  📰 新闻层 (news/)                                      │
│     • 多数据源新闻获取                                  │
│     • 实时财经新闻                                      │
│                                                         │
│  💭 情绪层 (sentiment/)                                 │
│     • 新闻情绪分析                                      │
│     • LLM 情感识别                                      │
│                                                         │
│  🔄 优化层 (optimizer/)                                 │
│     • 策略失败分析                                      │
│     • 自优化建议                                        │
│                                                         │
│  🛠️ 系统层 (system/)                                    │
│     • 健康检查                                          │
│     • 状态监控                                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 项目结构

```
ai-investor/
├── data/                    # 数据模块
│   ├── fetcher.py          # 数据获取接口
│   └── baostock_fetcher.py # BaoStock 实现
├── strategy/                # 策略模块
│   ├── generator.py        # 策略生成器
│   └── llm_generator.py    # LLM 策略生成
├── backtest/                # 回测模块
│   └── engine.py           # 回测引擎
├── report/                  # 报告模块
│   ├── generator.py        # 报告生成器
│   └── llm_enhancer.py     # LLM 报告增强
├── news/                    # 新闻模块
│   └── fetcher.py          # 新闻获取器
├── sentiment/               # 情绪模块
│   └── analyzer.py         # 情绪分析器
├── optimizer/               # 优化模块
│   └── llm_optimizer.py    # LLM 自优化
├── llm_service/             # LLM 服务层
│   ├── __init__.py         # 服务接口
│   ├── base.py             # 基础类
│   ├── dashscope.py        # Dashscope 实现
│   └── config.py           # 配置管理
├── system/                  # 系统模块
│   └── healthcheck.py      # 健康检查
├── storage/                 # 数据存储
│   ├── ashare.db           # A 股数据库
│   ├── news_cache/         # 新闻缓存
│   ├── llm_cache/          # LLM 响应缓存
│   └── llm_strategies/     # LLM 生成策略
├── reports/                 # 生成的报告
├── logs/                    # 运行日志
├── main.py                  # 主入口
├── requirements.txt         # 依赖
└── status.md               # 项目状态
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install baostock dashscope requests
```

### 2. 配置环境变量（可选）

```bash
# LLM 服务（启用 AI 功能）
set DASHSCOPE_API_KEY=your_api_key_here
```

### 3. 运行系统

```bash
# 运行每日任务（完整流程）
python main.py --daily

# 初始化数据
python main.py --init-data

# 生成 LLM 策略
python main.py --llm-strategy

# 优化策略
python main.py --optimize

# 健康检查
python -c "from system.healthcheck import HealthChecker; HealthChecker().check_all()"
```

---

## 📊 策略说明

### 均值回归策略
- **逻辑：** 价格围绕价值波动，超卖时买入，超买时卖出
- **回测表现：** +52.52% 总收益，+50.08% 年化，夏普 2.06
- **适用：** 震荡市场

### 动量突破策略
- **逻辑：** 突破关键价位时跟随趋势
- **回测表现：** +6.20% 总收益，胜率 33.3%
- **适用：** 趋势市场

### 价值投资策略
- **逻辑：** 低估值时买入，长期持有
- **回测表现：** +18.11% 总收益，夏普 0.80
- **适用：** 长线投资

---

## 🧠 LLM 功能

### 策略生成
```python
from strategy.llm_generator import LLMStrategyGenerator

gen = LLMStrategyGenerator()
strategy = gen.generate_strategy(market_data)
```

### 情绪分析
```python
from sentiment.analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()
sentiment = analyzer.analyze_realtime_news_sentiment(limit=30)
```

### 报告增强
```python
from report.llm_enhancer import LLMReportEnhancer

enhancer = LLMReportEnhancer()
report = enhancer.enhance_report(report_data)
```

### 自优化
```python
from optimizer.llm_optimizer import LLMOptimizer

optimizer = LLMOptimizer()
analysis = optimizer.analyze_failure(strategy, backtest_result)
```

---

## ⚠️ 错误处理

系统遵循**如实报告**原则：

- API 失败 → 直接报告错误，不降级
- 数据缺失 → 明确提示，不模拟
- 服务不可用 → 说明原因和建议

### 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| 新闻 API 404 | 外部 API 不可用 | 检查网络，稍后重试 |
| InvalidApiKey | 未配置 LLM Key | 设置 `DASHSCOPE_API_KEY` |
| 数据库错误 | 表名变更 | 检查数据库结构 |

---

## 📈 性能指标

| 指标 | 数值 |
|------|------|
| 数据库大小 | 25.2 MB |
| 股票数量 | 800 只 |
| 行情记录 | 193,449 条 |
| 策略数量 | 3 + LLM 生成 |
| 最佳策略 | 均值回归 (+52.52%) |

---

## 🔧 维护

### 更新数据
```bash
python main.py --init-data --stocks 100
```

### 健康检查
```bash
python -c "from system.healthcheck import HealthChecker; HealthChecker().check_all()"
```

### 查看日志
```bash
# 每日日志
logs/daily_YYYYMMDD.md

# 健康检查
logs/health_YYYYMMDD_HHMMSS.json
```

---

## 📝 待办事项

- [ ] 寻找稳定的新闻 API 数据源
- [ ] 配置有效 Dashscope API Key
- [ ] 添加更多交易策略
- [ ] 实现实时行情接入
- [ ] 添加组合优化功能

---

## 📞 支持

问题排查顺序：
1. 检查 `status.md` 了解当前状态
2. 运行健康检查 `python -c "..."`
3. 查看最新日志 `logs/`
4. 检查数据库 `storage/ashare.db`

---

*最后更新：2026-03-05*
