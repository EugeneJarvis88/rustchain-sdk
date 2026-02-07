"""RustChain SDK Exceptions"""


class RustChainError(Exception):
    """Base exception for RustChain SDK"""
    pass


class ConnectionError(RustChainError):
    """Raised when connection to node fails"""
    pass


class APIError(RustChainError):
    """Raised when API returns an error"""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code
