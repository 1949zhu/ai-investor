"""
Dashscope (Qwen) LLM 服务实现

使用阿里云 Dashscope API 调用 Qwen 模型
文档：https://help.aliyun.com/zh/dashscope/
"""

import os
import json
import time
from typing import Optional, Dict, Any, List
from pathlib import Path

try:
    import dashscope
    from dashscope import Generation
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False
    print("⚠️ dashscope 未安装，运行：pip install dashscope")

from .base import LLMService


class DashscopeService(LLMService):
    """Dashscope Qwen 服务"""
    
    # 默认模型配置
    DEFAULT_MODEL = "qwen-plus"
    DEFAULT_MAX_TOKENS = 2000
    DEFAULT_TEMPERATURE = 0.7
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = None,
        max_tokens: int = None,
        temperature: float = None,
        cache_dir: str = None
    ):
        """
        初始化 Dashscope 服务
        
        Args:
            api_key: Dashscope API Key（不传则从环境变量读取）
            model: 模型名称
            max_tokens: 最大输出 token 数
            temperature: 温度参数（0-1，越低越确定）
            cache_dir: 缓存目录（用于降低成本）
        """
        self.api_key = api_key or os.environ.get("DASHSCOPE_API_KEY")
        self.model = model or self.DEFAULT_MODEL
        self.max_tokens = max_tokens or self.DEFAULT_MAX_TOKENS
        self.temperature = temperature or self.DEFAULT_TEMPERATURE
        self.cache_dir = Path(cache_dir) if cache_dir else None
        
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.api_key:
            print("⚠️ 未设置 DASHSCOPE_API_KEY，将使用模拟模式")
        
        if DASHSCOPE_AVAILABLE and self.api_key:
            dashscope.api_key = self.api_key
            print(f"✅ Dashscope 服务已初始化（模型：{self.model}）")
    
    def _get_cache_key(self, prompt: str) -> str:
        """生成缓存键"""
        import hashlib
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """从缓存获取"""
        if not self.cache_dir:
            return None
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def _save_to_cache(self, key: str, data: Any):
        """保存到缓存"""
        if not self.cache_dir:
            return
        cache_file = self.cache_dir / f"{key}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        通用文本生成
        
        Args:
            prompt: 输入提示词
            **kwargs: 额外参数
            
        Returns:
            生成的文本
        """
        # 检查缓存
        cache_key = self._get_cache_key(prompt)
        cached = self._get_from_cache(cache_key)
        if cached:
            print(f"  [缓存命中] {cache_key[:8]}...")
            return cached
        
        if not self.api_key or not DASHSCOPE_AVAILABLE:
            # 模拟模式
            return self._mock_generate(prompt)
        
        try:
            response = Generation.call(
                model=self.model,
                prompt=prompt,
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                temperature=kwargs.get('temperature', self.temperature),
                result_format='message'
            )
            
            if response.status_code == 200:
                result = response.output.choices[0].message.content
                self._save_to_cache(cache_key, result)
                return result
            else:
                print(f"⚠️ Dashscope API 错误：{response.code} - {response.message}")
                return self._mock_generate(prompt)
                
        except Exception as e:
            print(f"⚠️ LLM 调用失败：{e}")
            return self._mock_generate(prompt)
    
    def generate_json(self, prompt: str, schema: Optional[dict] = None) -> dict:
        """
        结构化输出（JSON）
        
        Args:
            prompt: 输入提示词
            schema: JSON Schema（可选，用于验证）
            
        Returns:
            解析后的 JSON 对象
        """
        # 添加 JSON 输出指令
        json_prompt = f"""{prompt}

请严格按照 JSON 格式输出，不要包含任何其他文字。输出应该是一个有效的 JSON 对象，可以直接被解析。"""
        
        response_text = self.generate(json_prompt)
        
        # 提取 JSON 部分
        json_str = self._extract_json(response_text)
        
        try:
            result = json.loads(json_str)
            return result
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON 解析失败：{e}")
            print(f"原始输出：{json_str[:500]}...")
            return {}
    
    def analyze(self, context: str, task: str) -> dict:
        """
        分析任务
        
        Args:
            context: 上下文信息
            task: 分析任务描述
            
        Returns:
            结构化分析结果
        """
        prompt = f"""请分析以下信息，完成指定任务。

【上下文】
{context}

【任务】
{task}

请输出结构化的分析结果，使用 JSON 格式。"""
        
        return self.generate_json(prompt)
    
    def _extract_json(self, text: str) -> str:
        """从文本中提取 JSON"""
        # 尝试找到 JSON 块
        import re
        
        # 匹配 ```json ... ``` 块
        match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return match.group(1)
        
        # 匹配 ``` ... ``` 块
        match = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return match.group(1)
        
        # 匹配 { ... } 块
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return match.group(0)
        
        # 返回原文
        return text
    
    def _mock_generate(self, prompt: str) -> str:
        """
        模拟生成（无 API key 时）
        
        返回错误状态，不使用模拟数据
        """
        print("  ❌ LLM 服务不可用：未配置有效 API Key")
        
        # 返回错误标识
        return json.dumps({
            "status": "error",
            "error": "LLM 服务不可用",
            "error_details": "未配置有效的 DASHSCOPE_API_KEY",
            "message": "请设置环境变量 DASHSCOPE_API_KEY 后重试"
        }, ensure_ascii=False)
