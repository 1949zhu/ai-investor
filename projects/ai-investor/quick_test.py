"""
快速测试 - 单个智能体调用
"""
import os
os.environ['DASHSCOPE_API_KEY'] = 'sk-fb6aa9235b6b4627aa2ac5f7295db04c'

import dashscope
from dashscope import Generation

print("调用 LLM...")
resp = Generation.call(model='qwen-plus', messages=[{'role':'user','content':'用 50 字总结当前 A 股市场'}])
print(f"状态：{resp.status_code}")
if resp.status_code == 200:
    print(f"回复：{resp.output.text}")
