"""
LLM 服务层 - 统一接口

提供标准化的 LLM 调用接口，支持多模型切换
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import json
from pathlib import Path


class LLMService(ABC):
    """LLM 服务基础接口"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """通用文本生成"""
        pass
    
    @abstractmethod
    def generate_json(self, prompt: str, schema: Optional[dict] = None) -> dict:
        """结构化输出（JSON）"""
        pass
    
    @abstractmethod
    def analyze(self, context: str, task: str) -> dict:
        """分析任务（返回结构化结果）"""
        pass


def get_llm_service(provider: str = "dashscope", **kwargs) -> LLMService:
    """获取 LLM 服务实例"""
    if provider == "dashscope":
        from .dashscope import DashscopeService
        return DashscopeService(**kwargs)
    elif provider == "openai":
        from .openai import OpenAIService
        return OpenAIService(**kwargs)
    else:
        raise ValueError(f"Unknown provider: {provider}")
