#!/usr/bin/env python3
"""Setup script for bahia"""

from pathlib import Path
from setuptools import setup, find_packages

VERSION = (Path(__file__).parent / "VERSION").read_text().strip()

setup(
    name="bahia",
    version=VERSION,
    description="Monitor and manage open ports on macOS",
    author="Ricardo Gatica",
    author_email="hola@ricardogatica.com",
    url="https://github.com/ricardogatica/bahia",
    license="Apache-2.0",
    py_modules=["bahia"],
    install_requires=[
        "textual>=0.80.0",
    ],
    entry_points={
        "console_scripts": [
            "bahia=bahia:main",
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
