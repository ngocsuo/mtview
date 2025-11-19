class HidemiumAPIError(Exception):
    """Raised when Hidemium API returns error or unexpected response."""


class HidemiumValidationError(Exception):
    """Raised when input parameters are invalid before calling API."""
