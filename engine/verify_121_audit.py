#!/usr/bin/env python3
"""PINAX Audit Verification Engine (Backward Compatibility Entrypoint).

Runs the 171 issues verification engine against the pinax-registry repository.
Provided as an alias for legacy runners expecting verify_121_audit.py.
"""

import os
import sys

# Add directory containing verify_171_audit.py to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from verify_171_audit import main

if __name__ == "__main__":
    main()
