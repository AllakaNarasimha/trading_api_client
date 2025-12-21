import subprocess
import os
import sys

# Your specific paths - UPDATE THESE
bat_file = r"D:\Test\run_monitor.bat"
task_name = "OC Collector"
start_dir = r"D:\Test"

# First, verify the batch file exists
if not os.path.exists(bat_file):
    print(f"ERROR: Batch file not found at: {bat_file}")
    sys.exit(1)

print(f"Creating task with:")
print(f"  Batch file: {bat_file}")
print(f"  Task name: {task_name}")
print(f"  Start dir: {start_dir}")
print()

# Using cmd.exe with full path to avoid "file not found" errors
cmd = [
    'schtasks', '/create', '/tn', task_name,
    '/tr', f'cmd.exe /c "{bat_file}"',
    '/sc', 'onstart',
    '/f',
    '/rl', 'HIGHEST',
    '/ru', 'SYSTEM'
]

print("Running command:")
print(" ".join(cmd))
print()

result = subprocess.run(cmd, capture_output=True, text=True)
print("STDOUT:", result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
print("Return code:", result.returncode)

if result.returncode == 0:
    print(f"\n✓ Task '{task_name}' created successfully!")
    print(f"\nVerify: schtasks /query /tn \"{task_name}\" /v /fo list")
    print(f"Test run: schtasks /run /tn \"{task_name}\"")
    print(f"Delete: schtasks /delete /tn \"{task_name}\" /f")
else:
    print("\n✗ Task creation failed.")
    print("Make sure:")
    print("  1. Running as Administrator")
    print("  2. Batch file exists at the specified path")
    print("  3. No task with the same name already exists")
