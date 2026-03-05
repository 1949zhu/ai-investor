# 配置 LLM API Key

## 获取 API Key

1. 访问阿里云百炼控制台：https://bailian.console.aliyun.com/
2. 登录/注册阿里云账号
3. 进入「API-KEY 管理」
4. 创建新的 API Key
5. 复制 Key 到配置文件

## 配置方式

### 方式 1: 环境变量（推荐）

**Windows:**
```powershell
# 临时设置（当前会话）
$env:DASHSCOPE_API_KEY="sk-your-api-key-here"

# 永久设置
[System.Environment]::SetEnvironmentVariable("DASHSCOPE_API_KEY", "sk-your-api-key-here", "User")
```

**Linux/Mac:**
```bash
# 临时设置
export DASHSCOPE_API_KEY="sk-your-api-key-here"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export DASHSCOPE_API_KEY="sk-your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

### 方式 2: .env 文件

1. 复制示例文件：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的 API Key：
```
DASHSCOPE_API_KEY=sk-your-api-key-here
```

3. 在代码中加载：
```python
from dotenv import load_dotenv
load_dotenv()
```

## 验证配置

```bash
# 检查环境变量
echo $DASHSCOPE_API_KEY  # Linux/Mac
echo %DASHSCOPE_API_KEY%  # Windows CMD
$env:DASHSCOPE_API_KEY  # PowerShell

# 测试 API
python -c "import dashscope; dashscope.api_key='YOUR_KEY'; print(dashscope.Generation.call(model='qwen-plus', messages=[{'role':'user','content':'hi'}]))"
```

## 模型选择

| 模型 | 输入价格 | 输出价格 | 适用场景 |
|------|----------|----------|----------|
| qwen-turbo | ¥0.002/1K | ¥0.006/1K | 快速响应 |
| qwen-plus | ¥0.004/1K | ¥0.012/1K | 平衡（推荐）|
| qwen-max | ¥0.04/1K | ¥0.12/1K | 复杂任务 |

## 成本控制

智能体系统已配置以下成本控制措施：

- ✅ Token 缓存（避免重复调用）
- ✅ 每日预算限制（100K tokens ≈ ¥0.5-1/天）
- ✅ 简化模式（API 不可用时降级）

## 当前状态

```
✅ CrewAI 已安装 (v1.10.1)
⚠️ API Key 需更新 (当前 Key 认证失败)
✅ 简化模式可用（无 LLM 也可运行）
```

## 故障排除

### 401 认证失败
- 检查 API Key 是否正确
- 确认 API Key 未过期
- 检查阿里云账号余额

### 429 频率限制
- 降低调用频率
- 启用缓存
- 升级 API 配额

### 500 服务器错误
- 检查阿里云服务状态
- 稍后重试
- 使用简化模式
