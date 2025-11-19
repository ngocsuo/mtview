"""Hidemium browser profile management module.

Provides API client for Hidemium local service (default: http://127.0.0.1:2222).
"""

from .client import HidemiumClient
from .exceptions import HidemiumAPIError, HidemiumValidationError

__all__ = ["HidemiumClient", "HidemiumAPIError", "HidemiumValidationError"]
