#!/usr/bin/env python3
"""
Setup script for trading-api-monitor package.

Usage:
    python setup.py install
    python -m pip install .
    python -m pip install -e .  # Development mode
"""

import os
import sys
import subprocess
from pathlib import Path
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.install_scripts import install_scripts


def install_bundled_packages():
    """
    Install bundled .tar.gz packages after main package installation.
    This runs after the main package is installed.
    """
    # Get the directory where this setup.py is located
    setup_dir = Path(__file__).parent.resolve()
    libs_dir = setup_dir / 'client' / 'libs'
    
    if not libs_dir.exists():
        print(f"Warning: libs directory not found at {libs_dir}")
        return
    
    # List of bundled packages to install
    bundled_packages = [
        'nslogger-1.0.0.tar.gz',
        'trading_api-1.0.0.tar.gz'
    ]
    
    print("\n" + "=" * 70)
    print("Installing bundled packages...")
    print("=" * 70)
    
    for tar_file in bundled_packages:
        tar_path = libs_dir / tar_file
        
        if tar_path.exists():
            print(f"\n[*] Installing: {tar_file}")
            try:
                # Install the package
                # --no-deps: Don't install dependencies (they should be in main dependencies)
                subprocess.check_call(
                    [
                        sys.executable, 
                        '-m', 
                        'pip', 
                        'install', 
                        '--no-deps',
                        str(tar_path)
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT
                )
                print(f"   [OK] Successfully installed {tar_file}")
            except subprocess.CalledProcessError as e:
                print(f"   [FAIL] Failed to install {tar_file}")
                print(f"   Error: {e}")
                # Continue on error instead of failing
                # Uncomment next line to make installation fail on error:
                # sys.exit(1)
        else:
            print(f"   [WARN] {tar_file} not found at {tar_path}")
    
    print("\n" + "=" * 70)
    print("Bundled package installation complete!")
    print("=" * 70 + "\n")


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        # Run standard install
        install.run(self)
        # Install bundled packages
        self.execute(install_bundled_packages, [], msg="Installing bundled packages")


class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        # Run standard develop
        develop.run(self)
        # Install bundled packages
        self.execute(install_bundled_packages, [], msg="Installing bundled packages")


class PostInstallScriptsCommand(install_scripts):
    """Post-installation for scripts - runs after wheel install."""
    def run(self):
        install_scripts.run(self)
        
        # Find where the package was installed
        install_dir = self.install_dir
        if install_dir:
            # Try to locate the libs directory
            # The package data should be in site-packages/client/libs/
            import site
            for site_dir in site.getsitepackages():
                libs_dir = Path(site_dir) / 'client' / 'libs'
                if libs_dir.exists():
                    print(f"\n[INFO] Found bundled packages at: {libs_dir}")
                    
                    bundled_packages = [
                        'nslogger-1.0.0.tar.gz',
                        'trading_api-1.0.0.tar.gz'
                    ]
                    
                    print("\n" + "=" * 70)
                    print("Installing bundled packages...")
                    print("=" * 70)
                    
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
                                print(f"   [FAIL] Failed to install {tar_file}: {e}")
                        else:
                            print(f"   [WARN] {tar_file} not found at {tar_path}")
                    
                    print("\n" + "=" * 70)
                    print("Bundled package installation complete!")
                    print("=" * 70 + "\n")
                    break


setup(
    name="trading-api-monitor",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Option Chain Monitor - REST API for real-time option chain monitoring",
    long_description="Option Chain Monitor - REST API for real-time option chain monitoring",
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/trading-api-monitor",
    license="MIT",
    
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*"]),
    py_modules=["option_chain_monitor_api_simple", "post_install"],
    
    include_package_data=True,
    package_data={
        "client": [
            "libs/*.tar.gz",
            "libs/trading_api-1.0.0.tar.gz",
            "libs/nslogger-1.0.0.tar.gz",
        ],
        "*": [
            "requirements.txt",
        ],
    },
    
    install_requires=[
        "Flask>=2.3.0",
        "requests>=2.28.0",
        "urllib3>=1.26.0",
        "python-dotenv>=0.21.0",
        "certifi>=2023.0.0",
    ],
    
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    
    entry_points={
        "console_scripts": [
            "option-chain-monitor=option_chain_monitor_api_simple:main",
            "trading-api-post-install=post_install:main",
        ],
    },
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    
    zip_safe=False,
    
    # Custom commands for bundled package installation
    cmdclass={
        'install': PostInstallCommand,
        'develop': PostDevelopCommand,
        'install_scripts': PostInstallScriptsCommand,
    },
)