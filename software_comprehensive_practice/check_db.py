import sqlite3
conn = sqlite3.connect('db.sqlite3')
cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("Tables:", tables)
for t in tables:
    try:
        cur2 = conn.execute(f'SELECT COUNT(*) FROM "{t}"')
        count = cur2.fetchone()[0]
        print(f"  {t}: {count} rows")
    except:
        print(f"  {t}: error reading")
conn.close()
