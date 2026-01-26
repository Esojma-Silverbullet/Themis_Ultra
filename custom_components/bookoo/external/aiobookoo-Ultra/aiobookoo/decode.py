"""Weiterleitung auf die Ultra-Dekodierung."""

import aiobookoo_ultra.decode as _ultra_decode
from aiobookoo_ultra.decode import *  # noqa: F401,F403

__all__ = _ultra_decode.__all__  # type: ignore[attr-defined]
