"""
快速测试 - 直接读取数据库并显示
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

BASE_PATH = Path(__file__).parent
STORAGE_PATH = BASE_PATH / "storage"

print("="*60)
print("        数据库数据预览")
print("="*60)

# 1. agent_memory.db
print("\n📊 agent_memory.db")
db_path = STORAGE_PATH / "agent_memory.db"
if db_path.exists():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM decision_log")
    count = cursor.fetchone()[0]
    print(f"  决策记录：{count} 条")
    
    cursor.execute("SELECT date, decision, outcome FROM decision_log ORDER BY date DESC LIMIT 3")
    for row in cursor.fetchall():
        print(f"    - {row[0]}: {row[1][:30]}... → {row[2]}")
    
    conn.close()
else:
    print("  ❌ 数据库不存在")

# 2. problems.db
print("\n🔍 problems.db")
db_path = STORAGE_PATH / "problems.db"
if db_path.exists():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM problems")
    problems_count = cursor.fetchone()[0]
    print(f"  问题：{problems_count} 个")
    
    cursor.execute("SELECT problem, severity FROM problems LIMIT 3")
    for row in cursor.fetchall():
        print(f"    - {row[0]} ({row[1]})")
    
    cursor.execute("SELECT COUNT(*) FROM capability_gaps")
    gaps_count = cursor.fetchone()[0]
    print(f"  能力缺口：{gaps_count} 个")
    
    cursor.execute("SELECT COUNT(*) FROM improvements")
    improvements_count = cursor.fetchone()[0]
    print(f"  改进记录：{improvements_count} 个")
    
    conn.close()
else:
    print("  ❌ 数据库不存在")

# 3. scheduler.json
print("\n⚙️  scheduler.json")
config_path = BASE_PATH / "config" / "scheduler.json"
if config_path.exists():
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        print(f"  运行次数：{config.get('run_count', 0)}")
else:
    print("  ❌ 文件不存在")

# 4. ashare.db
print("\n💾 ashare.db")
db_path = STORAGE_PATH / "ashare.db"
if db_path.exists():
    size_mb = round(db_path.stat().st_size / (1024*1024), 1)
    print(f"  数据库大小：{size_mb} MB")
else:
    print("  ❌ 数据库不存在")

print("\n" + "="*60)
print("✅ 数据检查完成！")
print("\n如果上面显示有数据，但 Web 界面没有，说明是 Flask 代码问题。")
print("请刷新浏览器：http://localhost:5000")
print("="*60)
