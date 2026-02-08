"""RustChain API client with sync and async support."""

import time
import logging
from typing import Optional, List, Dict, Any, Union
from urllib.parse import urljoin

import httpx

from .models import (
    HealthStatus,
    Miner,
    Epoch,
    WalletBalance,
    Attestation,
    LotteryEligibility,
    TransferResult,
)
from .exceptions import RustChainError, ConnectionError, APIError

logger = logging.getLogger(__name__)

DEFAULT_NODE_URL = "https://50.28.86.131"
DEFAULT_TIMEOUT = 30.0
DEFAULT_RETRIES = 3
DEFAULT_BACKOFF = 1.0


class RustChainClient:
    """
    Synchronous RustChain API client.
    
    Usage:
        client = RustChainClient()
        miners = client.get_miners()
        balance = client.get_balance("my-wallet")
    
    Args:
        node_url: RustChain node URL (default: https://50.28.86.131)
        verify_ssl: Whether to verify SSL certificates (default: False for self-signed)
        timeout: Request timeout in seconds
        retries: Number of retry attempts
        backoff: Initial backoff delay between retries (exponential)
    """
    
    def __init__(
        self,
        node_url: str = DEFAULT_NODE_URL,
        verify_ssl: bool = False,
        timeout: float = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
        backoff: float = DEFAULT_BACKOFF,
    ):
        self.node_url = node_url.rstrip("/")
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        
        self._client = httpx.Client(
            base_url=self.node_url,
            verify=verify_ssl,
            timeout=timeout,
        )
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
    
    def close(self):
        """Close the HTTP client."""
        self._client.close()
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        last_error = None
        
        for attempt in range(self.retries):
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
                last_error = ConnectionError(f"Connection failed: {e}")
            except httpx.TimeoutException as e:
                last_error = ConnectionError(f"Request timeout: {e}")
            except httpx.HTTPError as e:
                last_error = RustChainError(f"HTTP error: {e}")
            
            if attempt < self.retries - 1:
                sleep_time = self.backoff * (2 ** attempt)
                logger.debug(f"Retry {attempt + 1}/{self.retries} in {sleep_time}s")
                time.sleep(sleep_time)
        
        raise last_error or RustChainError("Request failed")
    
    # Health & Status
    
    def health(self) -> HealthStatus:
        """Check node health status."""
        data = self._request("GET", "/health")
        return HealthStatus.from_dict(data)
    
    def is_healthy(self) -> bool:
        """Quick health check returning boolean."""
        try:
            return self.health().ok
        except:
            return False
    
    # Miners
    
    def get_miners(self) -> List[Miner]:
        """Get list of all active miners."""
        data = self._request("GET", "/api/miners")
        miners_list = data if isinstance(data, list) else data.get("miners", [])
        return [Miner.from_dict(m) for m in miners_list]
    
    def get_miner(self, miner_id: str) -> Optional[Miner]:
        """Get specific miner by ID."""
        miners = self.get_miners()
        for miner in miners:
            if miner.miner_id == miner_id:
                return miner
        return None
    
    # Wallet
    
    def get_balance(self, miner_id: str) -> WalletBalance:
        """Get wallet balance for a miner."""
        data = self._request("GET", "/wallet/balance", params={"miner_id": miner_id})
        return WalletBalance.from_dict(data, miner_id)
    
    def transfer(
        self,
        from_wallet: str,
        to_wallet: str,
        amount: float,
        private_key: str,
    ) -> TransferResult:
        """
        Transfer RTC between wallets.
        
        Args:
            from_wallet: Source wallet/miner ID
            to_wallet: Destination wallet/miner ID
            amount: Amount of RTC to transfer
            private_key: Private key for signing (hex or base64)
        """
        payload = {
            "from": from_wallet,
            "to": to_wallet,
            "amount": amount,
            "signature": private_key,  # Node handles signing verification
        }
        data = self._request("POST", "/wallet/transfer/signed", json=payload)
        return TransferResult.from_dict(data)
    
    # Epoch
    
    def get_epoch(self) -> Epoch:
        """Get current epoch information."""
        data = self._request("GET", "/epoch")
        return Epoch.from_dict(data)
    
    # Lottery
    
    def check_eligibility(self, miner_id: str) -> LotteryEligibility:
        """Check lottery eligibility for a miner."""
        data = self._request("GET", "/lottery/eligibility", params={"miner_id": miner_id})
        return LotteryEligibility.from_dict(data, miner_id)
    
    # Attestations
    
    def submit_attestation(self, payload: Dict[str, Any]) -> Attestation:
        """
        Submit an attestation to the network.
        
        Args:
            payload: Attestation payload with hardware fingerprint data
        """
        data = self._request("POST", "/attest/submit", json=payload)
        return Attestation.from_dict(data)


