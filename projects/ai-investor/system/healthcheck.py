"""
系统健康检查模块

定期检查系统各组件状态，确保正常运行
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class HealthChecker:
    """
    系统健康检查器
    
    检查项目：
    - 数据库状态
    - 策略模块
    - 回测引擎
    - 报告生成
    - 外部 API（新闻、LLM）
    """
    
    def __init__(self, workspace: str = None):
        self.workspace = Path(workspace) if workspace else Path(__file__).parent.parent
        self.storage_dir = self.workspace / "storage"
        self.reports_dir = self.workspace / "reports"
        self.logs_dir = self.workspace / "logs"
    
    def check_all(self) -> Dict:
        """
        执行全面健康检查
        
        Returns:
            健康状态报告
        """
        print("=" * 60)
        print("系统健康检查")
        print("=" * 60)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }
        
        # 检查各组件
        results['checks']['database'] = self.check_database()
        results['checks']['strategies'] = self.check_strategies()
        results['checks']['reports'] = self.check_reports()
        results['checks']['logs'] = self.check_logs()
        results['checks']['news_api'] = self.check_news_api()
        results['checks']['llm_service'] = self.check_llm_service()
        
        # 计算整体状态
        failed_count = sum(1 for check in results['checks'].values() if check.get('status') == 'error')
        warning_count = sum(1 for check in results['checks'].values() if check.get('status') == 'warning')
        
        if failed_count > 0:
            results['overall_status'] = 'error'
        elif warning_count > 0:
            results['overall_status'] = 'warning'
        
        # 打印摘要
        self._print_summary(results)
        
        return results
    
    def check_database(self) -> Dict:
        """检查数据库状态"""
        print("\n📊 检查数据库...")
        
        db_path = self.storage_dir / "ashare.db"
        
        if not db_path.exists():
            print("  ❌ 数据库文件不存在")
            return {
                'status': 'error',
                'message': '数据库文件不存在',
                'path': str(db_path)
            }
        
        file_size = db_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        
        # 尝试连接数据库
        try:
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # 检查表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # 检查股票数量
            cursor.execute("SELECT COUNT(*) FROM stock_info")
            stock_count = cursor.fetchone()[0]
            
            # 检查数据记录数
            cursor.execute("SELECT COUNT(*) FROM daily_quotes")
            quote_count = cursor.fetchone()[0]
            
            conn.close()
            
            print(f"  ✅ 数据库正常")
            print(f"     大小：{file_size_mb:.2f} MB")
            print(f"     表：{', '.join(tables)}")
            print(f"     股票数：{stock_count}")
            print(f"     行情记录：{quote_count}")
            
            return {
                'status': 'ok',
                'path': str(db_path),
                'size_mb': round(file_size_mb, 2),
                'tables': tables,
                'stock_count': stock_count,
                'quote_count': quote_count
            }
            
        except Exception as e:
            print(f"  ❌ 数据库连接失败：{e}")
            return {
                'status': 'error',
                'message': str(e),
                'path': str(db_path)
            }
    
    def check_strategies(self) -> Dict:
        """检查策略模块"""
        print("\n📈 检查策略模块...")
        
        strategy_dir = self.workspace / "strategy"
        
        if not strategy_dir.exists():
            print("  ❌ 策略目录不存在")
            return {'status': 'error', 'message': '策略目录不存在'}
        
        strategy_files = list(strategy_dir.glob("*.py"))
        print(f"  ✅ 找到 {len(strategy_files)} 个策略文件")
        
        return {
            'status': 'ok',
            'file_count': len(strategy_files),
            'files': [f.name for f in strategy_files]
        }
    
    def check_reports(self) -> Dict:
        """检查报告生成"""
        print("\n📝 检查报告...")
        
        if not self.reports_dir.exists():
            print("  ❌ 报告目录不存在")
            return {'status': 'error', 'message': '报告目录不存在'}
        
        report_files = sorted(self.reports_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not report_files:
            print("  ⚠️ 暂无报告")
            return {'status': 'warning', 'message': '暂无报告'}
        
        latest = report_files[0]
        age_hours = (datetime.now() - datetime.fromtimestamp(latest.stat().st_mtime)).total_seconds() / 3600
        
        print(f"  ✅ 最新报告：{latest.name}")
        print(f"     生成时间：{datetime.fromtimestamp(latest.stat().st_mtime).isoformat()}")
        print(f"     距今：{age_hours:.1f} 小时")
        
        return {
            'status': 'ok',
            'total_count': len(report_files),
            'latest': {
                'name': latest.name,
                'time': datetime.fromtimestamp(latest.stat().st_mtime).isoformat(),
                'age_hours': round(age_hours, 1)
            }
        }
    
    def check_logs(self) -> Dict:
        """检查日志"""
        print("\n📋 检查日志...")
        
        if not self.logs_dir.exists():
            print("  ⚠️ 日志目录不存在")
            return {'status': 'warning', 'message': '日志目录不存在'}
        
        log_files = list(self.logs_dir.glob("*.md"))
        
        if not log_files:
            print("  ⚠️ 暂无日志")
            return {'status': 'warning', 'message': '暂无日志'}
        
        print(f"  ✅ 找到 {len(log_files)} 个日志文件")
        
        return {
            'status': 'ok',
            'file_count': len(log_files)
        }
    
    def check_news_api(self) -> Dict:
        """检查新闻 API"""
        print("\n📰 检查新闻 API...")
        
        try:
            from news.fetcher import FinancialNewsFetcher
            
            fetcher = FinancialNewsFetcher()
            
            # 尝试获取少量新闻
            news = fetcher.fetch_all_news(limit_per_source=3)
            
            if news:
                print(f"  ✅ 新闻 API 正常，获取 {len(news)} 条")
                return {
                    'status': 'ok',
                    'news_count': len(news)
                }
            else:
                print(f"  ⚠️ 新闻 API 无数据")
                return {
                    'status': 'warning',
                    'message': '新闻 API 无数据返回'
                }
                
        except Exception as e:
            print(f"  ❌ 新闻 API 错误：{e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def check_llm_service(self) -> Dict:
        """检查 LLM 服务"""
        print("\n🧠 检查 LLM 服务...")
        
        try:
            from llm_service.config import LLMConfig
            
            if LLMConfig.validate():
                print(f"  ✅ LLM 服务已配置 ({LLMConfig.DASHSCOPE_MODEL})")
                return {
                    'status': 'ok',
                    'provider': LLMConfig.PROVIDER,
                    'model': LLMConfig.DASHSCOPE_MODEL
                }
            else:
                print(f"  ⚠️ LLM 服务未配置 API Key")
                return {
                    'status': 'warning',
                    'message': '未配置 DASHSCOPE_API_KEY'
                }
                
        except Exception as e:
            print(f"  ❌ LLM 服务错误：{e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _print_summary(self, results: Dict):
        """打印摘要"""
        print("\n" + "=" * 60)
        print("健康检查摘要")
        print("=" * 60)
        
        status_icon = {
            'ok': '✅',
            'warning': '⚠️',
            'error': '❌'
        }
        
        overall = results.get('overall_status', 'unknown')
        print(f"\n整体状态：{status_icon.get(overall, '❓')} {overall.upper()}")
        print(f"检查时间：{results.get('timestamp', 'N/A')}")
        
        print("\n各组件状态:")
        for name, check in results.get('checks', {}).items():
            status = check.get('status', 'unknown')
            icon = status_icon.get(status, '❓')
            print(f"  {icon} {name}: {status}")
    
    def save_report(self, results: Dict) -> str:
        """保存健康检查报告"""
        report_path = self.logs_dir / f"health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        return str(report_path)


if __name__ == "__main__":
    checker = HealthChecker()
    results = checker.check_all()
    
    # 保存报告
    report_path = checker.save_report(results)
    print(f"\n📁 报告已保存：{report_path}")
