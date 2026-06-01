#!/usr/bin/env python3
"""Setup script for ports-app"""

from setuptools import setup, find_packages

setup(
    name="ports-app",
    version="1.0.0",
    description="Monitor and manage open ports on macOS",
    author="Ricardo",
    author_email="ricardogatica@mine-class.cl",
    url="https://github.com/ricardogatica/ports-app",
    license="Apache-2.0",
    py_modules=["ports_app"],
    install_requires=[
        "textual>=0.80.0",
    ],
    entry_points={
        "console_scripts": [
            "ports-app=ports_app:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: Spanish",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Monitoring",
    ],
    python_requires=">=3.8",
)
