#!/usr/bin/env python3
"""
Post-installation script to install bundled packages and requirements.
This runs after the main package is installed.
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Install bundled custom packages and requirements.txt."""
    print("\n" + "=" * 70)
    print("POST-INSTALL: Installing bundled custom packages...")
    print("=" * 70)
    
    # Find the installed package location
    try:
        import client
        package_dir = Path(client.__file__).parent
        libs_dir = package_dir / 'libs'
        
        if not libs_dir.exists():
            print(f"[WARN] libs directory not found at: {libs_dir}")
            print("Skipping bundled package installation.")
            return 0
        
        bundled_packages = [
            'nslogger-1.0.0.tar.gz',
            'trading_api-1.0.0.tar.gz'
        ]
        
        for tar_file in bundled_packages:
            tar_path = libs_dir / tar_file
            
            if tar_path.exists():
                print(f"\n[*] Installing: {tar_file}")
                try:
                    subprocess.check_call(
                        [sys.executable, '-m', 'pip', 'install', '--no-deps', str(tar_path)],
                        stdout=sys.stdout,
                        stderr=sys.stderr
                    )
                    print(f"   [OK] Successfully installed {tar_file}")
                except subprocess.CalledProcessError as e:
                    print(f"   [FAIL] Failed to install {tar_file}")
                    print(f"   Error: {e}")
                    return 1
            else:
                print(f"   [WARN] {tar_file} not found at {tar_path}")
        
        print("\n" + "=" * 70)
        print("Bundled package installation complete!")
        print("=" * 70 + "\n")
        
        # Look for requirements.txt in multiple possible locations
        import site
        requirements_locations = []
        
        # Check site-packages directories
        for site_dir in site.getsitepackages():
            requirements_locations.extend([
                Path(site_dir) / 'requirements.txt',
                Path(site_dir) / 'trading_api_monitor-1.0.0.dist-info' / 'requirements.txt',
            ])
        
        # Also check near the package
        requirements_locations.extend([
            package_dir.parent / 'requirements.txt',
            package_dir / 'requirements.txt',
            Path.cwd() / 'requirements.txt',
        ])
        
        requirements_file = None
        for loc in requirements_locations:
            if loc.exists():
                requirements_file = loc
                print(f"[INFO] Found requirements.txt at: {requirements_file}")
                break
        
        if requirements_file:
            print("\n" + "=" * 70)
            print("POST-INSTALL: Installing dependencies from requirements.txt")
            print("=" * 70 + "\n")
            
            try:
                subprocess.check_call(
                    [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)],
                    stdout=sys.stdout,
                    stderr=sys.stderr
                )
                print("\n[OK] Requirements.txt installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"\n[WARN] Failed to install requirements.txt: {e}")
                print("This may be okay if requirements are already satisfied")
        else:
            print("[INFO] No requirements.txt found - skipping")
            print("[INFO] Searched locations:")
            for loc in requirements_locations[:5]:  # Show first 5
                print(f"  - {loc}")
        
        return 0
        
    except ImportError:
        print("[ERROR] Could not import client package")
        return 1
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
