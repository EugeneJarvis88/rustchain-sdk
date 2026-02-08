"""
RustChain SDK - Python client for RustChain Proof-of-Antiquity blockchain.

Usage:
    from rustchain_sdk import RustChainClient
    
    client = RustChainClient("https://50.28.86.131")
    miners = client.get_miners()
    balance = client.get_balance("my-wallet")
"""

from .client import RustChainClient, AsyncRustChainClient
from .models import Miner, Epoch, WalletBalance, HealthStatus, Attestation
from .exceptions import RustChainError, ConnectionError, APIError

__version__ = "0.1.0"
__all__ = [
    "RustChainClient",
    "AsyncRustChainClient", 
    "Miner",
    "Epoch",
    "WalletBalance",
    "HealthStatus",
    "Attestation",
    "RustChainError",
    "ConnectionError",
    "APIError",
]
