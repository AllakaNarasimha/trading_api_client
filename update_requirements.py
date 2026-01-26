import requests
import re
import time
import subprocess
import sys
from pathlib import Path

# Packages to ignore when checking for latest versions
IGNORED_PACKAGES = ['requests', 'aiohttp', 'sphinx', 'black', 'fyers-apiv3']  # Add package names here to skip version updates

# Upgrade pip first
print("Checking for pip upgrade...")
try:
    result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                          capture_output=True, text=True, timeout=60)
    if result.returncode == 0:
        print("✓ Pip upgraded successfully")
    else:
        print(f"⚠ Pip upgrade failed: {result.stderr}")
except Exception as e:
    print(f"⚠ Error upgrading pip: {e}")

# Read packages from requirements.txt
requirements_file = Path(__file__).parent / "requirements.txt"

packages = []
package_lines = []
if requirements_file.exists():
    with open(requirements_file, 'r') as f:
        for line in f:
            original_line = line.rstrip('\n')
            stripped = line.strip()
            # Store comments and empty lines as-is
            if not stripped or stripped.startswith('#'):
                package_lines.append((None, original_line))
            else:
                # Extract package name (before >=, ==, <=, etc.)
                match = re.match(r'^([a-zA-Z0-9_-]+)', stripped)
                if match:
                    pkg_name = match.group(1)
                    packages.append(pkg_name)
                    package_lines.append((pkg_name, original_line))
else:
    print(f"Error: requirements.txt not found at {requirements_file}")
    exit(1)

# Filter out ignored packages from version checking
packages_to_check = [pkg for pkg in packages if pkg not in IGNORED_PACKAGES]
if IGNORED_PACKAGES:
    print(f"Ignoring version checks for: {', '.join(IGNORED_PACKAGES)}")

print("\nFetching latest versions from PyPI...")
print("-" * 50)

# Fetch latest versions with retry logic
latest_versions = {}
for pkg in packages_to_check:
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            response = requests.get(
                f"https://pypi.org/pypi/{pkg}/json", 
                timeout=30  # Increased timeout to 30 seconds
            )
            response.raise_for_status()
            version = response.json()["info"]["version"]
            latest_versions[pkg] = version
            print(f"{pkg}: {version}")
            break  # Success, exit retry loop
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                print(f"{pkg}: Timeout (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"{pkg}: Timeout after {max_retries} attempts - keeping existing version")
                latest_versions[pkg] = None
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print(f"{pkg}: Error (attempt {attempt + 1}/{max_retries}): {type(e).__name__}, retrying...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                print(f"{pkg}: Error after {max_retries} attempts - {type(e).__name__} - keeping existing version")
                latest_versions[pkg] = None
        except Exception as e:
            print(f"{pkg}: Unexpected error - {type(e).__name__}: {e} - keeping existing version")
            latest_versions[pkg] = None
            break

# Set ignored packages to None (keep original versions)
for pkg in IGNORED_PACKAGES:
    if pkg in packages:
        latest_versions[pkg] = None
        print(f"{pkg}: Skipped (ignored)")

print("-" * 50)

# Update requirements.txt with latest versions
updated_lines = []
for pkg_name, original_line in package_lines:
    if pkg_name is None:
        # Keep comments and empty lines
        updated_lines.append(original_line)
    elif pkg_name in latest_versions and latest_versions[pkg_name]:
        # Update to latest version
        updated_lines.append(f"{pkg_name}>={latest_versions[pkg_name]}")
    else:
        # Keep original if version fetch failed
        updated_lines.append(original_line)

# Write updated content back to requirements.txt
with open(requirements_file, 'w') as f:
    f.write('\n'.join(updated_lines) + '\n')

print(f"\n✓ Updated {requirements_file} with latest versions!")
