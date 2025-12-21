#!/usr/bin/env python3
"""
Verify that all required packages are installed.
"""

import sys


def verify_packages():
    """Check if all required packages can be imported."""
    print("\n" + "=" * 70)
    print("VERIFYING INSTALLATION")
    print("=" * 70 + "\n")
    
    packages = {
        'Flask': 'Flask',
        'requests': 'requests',
        'trading_api': 'trading_api',
        'nslogger': 'nslogger',
        'client': 'client'
    }
    
    failed = []
    
    for name, module in packages.items():
        try:
            __import__(module)
            print(f"✓ {name:20s} - OK")
        except ImportError as e:
            print(f"✗ {name:20s} - MISSING ({e})")
            failed.append(name)
    
    print("\n" + "=" * 70)
    
    if failed:
        print(f"FAILED: {len(failed)} package(s) missing: {', '.join(failed)}")
        print("=" * 70 + "\n")
        return 1
    else:
        print("SUCCESS: All packages installed correctly!")
        print("=" * 70 + "\n")
        return 0


if __name__ == "__main__":
    sys.exit(verify_packages())
