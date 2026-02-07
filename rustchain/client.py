"""
RustChain API Client
Synchronous and async wrappers for RustChain node API
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import httpx

from .exceptions import RustChainError, ConnectionError, APIError


@dataclass
class Miner:
    """Represents a RustChain miner"""
    miner_id: str
    wallet: str
    hardware: str
    multiplier: float
    last_seen: str
    attestations: int
    
    @classmethod
    def from_dict(cls, data: dict) -> "Miner":
        return cls(
            miner_id=data.get("miner_id", ""),
            wallet=data.get("wallet", ""),
            hardware=data.get("hardware", "unknown"),
            multiplier=data.get("multiplier", 1.0),
            last_seen=data.get("last_seen", ""),
            attestations=data.get("attestations", 0),
        )


@dataclass
class EpochInfo:
    """Current epoch information"""
    epoch: int
    start_time: str
    end_time: str
    total_rewards: float
    miners_count: int


@dataclass 
class HealthStatus:
    """Node health status"""
    status: str
    version: str
    uptime: int
    peers: int
    last_block: int


class RustChainClient:
    """
    RustChain API Client
    
    Usage:
        client = RustChainClient("https://50.28.86.131")
        miners = client.get_miners()
        balance = client.get_balance("my-wallet")
    """
    
    DEFAULT_NODE = "https://50.28.86.131"
    
    def __init__(
        self,
        node_url: str = None,
        verify_ssl: bool = False,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """
        Initialize RustChain client.
        
        Args:
            node_url: RustChain node URL (default: https://50.28.86.131)
            verify_ssl: Verify SSL certificate (default: False for self-signed)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts on failure
            retry_delay: Initial delay between retries (exponential backoff)
        """
        self.node_url = (node_url or self.DEFAULT_NODE).rstrip("/")
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self._client = httpx.Client(
            base_url=self.node_url,
            verify=self.verify_ssl,
            timeout=self.timeout,
        )
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
        json: Dict = None,
    ) -> Any:
        """Make HTTP request with retry logic"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = self._client.request(
                    method=method,
                    url=endpoint,
                    params=params,
                    json=json,
                )
                
                if response.status_code >= 400:
                    raise APIError(
                        f"API error: {response.text}",
                        status_code=response.status_code,
                    )
                
                return response.json()
                
            except httpx.ConnectError as e:
                last_error = ConnectionError(f"Failed to connect to {self.node_url}: {e}")
            except httpx.TimeoutException as e:
                last_error = ConnectionError(f"Request timed out: {e}")
            except Exception as e:
                last_error = RustChainError(f"Request failed: {e}")
            
            if attempt < self.max_retries - 1:
                delay = self.retry_delay * (2 ** attempt)
                time.sleep(delay)
        
        raise last_error
    
    def health(self) -> HealthStatus:
        """Get node health status"""
        data = self._request("GET", "/health")
        return HealthStatus(
            status=data.get("status", "unknown"),
            version=data.get("version", ""),
            uptime=data.get("uptime", 0),
            peers=data.get("peers", 0),
            last_block=data.get("last_block", 0),
        )
    
    def get_miners(self) -> List[Miner]:
        """Get list of active miners"""
        data = self._request("GET", "/api/miners")
        miners = data if isinstance(data, list) else data.get("miners", [])
        return [Miner.from_dict(m) for m in miners]
    
    def get_balance(self, miner_id: str) -> float:
        """Get wallet balance for a miner"""
        data = self._request("GET", "/wallet/balance", params={"miner_id": miner_id})
        return float(data.get("balance", 0))
    
    def get_epoch(self) -> EpochInfo:
        """Get current epoch information"""
        data = self._request("GET", "/epoch")
        return EpochInfo(
            epoch=data.get("epoch", 0),
            start_time=data.get("start_time", ""),
            end_time=data.get("end_time", ""),
            total_rewards=data.get("total_rewards", 0),
            miners_count=data.get("miners_count", 0),
        )
    
    def check_eligibility(self, miner_id: str) -> Dict:
        """Check lottery eligibility for a miner"""
        return self._request("GET", "/lottery/eligibility", params={"miner_id": miner_id})
    
    def submit_attestation(self, payload: Dict) -> Dict:
        """Submit hardware attestation"""
        return self._request("POST", "/attest/submit", json=payload)
    
    def transfer(
        self,
        from_wallet: str,
        to_wallet: str,
        amount: float,
        signature: str,
    ) -> Dict:
        """
        Transfer RTC between wallets
        
        Args:
            from_wallet: Source wallet address
            to_wallet: Destination wallet address
            amount: Amount of RTC to transfer
            signature: Ed25519 signature of the transaction
        """
        payload = {
            "from": from_wallet,
            "to": to_wallet,
            "amount": amount,
            "signature": signature,
        }
        return self._request("POST", "/wallet/transfer/signed", json=payload)
    
    def get_attestations(self, miner_id: str = None, limit: int = 100) -> List[Dict]:
        """Get recent attestations"""
        params = {"limit": limit}
        if miner_id:
            params["miner_id"] = miner_id
        return self._request("GET", "/api/attestations", params=params)
    
    def close(self):
        """Close the HTTP client"""
        self._client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()


class AsyncRustChainClient:
    """Async version of RustChain client"""
    
    DEFAULT_NODE = "https://50.28.86.131"
    
    def __init__(
        self,
        node_url: str = None,
        verify_ssl: bool = False,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        self.node_url = (node_url or self.DEFAULT_NODE).rstrip("/")
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._client = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.node_url,
                verify=self.verify_ssl,
                timeout=self.timeout,
            )
        return self._client
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        import asyncio
        client = await self._get_client()
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = await client.request(method, endpoint, **kwargs)
                if response.status_code >= 400:
                    raise APIError(response.text, response.status_code)
                return response.json()
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
        
        raise last_error
    
    async def health(self) -> HealthStatus:
        data = await self._request("GET", "/health")
        return HealthStatus(**data)
    
    async def get_miners(self) -> List[Miner]:
        data = await self._request("GET", "/api/miners")
        miners = data if isinstance(data, list) else data.get("miners", [])
        return [Miner.from_dict(m) for m in miners]
    
    async def get_balance(self, miner_id: str) -> float:
        data = await self._request("GET", "/wallet/balance", params={"miner_id": miner_id})
        return float(data.get("balance", 0))
    
    async def close(self):
        if self._client:
            await self._client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        await self.close()
