import sqlite3
import os

ROOT = os.path.dirname(os.path.dirname(__file__))
DB = os.path.join(ROOT, 'boat_booking.db')

if not os.path.exists(DB):
    print('Database not found at', DB)
    raise SystemExit(1)

conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("PRAGMA table_info('review');")
rows = cur.fetchall()
print('Columns in review table:')
for r in rows:
    print(r)
conn.close()
