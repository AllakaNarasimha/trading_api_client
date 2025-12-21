#!/usr/bin/env python3
"""
Setup script for trading-api-monitor package.

Usage:
    python setup.py install
    python -m pip install .
    python -m pip install -e .  # Development mode
"""

from setuptools import setup, find_packages

setup(
    name="trading-api-monitor",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Option Chain Monitor - REST API for real-time option chain monitoring",
    long_description=open("doc/README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/trading-api-monitor",
    license="MIT",
    
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*"]),
    py_modules=["option_chain_monitor_api_simple"],
    
    include_package_data=True,
    package_data={
        "client": [
            "libs/*.tar.gz",
            "libs/trading_api-1.0.0.tar.gz",
            "libs/nslogger-1.0.0.tar.gz",
        ],
    },
    
    python_requires=">=3.11",
    
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
)
