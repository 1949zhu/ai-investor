import sqlite3
conn = sqlite3.connect('storage/ashare.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", [r[0] for r in cursor.fetchall()])
cursor.execute("PRAGMA table_info(daily_quotes)")
print("Columns:", [(r[1], r[2]) for r in cursor.fetchall()])
conn.close()
