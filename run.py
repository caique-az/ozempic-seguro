#!/usr/bin/env python
"""Start Ozempic Seguro from a source checkout (equivalent to `python -m ozempic_seguro`)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from ozempic_seguro.main import main

if __name__ == "__main__":
    sys.exit(main())
