"""Kompatibilitätspaket für bestehende Importe.

Offizieller Pfad ist `aiobookoo_ultra`; dieses Paket leitet lediglich weiter.
"""

import aiobookoo_ultra as _aiobookoo_ultra
from aiobookoo_ultra import *  # noqa: F401,F403

__all__ = _aiobookoo_ultra.__all__  # type: ignore[attr-defined]
