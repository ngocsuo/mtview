class ProxyAPIError(Exception):
    """Raised when the proxy API returns an unexpected status or structure."""


class ProxyValidationError(Exception):
    """Raised when input parameters are invalid before sending to API."""
