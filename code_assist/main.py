#!/usr/bin/env python3
"""
Code Assist CLI - Main Entry Point
Interactive AI-powered development companion
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cli.commands import cli

if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        print("\n👋 Goodbye! Thanks for using Code Assist!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        sys.exit(1)


# E:\Javascript        