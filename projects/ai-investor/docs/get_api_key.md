# 获取有效的 Dashscope API Key

## 当前问题

提供的 API Key `sk-sp-98f06df238734bcea1559d473e6da6f5` 认证失败（401 InvalidApiKey）。

## 正确获取方式

### 步骤 1: 访问阿里云百炼控制台

**网址：** https://bailian.console.aliyun.com/

### 步骤 2: 登录/注册

- 使用阿里云账号登录
- 如果没有账号，需要注册并完成实名认证

### 步骤 3: 开通服务

1. 进入「模型服务」或「API-KEY 管理」
2. 开通「通义千问」服务
3. 确认计费方式（按量付费）

### 步骤 4: 创建 API Key

1. 点击「创建新的 API-KEY」
2. 复制生成的 Key（格式：`sk-xxxxxxxxxxxxxxxx`）

### 步骤 5: 充值账户

**重要：** 确保阿里云账户有余额！

- 通义千问按 token 计费
- qwen-plus 价格：输入 ¥0.004/1K tokens，输出 ¥0.012/1K tokens
- 建议充值 ¥10-50 元即可使用很长时间

### 步骤 6: 验证 API Key

```bash
python -c "import dashscope; dashscope.api_key='sk-你的新 Key'; from dashscope import Generation; resp = Generation.call(model='qwen-plus', messages=[{'role':'user','content':'你好'}]); print('状态:', resp.status_code)"
```

预期输出：`状态：200`

---

## 价格参考

| 模型 | 输入价格 | 输出价格 | 推荐 |
|------|----------|----------|------|
| qwen-turbo | ¥0.002/1K | ¥0.006/1K | 快速测试 |
| qwen-plus | ¥0.004/1K | ¥0.012/1K | ⭐ 推荐 |
| qwen-max | ¥0.04/1K | ¥0.12/1K | 复杂任务 |

**每日成本估算：**
- 智能体系统每日运行 1 次
- 每次约 2000-3000 tokens
- 日成本：¥0.05-0.10 元

---

## 常见问题

### Q: API Key 格式不对？
A: 正确格式：`sk-` 开头，后跟 32 位字母数字

### Q: 401 认证失败？
A: 可能原因：
1. Key 复制错误（多了空格）
2. Key 已过期/被删除
3. 账户欠费
4. 服务未开通

### Q: 429 频率限制？
A: 降低调用频率或提升配额

### Q: 500 服务器错误？
A: 阿里云服务暂时不可用，稍后重试

---

## 获取帮助

- 阿里云文档：https://help.aliyun.com/product/42154.html
- 百炼控制台：https://bailian.console.aliyun.com/
- API 文档：https://help.aliyun.com/zh/dashscope/

---

**获取有效 API Key 后，系统将启用真正的 AI 智能体功能！**
