"""
最简单的 Flask 测试 - 直接返回数据库数据
"""

from flask import Flask, jsonify
import sqlite3
import json
from pathlib import Path
from datetime import datetime

app = Flask(__name__)

# 绝对路径
BASE_PATH = Path(r"D:\openclaw\workspace\projects\ai-investor")
STORAGE_PATH = BASE_PATH / "storage"

print(f"BASE_PATH: {BASE_PATH}")
print(f"agent_memory.db exists: {(STORAGE_PATH / 'agent_memory.db').exists()}")
print(f"problems.db exists: {(STORAGE_PATH / 'problems.db').exists()}")

@app.route('/api/status')
def get_status():
    print("[API] /api/status called!")
    
    status = {
        "win_rate": 0.5,
        "confidence": 0.6,
        "db_size": 0,
        "run_count": 0,
        "problems": [],
        "gaps": [],
        "reports": [],
        "improvements": []
    }
    
    # 获取问题
    db_path = STORAGE_PATH / "problems.db"
    print(f"[API] problems.db path: {db_path}, exists: {db_path.exists()}")
    
    if db_path.exists():
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT problem, category, severity FROM problems ORDER BY created_at DESC LIMIT 10")
        problems = cursor.fetchall()
        conn.close()
        status["problems"] = [{"problem": p[0], "category": p[1], "severity": p[2]} for p in problems]
        print(f"[API] Found {len(problems)} problems")
    
    # 获取能力缺口
    if db_path.exists():
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT capability, why_needed, priority FROM capability_gaps ORDER BY created_at DESC LIMIT 10")
        gaps = cursor.fetchall()
        conn.close()
        status["gaps"] = [{"capability": g[0], "why_needed": g[1], "priority": g[2]} for g in gaps]
        print(f"[API] Found {len(gaps)} gaps")
    
    # 获取数据库大小
    db_path = STORAGE_PATH / "ashare.db"
    if db_path.exists():
        status["db_size"] = round(db_path.stat().st_size / (1024*1024), 1)
        print(f"[API] DB size: {status['db_size']} MB")
    
    return jsonify(status)

@app.route('/')
def index():
    return jsonify({"message": "Flask test server running!", "path": str(BASE_PATH)})

if __name__ == "__main__":
    print("\n=== Test Flask Server ===")
    print("URL: http://localhost:5001")
    print("API: http://localhost:5001/api/status\n")
    app.run(host='0.0.0.0', port=5001, debug=False)
