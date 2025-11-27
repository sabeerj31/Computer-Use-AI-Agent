import os
import glob

base_path = r"d:/live-computer-agent/.venv/Lib/site-packages/google/adk"

def search_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                if "from_data" in line:
                    print(f"MATCH in {filepath}:{i+1}: {line.strip()}")
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

print("Searching in runners.py...")
search_in_file(os.path.join(base_path, "runners.py"))

print("\nSearching in all .py files in google/adk...")
for root, dirs, files in os.walk(base_path):
    for file in files:
        if file.endswith(".py"):
            search_in_file(os.path.join(root, file))
