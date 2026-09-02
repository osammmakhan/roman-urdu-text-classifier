import sqlite3
conn = sqlite3.connect('urdu_classifier.db')
cursor = conn.cursor()
cursor.execute('SELECT sql FROM sqlite_master WHERE type="table" AND name="classifications"')
print(cursor.fetchone()[0])
cursor.execute('PRAGMA table_info(classifications)')
for row in cursor.fetchall():
    print(row)
conn.close()