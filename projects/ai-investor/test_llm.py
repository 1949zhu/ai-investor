"""
测试 LLM 调用
"""

import os
import dashscope
from dashscope import Generation

# 设置 API Key
os.environ['DASHSCOPE_API_KEY'] = 'sk-fb6aa9235b6b4627aa2ac5f7295db04c'
dashscope.api_key = os.environ['DASHSCOPE_API_KEY']

print("测试 LLM 调用...")
print(f"API Key: {dashscope.api_key[:15]}...")

# 简单测试
response = Generation.call(
    model='qwen-plus',
    messages=[{'role': 'user', 'content': '用一句话介绍你自己'}],
    temperature=0.5,
    max_tokens=100
)

print(f"状态码：{response.status_code}")

if response.status_code == 200:
    print(f"回复：{response.output.text}")
else:
    print(f"错误：{response}")
