import sqlite3
import os

db_path = 'c:/Users/Lavya/Downloads/project/backend/db.sqlite3'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Global Test Cases (SAVED):")
cursor.execute("SELECT id, name, status, folder_id FROM project_planning_testcase WHERE project_id=1 AND status='SAVED' LIMIT 10;")
rows = cursor.fetchall()
for row in rows:
    print(row)

print("\nFolders (ACTIVE):")
cursor.execute("SELECT id, name, status FROM project_planning_testcasefolder WHERE project_id=1 AND status='ACTIVE';")
rows = cursor.fetchall()
for row in rows:
    print(row)

conn.close()
