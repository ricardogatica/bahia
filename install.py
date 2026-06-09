#!/usr/bin/env python3
"""
Cross-platform installer for Bahia
Works on macOS, Linux, Windows
"""

import sys
import subprocess
import os
from pathlib import Path


def print_header():
    print("\n" + "=" * 40)
    print("  BAHIA - Installation")
    print("  macOS Port Monitor TUI")
    print("=" * 40 + "\n")


def check_python():
    """Check Python version"""
    print("🔍 Checking Python...")
    print(f"   Version: {sys.version}")

    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)

    print("   ✓ OK\n")


def install_dependencies():
    """Install required packages"""
    print("📦 Installing dependencies...")

    packages = ["textual"]

    for package in packages:
        print(f"   Installing: {package}...", end=" ", flush=True)
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("✓")
        except subprocess.CalledProcessError:
            print("✗")
            print(f"\n❌ Failed to install {package}")
            print(f"Try manually: {sys.executable} -m pip install {package}")
            sys.exit(1)

    print()


def install_globally():
    """Try to install as global command"""
    print("🌍 Attempting global installation...")

    script_dir = Path(__file__).parent

    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-e", str(script_dir), "-q"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("   ✓ Installed globally\n")
        return True
    except subprocess.CalledProcessError:
        print("   ⚠ Global install failed (optional)\n")
        return False


def print_summary(global_install):
    """Print summary and next steps"""
    print("=" * 40)
    print("  Installation Complete! ✓")
    print("=" * 40 + "\n")

    if global_install:
        print("Run from anywhere:")
        print("  bahia\n")
    else:
        script_dir = Path(__file__).parent
        print("Run from project directory:")
        print(f"  {sys.executable} {script_dir / 'bahia.py'}\n")
        print("Or:")
        print(f"  {script_dir / 'bahia'}\n")

    print("Controls in app:")
    print("  ↑↓   Navigate")
    print("  k    Kill process")
    print("  r    Refresh")
    print("  q    Quit")
    print("\n✓ Happy monitoring!\n")


def main():
    """Main installation flow"""
    print_header()

    try:
        check_python()
        install_dependencies()
        global_install = install_globally()
        print_summary(global_install)
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation cancelled\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
