"""
宏观分析师智能体 - LLM 增强版

使用真实 LLM 进行宏观经济分析
"""

import os
from typing import Optional, Dict
from datetime import datetime


class MacroAnalyst:
    """
    宏观分析师智能体
    
    职责：
    - 分析宏观经济数据
    - 解读政策动向
    - 判断市场情绪
    - 输出宏观分析报告
    """
    
    def __init__(self, llm=None, memory=None):
        self.memory = memory
        self.llm = llm
        self.api_key = os.environ.get("DASHSCOPE_API_KEY", "")
    
    def analyze(self, context: Dict = None) -> str:
        """
        执行宏观分析（使用 LLM）
        """
        return self._llm_analyze(context)
    
    def _llm_analyze(self, context: Dict = None) -> str:
        """使用 LLM 进行宏观分析"""
        import dashscope
        from dashscope import Generation
        
        dashscope.api_key = self.api_key
        
        date = datetime.now().strftime("%Y-%m-%d")
        
        # 构建分析提示
        prompt = f"""你是一位经验丰富的宏观经济分析师，曾在大投行担任首席经济学家。

当前日期：{date}

请分析当前中国宏观经济环境和 A 股市场状态，包括：
1. 经济基本面（GDP、PMI、通胀等）
2. 政策环境（货币政策、财政政策、产业政策）
3. 国际环境（全球经济、贸易、地缘政治）
4. 市场情绪（成交量、资金流向、投资者信心）
5. 市场状态判断（牛市/熊市/震荡）
6. 配置建议（超配/标配/低配的行业）

要求：
- 分析客观、专业
- 给出明确的判断和理由
- 用中文输出，格式清晰

请以专业分析师的口吻撰写一份完整的宏观分析报告。
"""
        
        try:
            # 调用 LLM
            response = Generation.call(
                model='qwen-plus',
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            
            if response.status_code == 200:
                report = response.output.text
                
                # 提取市场状态
                market_state = self._extract_market_state(report)
                
                # 保存到记忆
                if self.memory:
                    self.memory.set_market_state(market_state)
                    self.memory.add_context("macro_report", report)
                
                return f"# 宏观经济分析报告（AI 生成）\n\n{report}"
            else:
                print(f"⚠️ LLM 调用失败：{response.status_code}")
                return self._fallback_analyze()
                
        except Exception as e:
            print(f"⚠️ LLM 分析异常：{e}")
            return self._fallback_analyze()
    
    def _extract_market_state(self, report: str) -> str:
        """从报告中提取市场状态判断"""
        # 简单关键词提取
        if "牛市" in report or "上涨" in report:
            return "牛市"
        elif "熊市" in report or "下跌" in report:
            return "熊市"
        else:
            return "震荡"
    
    def _fallback_analyze(self) -> str:
        """降级分析（当 LLM 不可用时）"""
        date = datetime.now().strftime("%Y-%m-%d")
        report = f"""# 宏观经济分析报告

**日期：** {date}

## 市场状态判断
**震荡上行**

### 判断依据
1. 经济基本面稳定
2. 政策环境友好
3. 估值处于合理区间

## 配置建议
- 超配：科技、消费、医药
- 标配：金融、制造
- 低配：周期、地产

---
*注：LLM 服务不可用，使用简化分析*
"""
        if self.memory:
            self.memory.set_market_state("震荡上行")
        return report
    
    def get_market_state(self) -> str:
        """获取当前市场状态判断"""
        if self.memory:
            return self.memory.get_market_state() or "未知"
        return "未知"
