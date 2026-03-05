"""
测试 Flask 路径问题
"""

from pathlib import Path
import sqlite3

# 模拟 Flask 中的路径
BASE_PATH = Path(__file__).parent
STORAGE_PATH = BASE_PATH / "storage"

print(f"BASE_PATH: {BASE_PATH}")
print(f"BASE_PATH absolute: {BASE_PATH.absolute()}")
print(f"STORAGE_PATH: {STORAGE_PATH}")
print(f"STORAGE_PATH absolute: {STORAGE_PATH.absolute()}")

# 检查数据库
db_path = STORAGE_PATH / "agent_memory.db"
print(f"\nagent_memory.db: {db_path}")
print(f"Exists: {db_path.exists()}")

if db_path.exists():
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM decision_log")
    count = cursor.fetchone()[0]
    print(f"Decision count: {count}")
    conn.close()
else:
    # 尝试绝对路径
    abs_path = Path(r"D:\openclaw\workspace\projects\ai-investor\storage\agent_memory.db")
    print(f"\nTrying absolute path: {abs_path}")
    print(f"Exists: {abs_path.exists()}")
    if abs_path.exists():
        conn = sqlite3.connect(str(abs_path))
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM decision_log")
        count = cursor.fetchone()[0]
        print(f"Decision count: {count}")
        conn.close()
