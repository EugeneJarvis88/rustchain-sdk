"""Custom exceptions for RustChain SDK."""

from typing import Optional


class RustChainError(Exception):
    """Base exception for RustChain SDK errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ConnectionError(RustChainError):
    """Raised when connection to node fails."""
    pass


class APIError(RustChainError):
    """Raised when API returns an error response."""
    pass


class ValidationError(RustChainError):
    """Raised when input validation fails."""
    pass


class WalletError(RustChainError):
    """Raised when wallet operations fail."""
    pass
