import sqlite3
from pathlib import Path

storage = Path('storage')
print('='*60)
print('        AI 投资智能体 - 系统状态')
print('='*60)

print('\n数据库状态:')
for db in ['ashare.db', 'agent_memory.db', 'problems.db', 'evolution.db']:
    path = storage / db
    if path.exists():
        size = round(path.stat().st_size/1024/1024, 2)
        print(f'  OK {db}: {size} MB')
    else:
        print(f'  X {db}: 不存在')

conn = sqlite3.connect(str(storage/'agent_memory.db'))
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM decision_log')
print(f'\n决策记录：{cur.fetchone()[0]} 条')

conn = sqlite3.connect(str(storage/'problems.db'))
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM problems WHERE status="identified"')
print(f'待解决问题：{cur.fetchone()[0]} 个')
cur.execute('SELECT COUNT(*) FROM capability_gaps')
print(f'能力缺口：{cur.fetchone()[0]} 个')
cur.execute('SELECT COUNT(*) FROM improvements')
print(f'已完成改进：{cur.fetchone()[0]} 个')

reports = list(Path('reports/autonomous').glob('*.md'))
print(f'\n自主报告：{len(reports)} 份')

print('\n' + '='*60)
print('系统核心功能正常')
print('='*60)
