#!/usr/bin/env python3
"""Main CLI entry point - redirects to index_series functionality."""
import sys

from .index_series import main

if __name__ == "__main__":
    sys.exit(main())
