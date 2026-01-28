import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'boat_booking.db')

if not os.path.exists(DB_PATH):
    print('Database file not found:', DB_PATH)
    raise SystemExit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

try:
    # Check if column already exists
    cur.execute("PRAGMA table_info('review');")
    cols = [r[1] for r in cur.fetchall()]
    if 'is_active' in cols:
        print('Column is_active already exists in review table')
    else:
        cur.execute("ALTER TABLE review ADD COLUMN is_active BOOLEAN DEFAULT 1;")
        conn.commit()
        print('Added is_active column to review table')
except Exception as e:
    print('Error altering table:', e)
    raise
finally:
    conn.close()
