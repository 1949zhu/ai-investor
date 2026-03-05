"""
自主调度器 - 让系统自己运行，不用人管

功能：
1. 定时自主检查（每 4 小时）
2. 发现异常主动通知
3. 定期自主改进
4. 记录运行日志
"""

import os
import sys
import time
import json
import schedule
from datetime import datetime
from pathlib import Path

# 设置 API Key
os.environ['DASHSCOPE_API_KEY'] = 'sk-fb6aa9235b6b4627aa2ac5f7295db04c'

sys.path.insert(0, '.')

from autonomous.evolution_engine import SelfEvolutionEngine
from data.market_data import get_latest_market_data
from memory.agent_memory import AgentMemory


class AutonomousScheduler:
    """自主调度器"""
    
    def __init__(self):
        self.engine = SelfEvolutionEngine()
        self.memory = AgentMemory()
        self.log_dir = Path(__file__).parent.parent / "logs" / "autonomous"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = Path(__file__).parent.parent / "config" / "scheduler.json"
        self._init_config()
    
    def _init_config(self):
        """初始化配置"""
        if not self.config_path.exists():
            config = {
                "enabled": True,
                "check_interval_hours": 4,
                "full_analysis_interval_hours": 24,
                "alert_enabled": True,
                "last_check": None,
                "last_full_analysis": None,
                "run_count": 0
            }
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
    
    def _load_config(self) -> Dict:
        """加载配置"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_config(self, config: Dict):
        """保存配置"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def _log(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        # 写入日志文件
        log_file = self.log_dir / f"autonomous_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def periodic_check(self):
        """定期自主检查"""
        self._log("="*50)
        self._log("启动自主检查周期...")
        
        try:
            # 运行自主进化周期
            result = self.engine.autonomous_run()
            
            # 更新配置
            config = self._load_config()
            config['last_check'] = datetime.now().isoformat()
            config['run_count'] = config.get('run_count', 0) + 1
            self._save_config(config)
            
            # 记录结果
            confidence = result['assessment']['confidence']
            self._log(f"自主检查完成，系统置信度：{confidence*100:.1f}%")
            
            # 如果有异常，记录警报
            if result['assessment'].get('anomalies'):
                self._log(f"发现 {len(result['assessment']['anomalies'])} 个异常", "WARNING")
            
        except Exception as e:
            self._log(f"自主检查失败：{e}", "ERROR")
    
    def full_analysis(self):
        """完整分析（每天一次）"""
        self._log("="*50)
        self._log("启动每日完整分析...")
        
        try:
            # 1. 获取市场数据
            self._log("获取市场数据...")
            market_data = get_latest_market_data()
            
            # 2. 运行 AI 决策
            self._log("运行 AI 决策...")
            # (这里可以调用 generate_ai_v4.py 的逻辑)
            
            # 3. 运行自主进化
            self._log("运行自主进化...")
            result = self.engine.autonomous_run()
            
            # 4. 更新配置
            config = self._load_config()
            config['last_full_analysis'] = datetime.now().isoformat()
            self._save_config(config)
            
            self._log("每日完整分析完成")
            
        except Exception as e:
            self._log(f"每日完整分析失败：{e}", "ERROR")
    
    def get_status(self) -> Dict:
        """获取系统状态"""
        config = self._load_config()
        
        return {
            "enabled": config.get('enabled', True),
            "last_check": config.get('last_check'),
            "last_full_analysis": config.get('last_full_analysis'),
            "run_count": config.get('run_count', 0),
            "check_interval_hours": config.get('check_interval_hours', 4),
            "next_check": self._calculate_next_check(config)
        }
    
    def _calculate_next_check(self, config: Dict) -> str:
        """计算下次检查时间"""
        last_check = config.get('last_check')
        if not last_check:
            return "即将运行"
        
        try:
            last = datetime.fromisoformat(last_check)
            interval = config.get('check_interval_hours', 4)
            next_check = last + timedelta(hours=interval)
            return next_check.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return "未知"
    
    def run_continuous(self, interval_minutes: int = 240):
        """持续运行模式"""
        self._log("启动持续运行模式...")
        self._log(f"检查间隔：{interval_minutes}分钟")
        
        # 设置定时任务
        schedule.every(interval_minutes).minutes.do(self.periodic_check)
        schedule.every().day.at("20:00").do(self.full_analysis)
        
        self._log("调度器已启动，按 Ctrl+C 停止")
        
        # 立即运行一次
        self.periodic_check()
        
        # 持续运行
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    
    def run_once(self):
        """运行一次"""
        self.periodic_check()


# 导入 timedelta
from datetime import timedelta


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='自主调度器')
    parser.add_argument('--mode', choices=['once', 'continuous'], default='once',
                       help='运行模式：once=运行一次，continuous=持续运行')
    parser.add_argument('--interval', type=int, default=240,
                       help='检查间隔（分钟），默认 240 分钟（4 小时）')
    
    args = parser.parse_args()
    
    scheduler = AutonomousScheduler()
    
    if args.mode == 'once':
        scheduler.run_once()
    else:
        scheduler.run_continuous(interval_minutes=args.interval)
