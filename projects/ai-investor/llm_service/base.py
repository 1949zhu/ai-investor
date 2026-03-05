"""
LLM 服务基础接口定义
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class LLMService(ABC):
    """LLM 服务基础接口"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        通用文本生成
        
        Args:
            prompt: 输入提示词
            **kwargs: 额外参数
            
        Returns:
            生成的文本
        """
        pass
    
    @abstractmethod
    def generate_json(self, prompt: str, schema: Optional[dict] = None) -> dict:
        """
        结构化输出（JSON）
        
        Args:
            prompt: 输入提示词
            schema: JSON Schema（可选）
            
        Returns:
            解析后的 JSON 对象
        """
        pass
    
    @abstractmethod
    def analyze(self, context: str, task: str) -> dict:
        """
        分析任务
        
        Args:
            context: 上下文信息
            task: 分析任务描述
            
        Returns:
            结构化分析结果
        """
        pass
