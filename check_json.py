import sqlite3
import json
import os

db_path = 'c:/Users/Lavya/Downloads/project/backend/db.sqlite3'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("Global Test Cases (SAVED) JSON:")
cursor.execute("SELECT * FROM project_planning_testcase WHERE project_id=1 AND status='SAVED' LIMIT 2;")
rows = [dict(r) for r in cursor.fetchall()]
print(json.dumps(rows, indent=2))

conn.close()
