# 自主运行配置 - 让系统自己跑，不用人管

## 🎯 目标

让 AI 投资系统**真正自主运行**：
- ✅ 自己定时检查（每 4 小时）
- ✅ 自己每日分析（每天 20:00）
- ✅ 自己发现问题
- ✅ 自己尝试改进
- ✅ 主动通知异常

---

## 📁 新增文件

```
autonomous/
├── evolution_engine.py    # 自主进化引擎（大脑）
└── scheduler.py           # 自主调度器（心跳）
```

---

## 🚀 三种运行方式

### 方式 1：手动运行一次（测试用）

```bash
cd D:\openclaw\workspace\projects\ai-investor
python autonomous\scheduler.py --mode once
```

### 方式 2：持续运行（开发测试）

```bash
python autonomous\scheduler.py --mode continuous --interval 240
```

### 方式 3：Windows 任务计划（推荐，真正自主）

```powershell
# 创建任务计划程序
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "D:\openclaw\workspace\projects\ai-investor\autonomous\scheduler.py --mode once" `
  -WorkingDirectory "D:\openclaw\workspace\projects\ai-investor"

# 每 4 小时触发一次
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
  -RepetitionInterval (New-TimeSpan -Hours 4)

# 注册任务
Register-ScheduledTask -TaskName "AIInvestor-AutoCheck" `
  -Action $action `
  -Trigger $trigger `
  -Description "AI 投资系统自主检查 - 每 4 小时运行一次"
```

### 方式 4：每日完整分析

```powershell
# 每天晚上 8 点运行完整分析
$trigger = New-ScheduledTaskTrigger -Daily -At 8pm

Register-ScheduledTask -TaskName "AIInvestor-DailyAnalysis" `
  -Action $action `
  -Trigger $trigger `
  -Description "AI 投资系统每日完整分析"
```

---

## 📊 自主系统在做什么？

### 每 4 小时自动执行：

```
1. 🔍 自主检查
   - 检查最近决策质量（胜率如何？）
   - 检查当前策略有效性（还管用吗？）
   - 检测异常模式（连续失败？）

2. 🧠 自主评估
   - 计算系统置信度（我有多大把握？）
   - 判断是否需要调整（要不要改进？）

3. 🔄 自主改进（如果需要）
   - 生成新假设（是不是市场风格变了？）
   - 尝试新策略（换个方法试试）
   - 记录实验结果（这个有效/无效）

4. 📝 生成报告
   - 保存自主进化报告
   - 有异常时生成警报
```

### 每天晚上 8 点自动执行：

```
1. 📡 获取完整市场数据
2. 🤖 运行 AI 决策流程
3. 🧠 运行自主进化
4. 📊 生成完整报告
```

---

## 📂 生成的文件

```
logs/autonomous/
└── autonomous_20260305.log    # 自主运行日志

reports/evolution/
├── assessment_*.json          # 自主评估报告
├── autonomous_*.md            # 自主进化报告
└── alert_*.txt                # 异常警报（如有）

config/
├── evolution.json             # 进化配置
└── scheduler.json             # 调度配置
```

---

## 🔔 系统会主动通知你的情况

### 会通知：
- ⚠️  发现异常（连续失败、胜率过低）
- 🎉  有新发现（"我发现了一个新规律！"）
- 📊  每日总结（今天表现如何）

### 不会通知：
- ✅ 正常运行（一切顺利时保持安静）

---

## 💡 真正的"自主"体现在哪里？

| 传统方式 | 自主系统 |
|----------|----------|
| 等人运行 `python generate_ai_v4.py` | 自己每 4 小时检查 |
| 等人看报告 | 有异常才通知你 |
| 等人发现策略不行 | 自己检测并尝试改进 |
| 等人改代码 | 自己生成新假设、尝试新策略 |
| 等人记录结果 | 自己记录什么有效/无效 |
| 等人复盘 | 自己每日总结 |

---

## 🎯 系统的"思考"过程

```
每次自主检查，系统会问自己：

1. "我最近的判断准吗？"
   → 胜率 60%+ → 继续
   → 胜率<50% → 需要调整

2. "现在用的策略还管用吗？"
   → 有效 → 继续用
   → 无效 → 试试别的

3. "有没有异常情况？"
   → 连续失败 3 次 → 警报！降低仓位
   → 市场突变 → 重新评估

4. "我能变得更好吗？"
   → 生成新假设
   → 尝试新方法
   → 记录结果
```

---

## 📈 查看系统状态

```bash
# 查看最近的自主报告
Get-ChildItem reports/evolution/*.md | Sort-Object LastWriteTime -Descending | Select-Object -First 1

# 查看日志
Get-Content logs/autonomous/autonomous_20260305.log -Tail 50

# 查看配置
Get-Content config/scheduler.json
```

---

## ⚙️ 自定义配置

编辑 `config/scheduler.json`：

```json
{
  "enabled": true,                    // 是否启用自主模式
  "check_interval_hours": 4,          // 检查间隔（小时）
  "full_analysis_interval_hours": 24, // 完整分析间隔（小时）
  "alert_enabled": true,              // 是否发送警报
  "auto_adjust_threshold": 0.6        // 自动调整阈值（胜率低于此值触发）
}
```

---

## 🤖 系统进化示例

### 第 1 天
```
系统：我开始运行了！
置信度：50%（初始值）
策略：default
```

### 第 3 天（发现胜率低）
```
系统：最近胜率只有 40%，不太对劲...
自主发现：可能是市场风格变了
新假设：情绪极端值时应该反向操作
尝试：新策略 sentiment_contrarian
```

### 第 7 天（找到有效方法）
```
系统：新策略胜率 65%！有效！
置信度：70%（提升了）
策略：sentiment_contrarian
记录：这个策略在震荡市中有效
```

### 第 30 天（持续进化）
```
系统：我已经积累了 30 天的经验
有效策略：3 个
无效策略：5 个
发现规律：8 条
置信度：75%
```

---

## 🎯 这就是真正的"自主进化"

**不是等人来按按钮，而是：**
- 自己定时运行
- 自己评估好坏
- 自己尝试改进
- 自己积累经验
- 主动告诉你重要发现

**你只需要：**
- 偶尔看看报告
- 异常时介入调整
- 其他时间让它自己跑

---

*这才是真正的 AI Agent，不是工具*
