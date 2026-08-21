"""Test configuration for the bundled aiobookoo-ultra library."""

import sys
from pathlib import Path

BUNDLED_LIBRARY = (
    Path(__file__).parents[1]
    / "custom_components"
    / "bookoo"
    / "external"
    / "aiobookoo-Ultra"
)
sys.path.insert(0, str(BUNDLED_LIBRARY))
