"""Capture loaddata error properly."""
import subprocess
import sys

result = subprocess.run(
    [r".\venv\Scripts\python.exe", "manage.py", "loaddata", "data_dump.json", "--traceback"],
    capture_output=True,
    text=True,
    cwd=r"c:\Users\Lavya\Downloads\project\backend",
)
print("=== STDOUT ===")
print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
print("=== STDERR ===")
print(result.stderr[-3000:] if len(result.stderr) > 3000 else result.stderr)
print(f"=== EXIT CODE: {result.returncode} ===")
