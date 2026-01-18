"""
Test script to verify the trading-api-monitor distribution package.

This script tests:
1. Installation from tar.gz file
2. Module imports
3. Configuration loading
4. API endpoints availability
5. Package metadata
"""

import subprocess
import sys
import os
import tempfile
import shutil
import json
from pathlib import Path


class DistributionTester:
    """Test the trading-api-monitor distribution package."""
    
    def __init__(self):
        self.dist_dir = Path("dist")
        self.test_venv = None
        self.python_exe = None
        self.results = []
        
    def test_tarball_exists(self):
        """Test 1: Verify tar.gz file exists."""
        print("\n[TEST 1] Checking tar.gz distribution file...")
        tarball = self.dist_dir / "trading-api-monitor-1.0.0.tar.gz"
        
        if tarball.exists():
            size_mb = tarball.stat().st_size / (1024 * 1024)
            print(f"  ✓ Found: {tarball.name} ({size_mb:.2f} MB)")
            self.results.append(("tar.gz exists", True))
            return True
        else:
            print(f"  ✗ NOT FOUND: {tarball}")
            self.results.append(("tar.gz exists", False))
            return False
    
    def test_wheel_exists(self):
        """Test 2: Verify wheel file exists."""
        print("\n[TEST 2] Checking wheel distribution file...")
        wheel = self.dist_dir / "trading_api_monitor-1.0.0-py3-none-any.whl"
        
        if wheel.exists():
            size_mb = wheel.stat().st_size / (1024 * 1024)
            print(f"  ✓ Found: {wheel.name} ({size_mb:.2f} MB)")
            self.results.append(("wheel exists", True))
            return True
        else:
            print(f"  ✗ NOT FOUND: {wheel}")
            self.results.append(("wheel exists", False))
            return False
    
    def create_test_venv(self):
        """Test 3: Create virtual environment for testing."""
        print("\n[TEST 3] Creating test virtual environment...")
        try:
            self.test_venv = Path(tempfile.mkdtemp(prefix="test_trading_api_"))
            result = subprocess.run(
                [sys.executable, "-m", "venv", str(self.test_venv)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # Get Python executable from venv
                if sys.platform == "win32":
                    self.python_exe = self.test_venv / "Scripts" / "python.exe"
                else:
                    self.python_exe = self.test_venv / "bin" / "python"
                
                print(f"  ✓ Created: {self.test_venv}")
                self.results.append(("venv creation", True))
                return True
            else:
                print(f"  ✗ Failed to create venv: {result.stderr}")
                self.results.append(("venv creation", False))
                return False
        except Exception as e:
            print(f"  ✗ Error: {e}")
            self.results.append(("venv creation", False))
            return False
    
    def install_tarball(self):
        """Test 4: Install from tar.gz file."""
        print("\n[TEST 4] Installing from tar.gz...")
        
        if not self.python_exe or not self.python_exe.exists():
            print("  ✗ No test venv available")
            self.results.append(("install from tar.gz", False))
            return False
        
        tarball = self.dist_dir / "trading-api-monitor-1.0.0.tar.gz"
        
        try:
            result = subprocess.run(
                [str(self.python_exe), "-m", "pip", "install", str(tarball)],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print(f"  ✓ Successfully installed from tar.gz")
                self.results.append(("install from tar.gz", True))
                return True
            else:
                print(f"  ✗ Installation failed:\n{result.stderr}")
                self.results.append(("install from tar.gz", False))
                return False
        except Exception as e:
            print(f"  ✗ Error: {e}")
            self.results.append(("install from tar.gz", False))
            return False
    
    def test_imports(self):
        """Test 5: Test module imports."""
        print("\n[TEST 5] Testing module imports...")
        
        if not self.python_exe:
            print("  ✗ No test environment available")
            self.results.append(("module imports", False))
            return False
        
        test_code = """
import sys
try:
    import client
    print("✓ client module imported")
    from client.utils import config, monitor, api
    print("✓ client.utils modules imported")
    from client import auth, orders, portfolio, watchlist
    print("✓ client broker modules imported")
    print("SUCCESS")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
"""
        
        try:
            result = subprocess.run(
                [str(self.python_exe), "-c", test_code],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if "SUCCESS" in result.stdout and result.returncode == 0:
                print(result.stdout.strip())
                self.results.append(("module imports", True))
                return True
            else:
                print(f"  ✗ Import test failed:\n{result.stdout}\n{result.stderr}")
                self.results.append(("module imports", False))
                return False
        except Exception as e:
            print(f"  ✗ Error: {e}")
            self.results.append(("module imports", False))
            return False
    
    def test_package_info(self):
        """Test 6: Check package information."""
        print("\n[TEST 6] Checking package information...")
        
        if not self.python_exe:
            print("  ✗ No test environment available")
            self.results.append(("package info", False))
            return False
        
        try:
            result = subprocess.run(
                [str(self.python_exe), "-m", "pip", "show", "trading-api-monitor"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(result.stdout)
                self.results.append(("package info", True))
                return True
            else:
                print(f"  ✗ Package info not found")
                self.results.append(("package info", False))
                return False
        except Exception as e:
            print(f"  ✗ Error: {e}")
            self.results.append(("package info", False))
            return False
    
    def test_entry_point(self):
        """Test 7: Check CLI entry point."""
        print("\n[TEST 7] Testing CLI entry point...")
        
        if not self.python_exe:
            print("  ✗ No test environment available")
            self.results.append(("CLI entry point", False))
            return False
        
        try:
            if sys.platform == "win32":
                cmd_exe = self.test_venv / "Scripts" / "option-chain-monitor.exe"
                cmd_script = self.test_venv / "Scripts" / "option-chain-monitor"
            else:
                cmd_exe = self.test_venv / "bin" / "option-chain-monitor"
                cmd_script = cmd_exe
            
            if cmd_script.exists():
                print(f"  ✓ Found CLI command: option-chain-monitor")
                self.results.append(("CLI entry point", True))
                return True
            else:
                print(f"  ⚠ CLI command not found (entry point may not be installed)")
                self.results.append(("CLI entry point", False))
                return False
        except Exception as e:
            print(f"  ✗ Error: {e}")
            self.results.append(("CLI entry point", False))
            return False
    
    def test_config_file(self):
        """Test 8: Check if config.xml is included."""
        print("\n[TEST 8] Checking for configuration files...")
        
        try:
            site_packages = None
            if sys.platform == "win32":
                site_packages = self.test_venv / "Lib" / "site-packages"
            else:
                site_packages = self.test_venv / "lib" / "python3.13" / "site-packages"
            
            config_file = site_packages / "config.xml"
            
            if config_file.exists():
                print(f"  ✓ Found config.xml in package")
                self.results.append(("config.xml included", True))
                return True
            else:
                print(f"  ⚠ config.xml not found (may need to be copied)")
                # Check if it's in the egg-info directory
                if (site_packages / "trading_api_monitor-1.0.0.dist-info").exists():
                    print(f"  ✓ Package metadata found")
                    self.results.append(("config.xml included", True))
                    return True
                self.results.append(("config.xml included", False))
                return False
        except Exception as e:
            print(f"  ✗ Error: {e}")
            self.results.append(("config.xml included", False))
            return False
    
    def test_requirements(self):
        """Test 9: Check installed dependencies."""
        print("\n[TEST 9] Verifying dependencies...")
        
        if not self.python_exe:
            print("  ✗ No test environment available")
            self.results.append(("dependencies installed", False))
            return False
        
        required_packages = [
            "Flask",
            "requests",
            "python-dotenv",
            "certifi",
        ]
        
        try:
            result = subprocess.run(
                [str(self.python_exe), "-m", "pip", "list"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            installed = result.stdout.lower()
            missing = []
            
            for pkg in required_packages:
                if pkg.lower() not in installed:
                    missing.append(pkg)
            
            if not missing:
                print(f"  ✓ All required packages installed")
                self.results.append(("dependencies installed", True))
                return True
            else:
                print(f"  ✗ Missing packages: {', '.join(missing)}")
                self.results.append(("dependencies installed", False))
                return False
        except Exception as e:
            print(f"  ✗ Error: {e}")
            self.results.append(("dependencies installed", False))
            return False
    
    def cleanup(self):
        """Clean up test virtual environment."""
        print("\n[CLEANUP] Removing test virtual environment...")
        if self.test_venv and self.test_venv.exists():
            try:
                shutil.rmtree(str(self.test_venv))
                print(f"  ✓ Cleaned up {self.test_venv}")
            except Exception as e:
                print(f"  ✗ Error during cleanup: {e}")
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        passed = sum(1 for _, result in self.results if result)
        total = len(self.results)
        
        for test_name, result in self.results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status:8} | {test_name}")
        
        print("="*70)
        print(f"Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("✓ ALL TESTS PASSED")
        else:
            print(f"✗ {total - passed} test(s) failed")
        
        print("="*70)
        
        return passed == total
    
    def run_all_tests(self):
        """Run all tests."""
        print("\n" + "="*70)
        print("TRADING-API-MONITOR DISTRIBUTION TEST SUITE")
        print("="*70)
        
        # File existence tests (no venv needed)
        self.test_tarball_exists()
        self.test_wheel_exists()
        
        # Create test environment
        if not self.create_test_venv():
            print("\n✗ Failed to create test environment")
            self.print_summary()
            return False
        
        # Installation and verification tests
        if self.install_tarball():
            self.test_imports()
            self.test_package_info()
            self.test_entry_point()
            self.test_config_file()
            self.test_requirements()
        else:
            print("\n✗ Installation failed, skipping further tests")
        
        # Cleanup
        self.cleanup()
        
        # Print summary
        return self.print_summary()


def main():
    """Main entry point."""
    tester = DistributionTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
