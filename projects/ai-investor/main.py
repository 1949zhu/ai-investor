"""
AI 投资顾问系统 - 主入口（LLM 增强版）

整合数据、策略、回测、报告模块
提供完整的投资分析和决策能力

LLM 增强功能：
- AI 策略生成
- 情绪分析  
- 报告增强
- 自优化
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from data.baostock_fetcher import BaoStockDataFetcher
from strategy.generator import StrategyGenerator
from strategy.llm_generator import LLMStrategyGenerator
from backtest.engine import BacktestEngine
from report.generator import ReportGenerator
from report.llm_enhancer import LLMReportEnhancer
from sentiment.analyzer import SentimentAnalyzer
from optimizer.llm_optimizer import LLMOptimizer
from news.fetcher import FinancialNewsFetcher
from datetime import datetime, timedelta


class AIInvestmentAdvisor:
    """
    AI 投资顾问系统主类（LLM 增强版）
    """
    
    def __init__(self, workspace: str = None, enable_llm: bool = True):
        if workspace is None:
            workspace = Path(__file__).parent
        self.workspace = Path(workspace)
        self.enable_llm = enable_llm
        
        # 初始化基础模块
        self.data_fetcher = BaoStockDataFetcher(str(self.workspace / "storage" / "ashare.db"))
        self.strategy_generator = StrategyGenerator(str(self.workspace / "storage" / "ashare.db"))
        self.backtest_engine = BacktestEngine(str(self.workspace / "storage" / "ashare.db"))
        self.report_generator = ReportGenerator(str(self.workspace / "reports"))
        
        # 初始化 LLM 模块（可选）
        if self.enable_llm:
            try:
                self.llm_strategy_gen = LLMStrategyGenerator()
                self.llm_report_enhancer = LLMReportEnhancer()
                self.news_fetcher = FinancialNewsFetcher()
                self.sentiment_analyzer = SentimentAnalyzer(news_fetcher=self.news_fetcher)
                self.llm_optimizer = LLMOptimizer()
                print("🤖 AI 投资顾问系统已初始化（LLM 增强版 + 实时新闻）")
            except Exception as e:
                print(f"⚠️ LLM 模块初始化失败：{e}，使用基础版")
                self.enable_llm = False
                self.llm_strategy_gen = None
                self.llm_report_enhancer = None
                self.news_fetcher = None
                self.sentiment_analyzer = None
                self.llm_optimizer = None
                print("🤖 AI 投资顾问系统已初始化（基础版）")
        else:
            self.llm_strategy_gen = None
            self.llm_report_enhancer = None
            self.news_fetcher = None
            self.sentiment_analyzer = None
            self.llm_optimizer = None
            print("🤖 AI 投资顾问系统已初始化（基础版）")
    
    def run_daily_task(self, enable_llm_features: bool = True):
        """运行每日任务（LLM 增强版）"""
        print("\n" + "="*60)
        print("📅 每日任务开始（LLM 增强版）")
        print("="*60)
        
        # 1. 分析市场
        print("\n1️⃣ 分析市场...")
        result = self.analyze_and_recommend()
        
        # 2. LLM 情绪分析（可选）
        if enable_llm_features and self.sentiment_analyzer:
            print("\n2️⃣ LLM 实时情绪分析...")
            try:
                # 获取并分析实时新闻情绪
                sentiment = self.sentiment_analyzer.analyze_realtime_news_sentiment(limit=30)
                result['sentiment'] = sentiment
                
                if sentiment.get('status') == 'error':
                    print(f"  ❌ 情绪分析失败：{sentiment.get('error', '未知错误')}")
                    print(f"     详情：{sentiment.get('error_details', '')}")
                else:
                    print(f"  ✅ 市场情绪：{sentiment.get('sentiment_label', 'N/A')}")
                    print(f"  ✅ 情绪分数：{sentiment.get('overall_sentiment', 0):.2f}")
                    print(f"  ✅ 新闻来源：{sentiment.get('news_sources', [])}")
            except Exception as e:
                print(f"  ❌ 情绪分析异常：{e}")
        
        # 3. 生成报告
        print("\n3️⃣ 生成报告...")
        report = self._generate_enhanced_report(result)
        result['report'] = report
        print(f"  报告已保存至：{self.workspace / 'reports'}")
        
        # 4. 记录日志
        self._log_daily_result(result)
        
        print("\n✅ 每日任务完成")
        return result
    
    def analyze_and_recommend(self, symbols: list = None) -> dict:
        """分析市场并生成投资建议"""
        print("\n🔍 开始分析市场...")
        
        # 获取策略（优先 LLM 生成的）
        if self.enable_llm and self.llm_strategy_gen:
            llm_strategies = self.llm_strategy_gen.load_strategies()
            if llm_strategies:
                print(f"  加载 {len(llm_strategies)} 个 LLM 生成策略")
                strategies = llm_strategies
            else:
                strategies = self.strategy_generator.get_all_builtin_strategies()
        else:
            strategies = self.strategy_generator.get_all_builtin_strategies()
        
        # 如果没有指定股票，从数据库获取
        if symbols is None:
            symbols = self._get_candidate_stocks()
        
        print(f"  分析股票：{symbols}")
        
        # 对每个策略进行回测
        best_strategy = None
        best_results = None
        all_results = []
        
        for strategy in strategies:
            print(f"\n  回测策略：{strategy.get('name', '未知')}")
            results = self.backtest_engine.run_backtest(
                strategy=strategy,
                symbols=symbols,
                start_date=(datetime.now() - timedelta(days=365)).strftime("%Y%m%d"),
                end_date=datetime.now().strftime("%Y%m%d")
            )
            results['strategy'] = strategy
            all_results.append(results)
            
            if best_results is None or results.get('total_return_pct', 0) > best_results.get('total_return_pct', 0):
                best_strategy = strategy
                best_results = results
        
        # 生成投资建议
        recommendation = self._generate_recommendation(best_strategy, best_results, symbols)
        
        return {
            'strategy': best_strategy,
            'backtest_results': best_results,
            'recommendation': recommendation,
            'all_strategy_results': all_results,
            'symbols': symbols
        }
    
    def _get_candidate_stocks(self, limit: int = 10) -> list:
        """获取候选股票列表"""
        return ["000001", "000002", "600000", "600036", "000651"][:limit]
    
    def _generate_recommendation(self, strategy: dict, results: dict, symbols: list) -> dict:
        """生成交易建议"""
        if strategy is None:
            return {'action': '观望', 'position': '0%', 'rationale': '暂无合适策略'}
        
        # 根据策略类型生成建议
        strategy_name = strategy.get('name', '')
        if '均值回归' in strategy_name:
            return {
                'action': '分批买入',
                'position': '10-20%',
                'holding_period': '短线（1-2 周）',
                'rationale': '均值回归策略适合在市场波动时操作'
            }
        elif '动量' in strategy_name:
            return {
                'action': '突破买入',
                'position': '10-15%',
                'holding_period': '短线（3-5 天）',
                'rationale': '动量策略需要快速反应'
            }
        else:
            return {
                'action': '价值配置',
                'position': '20-30%',
                'holding_period': '中线（1-3 个月）',
                'rationale': '价值投资需要耐心，建议长期持有'
            }
    
    def _generate_enhanced_report(self, result: dict) -> str:
        """生成增强报告"""
        strategy = result.get('strategy', {})
        backtest = result.get('backtest_results', {})
        
        # 基础报告
        stock_analysis = {
            'symbols': [{'symbol': sym, 'name': sym, 'reason': '基于策略筛选'} for sym in result.get('symbols', [])[:5]]
        }
        
        report_path = self.report_generator.generate_investment_report(
            strategy_name=strategy.get('name', '未知'),
            stock_analysis=stock_analysis,
            recommendation=result.get('recommendation', {}),
            backtest_results=backtest
        )
        
        # LLM 增强报告（可选）
        if self.enable_llm and self.llm_report_enhancer:
            try:
                print("  🧠 LLM 正在增强报告...")
                result = self.llm_report_enhancer.enhance_report({
                    'strategy': strategy,
                    'backtest': backtest,
                    'stocks': stock_analysis['symbols']
                })
                
                if result.get('status') == 'error':
                    print(f"  ❌ LLM 报告增强失败：{result.get('error', '未知错误')}")
                else:
                    # 将增强内容追加到报告
                    with open(report_path, 'a', encoding='utf-8') as f:
                        f.write("\n\n---\n\n")
                        f.write("## 🧠 AI 投资逻辑深度分析\n\n")
                        f.write(result.get('content', ''))
                    print("  ✅ 报告已 LLM 增强")
            except Exception as e:
                print(f"  ❌ LLM 增强异常：{e}")
        
        return report_path
    
    def _log_daily_result(self, result: dict):
        """记录每日结果"""
        log_path = self.workspace / "logs" / f"daily_{datetime.now().strftime('%Y%m%d')}.md"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"# 每日运行日志\n\n")
            f.write(f"日期：{datetime.now().isoformat()}\n\n")
            f.write(f"策略：{result.get('strategy', {}).get('name', 'N/A')}\n\n")
            f.write(f"回测结果：\n")
            for key, value in result.get('backtest_results', {}).items():
                f.write(f"- {key}: {value}\n")
    
    def generate_llm_strategy(self, market_context: str = "") -> dict:
        """使用 LLM 生成新策略"""
        if not self.llm_strategy_gen:
            print("⚠️ LLM 策略生成器未启用")
            return {}
        
        print("\n🧠 使用 LLM 生成新策略...")
        
        # 市场数据特征
        market_data = {
            "market_trend": "震荡上行",
            "volatility": "中等",
            "avg_daily_change": 0.02,
            "description": market_context or "当前 A 股市场"
        }
        
        strategy = self.llm_strategy_gen.generate_strategy(market_data, market_context)
        print(f"✅ 新策略已生成：{strategy.get('name', '未知')}")
        
        return strategy
    
    def optimize_strategy(self, strategy_id: str = None):
        """优化策略"""
        if not self.llm_optimizer:
            print("⚠️ LLM 优化器未启用")
            return
        
        print("\n🧠 开始策略优化...")
        
        # 加载策略
        if self.llm_strategy_gen:
            strategies = self.llm_strategy_gen.load_strategies()
            if strategies:
                strategy = strategies[0]  # 优化第一个策略
                
                # 模拟回测结果
                backtest_result = {
                    'total_return_pct': 15.5,
                    'annual_return_pct': 14.8,
                    'sharpe_ratio': 1.2,
                    'max_drawdown_pct': 5.3,
                    'win_rate_pct': 55.0,
                    'trade_count': 25,
                    'evaluation': 'ACCEPTABLE'
                }
                
                # 分析失败原因
                analysis = self.llm_optimizer.analyze_failure(strategy, backtest_result)
                print(f"  分析完成：{analysis.get('primary_failure_reason', 'N/A')}")
                
                # 提出改进建议
                improvement = self.llm_optimizer.suggest_improvements(strategy, analysis)
                print(f"  改进方案已生成")
            else:
                print("  暂无 LLM 策略可优化")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI 投资顾问系统（LLM 增强版）')
    parser.add_argument('--init-data', action='store_true', help='初始化数据')
    parser.add_argument('--analyze', action='store_true', help='分析并生成建议')
    parser.add_argument('--daily', action='store_true', help='运行每日任务')
    parser.add_argument('--llm-strategy', action='store_true', help='生成 LLM 策略')
    parser.add_argument('--optimize', action='store_true', help='优化策略')
    parser.add_argument('--stocks', type=str, nargs='+', help='指定股票列表')
    parser.add_argument('--no-llm', action='store_true', help='禁用 LLM 功能')
    
    args = parser.parse_args()
    
    # 初始化系统
    advisor = AIInvestmentAdvisor(enable_llm=not args.no_llm)
    
    if args.init_data:
        advisor.initialize_data(stock_count=50)
    elif args.llm_strategy:
        strategy = advisor.generate_llm_strategy()
        print(f"\n生成的策略：{strategy}")
    elif args.optimize:
        advisor.optimize_strategy()
    elif args.analyze:
        symbols = args.stocks if args.stocks else None
        result = advisor.analyze_and_recommend(symbols)
        print("\n" + "="*60)
        print("分析完成！")
        print("="*60)
    elif args.daily:
        advisor.run_daily_task(enable_llm_features=not args.no_llm)
    else:
        # 默认运行每日任务
        advisor.run_daily_task(enable_llm_features=not args.no_llm)


if __name__ == "__main__":
    main()
