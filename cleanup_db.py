import sqlite3
import os

db_path = 'c:/Users/Lavya/Downloads/project/backend/db.sqlite3'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Tables to drop if they exist
tables_to_drop = [
    'project_planning_localtestcasefolder',
    'project_planning_localtestcase',
    'project_planning_testsuite',
    'project_planning_localtestcaseversion'
]

print("Existing tables:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in cursor.fetchall()]
print(tables)

for table in tables_to_drop:
    if table in tables:
        print(f"Dropping table {table}...")
        cursor.execute(f"DROP TABLE {table};")

conn.commit()
conn.close()
print("Cleanup complete.")
