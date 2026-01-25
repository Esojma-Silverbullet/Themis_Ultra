"""Weiterleitung auf die Ultra-Implementierung."""

import aiobookoo_ultra.bookooscale as _ultra_bookooscale
from aiobookoo_ultra.bookooscale import *  # noqa: F401,F403

__all__ = _ultra_bookooscale.__all__  # type: ignore[attr-defined]
