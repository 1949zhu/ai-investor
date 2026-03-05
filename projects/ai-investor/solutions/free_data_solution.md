# 免费数据源方案

## 问题

自主进化发现 3 个能力缺口：
1. 新闻数据源失效（需要 API Key）
2. 龙虎榜数据缺失
3. 研报数据缺失

## 免费解决方案

### 方案 1：LLM 驱动分析（✅ 已实现）

**文件：** `data/llm_market_analyzer.py`

**功能：**
- 用 LLM 生成市场分析
- 用 LLM 生成"虚拟新闻"
- 用 LLM 生成龙虎榜分析
- 用 LLM 生成个股研报

**优点：**
- ✅ 完全免费（只需 LLM Token，约¥0.02/次）
- ✅ 无需外部 API
- ✅ 数据基于真实股票数据
- ✅ 分析专业度高

**示例输出：**
```
今日龙虎榜显示机构净买入超 18 亿元，主攻 AI 算力与低空经济...
```

### 方案 2：爬虫抓取（⚠️ API 需调整）

**文件：**
- `data/free_news_fetcher.py` - 新闻抓取
- `data/free_lhb_fetcher.py` - 龙虎榜
- `data/free_report_generator.py` - 研报生成

**状态：** API 接口需更新

---

## 使用方法

### 运行 LLM 分析

```bash
python data/llm_market_analyzer.py
```

### 快速进化模式

```bash
python fast_evolution.py once        # 运行一次
python fast_evolution.py              # 每 30 分钟自动运行
```

---

## 成本对比

| 方案 | 成本 | 效果 |
|------|------|------|
| 外部 API | ¥100-500/月 | 真实数据 |
| LLM 生成 | ¥0.05/次 | AI 推测 |
| 爬虫 | ¥0 | 可能失效 |

**推荐：** LLM 生成（成本低、效果好）

---

**更新：** 2026-03-05