class AsyncRustChainClient:
    """
    Asynchronous RustChain API client.
    
    Usage:
        async with AsyncRustChainClient() as client:
            miners = await client.get_miners()
            balance = await client.get_balance("my-wallet")
    """
    
    def __init__(
        self,
        node_url: str = DEFAULT_NODE_URL,
        verify_ssl: bool = False,
        timeout: float = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
        backoff: float = DEFAULT_BACKOFF,
    ):
        self.node_url = node_url.rstrip("/")
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            base_url=self.node_url,
            verify=self.verify_ssl,
            timeout=self.timeout,
        )
        return self
    
    async def __aexit__(self, *args):
        await self.close()
    
    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        import asyncio
        
        if not self._client:
            self._client = httpx.AsyncClient(
                base_url=self.node_url,
                verify=self.verify_ssl,
                timeout=self.timeout,
            )
        
        last_error = None
        
        for attempt in range(self.retries):
            try:
                response = await self._client.request(
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
                last_error = ConnectionError(f"Connection failed: {e}")
            except httpx.TimeoutException as e:
                last_error = ConnectionError(f"Request timeout: {e}")
            except httpx.HTTPError as e:
                last_error = RustChainError(f"HTTP error: {e}")
            
            if attempt < self.retries - 1:
                sleep_time = self.backoff * (2 ** attempt)
                logger.debug(f"Retry {attempt + 1}/{self.retries} in {sleep_time}s")
                await asyncio.sleep(sleep_time)
        
        raise last_error or RustChainError("Request failed")
    
    # Health & Status
    
    async def health(self) -> HealthStatus:
        """Check node health status."""
        data = await self._request("GET", "/health")
        return HealthStatus.from_dict(data)
    
    async def is_healthy(self) -> bool:
        """Quick health check returning boolean."""
        try:
            return (await self.health()).ok
        except:
            return False
    
    # Miners
    
    async def get_miners(self) -> List[Miner]:
        """Get list of all active miners."""
        data = await self._request("GET", "/api/miners")
        miners_list = data if isinstance(data, list) else data.get("miners", [])
        return [Miner.from_dict(m) for m in miners_list]
    
    async def get_miner(self, miner_id: str) -> Optional[Miner]:
        """Get specific miner by ID."""
        miners = await self.get_miners()
        for miner in miners:
            if miner.miner_id == miner_id:
                return miner
        return None
    
    # Wallet
    
    async def get_balance(self, miner_id: str) -> WalletBalance:
        """Get wallet balance for a miner."""
        data = await self._request("GET", "/wallet/balance", params={"miner_id": miner_id})
        return WalletBalance.from_dict(data, miner_id)
    
    async def transfer(
        self,
        from_wallet: str,
        to_wallet: str,
        amount: float,
        private_key: str,
    ) -> TransferResult:
        """Transfer RTC between wallets."""
        payload = {
            "from": from_wallet,
            "to": to_wallet,
            "amount": amount,
            "signature": private_key,
        }
        data = await self._request("POST", "/wallet/transfer/signed", json=payload)
        return TransferResult.from_dict(data)
    
    # Epoch
    
    async def get_epoch(self) -> Epoch:
        """Get current epoch information."""
        data = await self._request("GET", "/epoch")
        return Epoch.from_dict(data)
    
    # Lottery
    
    async def check_eligibility(self, miner_id: str) -> LotteryEligibility:
        """Check lottery eligibility for a miner."""
        data = await self._request("GET", "/lottery/eligibility", params={"miner_id": miner_id})
        return LotteryEligibility.from_dict(data, miner_id)
    
    # Attestations
    
    async def submit_attestation(self, payload: Dict[str, Any]) -> Attestation:
        """Submit an attestation to the network."""
        data = await self._request("POST", "/attest/submit", json=payload)
        return Attestation.from_dict(data)
