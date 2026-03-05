"""
LLM 服务配置
"""

import os
from pathlib import Path
from typing import Optional


class LLMConfig:
    """LLM 配置管理"""
    
    # 提供商配置
    PROVIDER = os.environ.get("LLM_PROVIDER", "dashscope")
    
    # Dashscope 配置
    DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
    DASHSCOPE_MODEL = os.environ.get("DASHSCOPE_MODEL", "qwen-plus")
    
    # 通用配置
    MAX_TOKENS = 2000
    TEMPERATURE = 0.7
    TIMEOUT = 60
    
    # 缓存配置
    CACHE_ENABLED = True
    CACHE_DIR = Path(__file__).parent.parent / "storage" / "llm_cache"
    
    # 成本限制
    DAILY_TOKEN_BUDGET = 100000  # 每日 token 预算
    MAX_RETRIES = 3
    
    @classmethod
    def validate(cls) -> bool:
        """验证配置是否有效"""
        if cls.PROVIDER == "dashscope" and not cls.DASHSCOPE_API_KEY:
            print("⚠️ 未设置 DASHSCOPE_API_KEY 环境变量")
            print("  请在环境变量中设置或使用模拟模式")
            return False
        return True
    
    @classmethod
    def get_service_config(cls) -> dict:
        """获取服务配置字典"""
        return {
            "provider": cls.PROVIDER,
            "api_key": cls.DASHSCOPE_API_KEY,
            "model": cls.DASHSCOPE_MODEL,
            "max_tokens": cls.MAX_TOKENS,
            "temperature": cls.TEMPERATURE,
            "cache_dir": str(cls.CACHE_DIR) if cls.CACHE_ENABLED else None
        }


# 创建缓存目录
if LLMConfig.CACHE_ENABLED:
    LLMConfig.CACHE_DIR.mkdir(parents=True, exist_ok=True)
