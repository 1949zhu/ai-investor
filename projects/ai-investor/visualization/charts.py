"""
决策可视化 - 生成图表和摘要
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class DecisionVisualizer:
    """决策可视化器"""
    
    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / "reports" / "visualizations"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_ascii_chart(self, data: List[float], labels: List[str] = None,
                              title: str = "", width: int = 60, height: int = 15) -> str:
        """生成 ASCII 图表"""
        if not data:
            return "无数据"
        
        min_val = min(data)
        max_val = max(data)
        range_val = max_val - min_val if max_val != min_val else 1
        
        # 规范化数据
        normalized = [(v - min_val) / range_val * (height - 1) for v in data]
        
        # 生成图表
        lines = []
        if title:
            lines.append(f"{' ' * (width//2 - len(title)//2)}{title}")
            lines.append("")
        
        # Y 轴标签
        lines.append(f"  {max_val:.2f} ┤")
        
        # 图表主体
        for row in range(height - 1, -1, -1):
            line = f"        │" if row != height//2 else f"  {min_val:.2f} ┤"
            for col, norm_val in enumerate(normalized):
                if int(norm_val) == row:
                    line += "█"
                elif int(norm_val) > row:
                    line += "│"
                else:
                    line += " "
            lines.append(line)
        
        # X 轴
        lines.append(f"        └" + "─" * len(data))
        
        # X 轴标签
        if labels and len(labels) >= len(data):
            label_line = "         "
            for i, label in enumerate(labels[::max(1, len(labels)//10)]):
                label_line += f"{label[:4]:<5}"
            lines.append(label_line)
        
        return "\n".join(lines)
    
    def generate_summary_table(self, decisions: List[Dict]) -> str:
        """生成决策摘要表"""
        if not decisions:
            return "暂无决策记录"
        
        lines = []
        lines.append("┌────────────┬──────────┬─────────┬──────────┬────────┐")
        lines.append("│ 日期       │ 市场状态 │ 决策    │ 结果     │ 收益   │")
        lines.append("├────────────┼──────────┼─────────┼──────────┼────────┤")
        
        for dec in decisions[:10]:
            date = dec.get('date', '未知')[:10]
            market = dec.get('market_state', '未知')[:8]
            decision = dec.get('decision', '')[:20] + "..." if len(dec.get('decision', '')) > 20 else dec.get('decision', '')
            outcome = dec.get('outcome', '待验证')[:8]
            reflection = dec.get('reflection', '')
            
            # 尝试从 reflection 提取收益
            收益 = "-"
            if reflection and "收益" in reflection:
                try:
                    收益 = reflection.split("收益")[1].split("%")[0] + "%"
                except:
                    收益 = "待计算"
            
            lines.append(f"│ {date:<10} │ {market:<8} │ {decision:<20} │ {outcome:<8} │ {收益:<6} │")
        
        lines.append("└────────────┴──────────┴─────────┴──────────┴────────┘")
        
        return "\n".join(lines)
    
    def generate_performance_chart(self, returns: List[float]) -> str:
        """生成收益曲线图"""
        if not returns:
            return "无数据"
        
        # 计算累计收益
        cumulative = []
        total = 1.0
        for r in returns:
            total *= (1 + r)
            cumulative.append(total - 1)
        
        # 生成标签
        labels = [f"D{i+1}" for i in range(len(cumulative))]
        
        return self.generate_ascii_chart(
            cumulative,
            labels=labels,
            title="累计收益曲线",
            width=60,
            height=12
        )
    
    def generate_market_sentiment_gauge(self, score: float) -> str:
        """生成情绪仪表盘"""
        score = max(0, min(100, score))
        
        width = 50
        position = int(score / 100 * width)
        
        lines = []
        lines.append("市场情绪仪表盘")
        lines.append("")
        lines.append(f"  悲观 {'─' * position}●{'─' * (width - position)} 乐观")
        lines.append(f"       0        50       100")
        lines.append("")
        
        # 情绪标签
        if score >= 80:
            label = "极度乐观"
        elif score >= 60:
            label = "乐观"
        elif score >= 40:
            label = "中性"
        elif score >= 20:
            label = "悲观"
        else:
            label = "极度悲观"
        
        lines.append(f"  当前情绪：{label} ({score:.1f}分)")
        
        return "\n".join(lines)
    
    def generate_decision_tree(self, decision: Dict) -> str:
        """生成决策树"""
        lines = []
        lines.append("决策分析树")
        lines.append("")
        lines.append(f"├─ 市场状态：{decision.get('market_state', '未知')}")
        lines.append(f"├─ 决策内容")
        lines.append(f"│  └─ {decision.get('decision', '')[:100]}")
        lines.append(f"├─ 决策理由")
        lines.append(f"│  └─ {decision.get('reasoning', '')[:100]}")
        lines.append(f"├─ 结果")
        lines.append(f"│  └─ {decision.get('outcome', '待验证')}")
        lines.append(f"└─ 反思")
        lines.append(f"   └─ {decision.get('reflection', '暂无')}")
        
        return "\n".join(lines)
    
    def generate_full_report(self, decisions: List[Dict], performance_data: Dict = None) -> str:
        """生成完整可视化报告"""
        lines = []
        
        # 标题
        lines.append("=" * 70)
        lines.append("              AI 投资决策可视化报告")
        lines.append(f"              生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("=" * 70)
        lines.append("")
        
        # 决策摘要表
        lines.append("📊 决策摘要")
        lines.append("")
        lines.append(self.generate_summary_table(decisions))
        lines.append("")
        
        # 情绪仪表盘
        if decisions:
            latest = decisions[0]
            # 简单情绪评分
            market_state = latest.get('market_state', '')
            if '乐观' in market_state:
                score = 75
            elif '悲观' in market_state:
                score = 25
            else:
                score = 50
            
            lines.append("📈 市场情绪")
            lines.append("")
            lines.append(self.generate_market_sentiment_gauge(score))
            lines.append("")
        
        # 绩效图表
        if performance_data and 'returns' in performance_data:
            lines.append("📉 收益曲线")
            lines.append("")
            lines.append(self.generate_performance_chart(performance_data['returns']))
            lines.append("")
        
        # 统计信息
        lines.append("📋 统计信息")
        lines.append("")
        if decisions:
            lines.append(f"  总决策数：{len(decisions)}")
            verified = sum(1 for d in decisions if d.get('outcome') != '待验证')
            lines.append(f"  已验证：{verified}")
            lines.append(f"  待验证：{len(decisions) - verified}")
        
        if performance_data:
            if 'win_rate' in performance_data:
                lines.append(f"  胜率：{performance_data['win_rate']*100:.1f}%")
            if 'avg_return' in performance_data:
                lines.append(f"  平均收益：{performance_data['avg_return']*100:.2f}%")
        
        lines.append("")
        lines.append("=" * 70)
        
        report = "\n".join(lines)
        
        # 保存报告
        output_file = self.output_dir / f"visualization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report, str(output_file)


if __name__ == "__main__":
    print("测试决策可视化...\n")
    
    visualizer = DecisionVisualizer()
    
    # 模拟决策数据
    decisions = [
        {
            'date': '2026-03-05',
            'market_state': '震荡市',
            'decision': '买入中国平安 (601318.SH)',
            'reasoning': '低估值 + 高股息',
            'outcome': '收益 2.5%',
            'reflection': '收益 2.5%，符合预期'
        },
        {
            'date': '2026-03-04',
            'market_state': '乐观',
            'decision': '买入贵州茅台 (600519.SH)',
            'reasoning': '消费复苏',
            'outcome': '收益 5.2%',
            'reflection': '收益 5.2%，超预期'
        },
        {
            'date': '2026-03-03',
            'market_state': '悲观',
            'decision': '减仓',
            'reasoning': '避险',
            'outcome': '避免损失 3%',
            'reflection': '成功避险'
        }
    ]
    
    # 生成报告
    performance_data = {
        'returns': [0.025, 0.052, -0.03, 0.015, 0.042],
        'win_rate': 0.75,
        'avg_return': 0.021
    }
    
    report, output_file = visualizer.generate_full_report(decisions, performance_data)
    
    print(report)
    print(f"\n报告已保存：{output_file}")
