# -*- coding: utf-8 -*-
"""生成自主运行报告"""

import sqlite3
from pathlib import Path
from datetime import datetime

db = Path('storage/problems.db')
conn = sqlite3.connect(db)
cursor = conn.cursor()

report = []
report.append("# 智能体自主运行报告")
report.append(f"\n**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

# 问题追踪
report.append("## 问题追踪 (最近 5 个)")
report.append("")
cursor.execute('SELECT problem, status, created_at FROM problems ORDER BY created_at DESC LIMIT 5')
for row in cursor.fetchall():
    report.append(f"- [{row[2][:16]}] {row[0][:50]} - **{row[1]}**")

# 能力缺口
report.append("\n## 能力缺口")
report.append("")
cursor.execute('SELECT capability, implemented, created_at FROM capability_gaps ORDER BY created_at DESC')
implemented = 0
pending = 0
for row in cursor.fetchall():
    if row[1]:
        implemented += 1
    else:
        pending += 1

report.append(f"- ✅ 已完成：{implemented} 个")
report.append(f"- ⏳ 待解决：{pending} 个")

# 改进记录
report.append("\n## 改进记录 (最近 3 次)")
report.append("")
cursor.execute('SELECT improvement, created_at FROM improvements ORDER BY created_at DESC LIMIT 3')
for row in cursor.fetchall():
    report.append(f"- [{row[1][:16]}] {row[0][:50]}")

# 统计
report.append("\n## 统计")
report.append("")
cursor.execute('SELECT COUNT(*) FROM problems')
report.append(f"- 总问题数：{cursor.fetchone()[0]}")

cursor.execute('SELECT COUNT(*) FROM capability_gaps')
report.append(f"- 总能力缺口：{cursor.fetchone()[0]}")

cursor.execute('SELECT COUNT(*) FROM improvements')
report.append(f"- 总改进数：{cursor.fetchone()[0]}")

conn.close()

# 保存
output = Path('solutions') / f"autonomous_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
with open(output, 'w', encoding='utf-8') as f:
    f.write('\n'.join(report))

print('\n'.join(report))
print(f"\n报告已保存：{output}")
