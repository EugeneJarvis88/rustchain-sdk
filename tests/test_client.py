"""Tests for RustChain SDK client."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from rustchain_sdk import RustChainClient, AsyncRustChainClient
from rustchain_sdk.models import HealthStatus, Miner, Epoch, WalletBalance
from rustchain_sdk.exceptions import RustChainError, ConnectionError, APIError


class TestRustChainClient:
    """Tests for synchronous client."""
    
    def test_client_init(self):
        """Test client initialization."""
        client = RustChainClient()
        assert client.node_url == "https://50.28.86.131"
        assert client.verify_ssl == False
        assert client.timeout == 30.0
        assert client.retries == 3
        client.close()
    
    def test_client_custom_url(self):
        """Test client with custom URL."""
        client = RustChainClient(node_url="https://custom.node.com/")
        assert client.node_url == "https://custom.node.com"
        client.close()
    
    def test_client_context_manager(self):
        """Test client as context manager."""
        with RustChainClient() as client:
            assert client is not None
    
    @patch.object(RustChainClient, '_request')
    def test_health(self, mock_request):
        """Test health endpoint."""
        mock_request.return_value = {"ok": True, "version": "1.0.0"}
        
        with RustChainClient() as client:
            health = client.health()
            
        assert health.ok == True
        assert health.version == "1.0.0"
        mock_request.assert_called_once_with("GET", "/health")
    
    @patch.object(RustChainClient, '_request')
    def test_get_miners(self, mock_request):
        """Test get miners endpoint."""
        mock_request.return_value = [
            {"miner_id": "miner1", "hardware_class": "PowerPC G4", "multiplier": 2.5},
            {"miner_id": "miner2", "hardware_class": "x86_64", "multiplier": 1.0},
        ]
        
        with RustChainClient() as client:
            miners = client.get_miners()
        
        assert len(miners) == 2
        assert miners[0].miner_id == "miner1"
        assert miners[0].hardware_class == "PowerPC G4"
        assert miners[0].multiplier == 2.5
    
    @patch.object(RustChainClient, '_request')
    def test_get_balance(self, mock_request):
        """Test get balance endpoint."""
        mock_request.return_value = {"balance": 123.456, "pending": 10.0}
        
        with RustChainClient() as client:
            balance = client.get_balance("my-wallet")
        
        assert balance.miner_id == "my-wallet"
        assert balance.balance == 123.456
        assert balance.pending == 10.0
        mock_request.assert_called_once_with(
            "GET", "/wallet/balance", params={"miner_id": "my-wallet"}
        )
    
    @patch.object(RustChainClient, '_request')
    def test_get_epoch(self, mock_request):
        """Test get epoch endpoint."""
        mock_request.return_value = {"epoch": 42, "participants": 10}
        
        with RustChainClient() as client:
            epoch = client.get_epoch()
        
        assert epoch.epoch_number == 42
        assert epoch.participants == 10
    
    @patch.object(RustChainClient, '_request')
    def test_is_healthy_true(self, mock_request):
        """Test is_healthy returns True."""
        mock_request.return_value = {"ok": True}
        
        with RustChainClient() as client:
            assert client.is_healthy() == True
    
    @patch.object(RustChainClient, '_request')
    def test_is_healthy_false_on_error(self, mock_request):
        """Test is_healthy returns False on error."""
        mock_request.side_effect = ConnectionError("Failed")
        
        with RustChainClient() as client:
            assert client.is_healthy() == False


class TestModels:
    """Tests for data models."""
    
    def test_health_status_from_dict(self):
        """Test HealthStatus.from_dict."""
        data = {"ok": True, "version": "1.0", "uptime": 3600}
        status = HealthStatus.from_dict(data)
        
        assert status.ok == True
        assert status.version == "1.0"
        assert status.uptime == 3600
    
    def test_miner_from_dict(self):
        """Test Miner.from_dict."""
        data = {
            "miner_id": "test-miner",
            "hardware_class": "PowerPC G5",
            "multiplier": 3.0,
            "rtc_earned": 100.5,
        }
        miner = Miner.from_dict(data)
        
        assert miner.miner_id == "test-miner"
        assert miner.hardware_class == "PowerPC G5"
        assert miner.multiplier == 3.0
        assert miner.rtc_earned == 100.5
    
    def test_miner_from_dict_with_id_field(self):
        """Test Miner.from_dict with 'id' instead of 'miner_id'."""
        data = {"id": "alt-miner", "multiplier": 1.5}
        miner = Miner.from_dict(data)
        
        assert miner.miner_id == "alt-miner"
    
    def test_wallet_balance_from_dict(self):
        """Test WalletBalance.from_dict."""
        data = {"balance": 50.0, "pending": 5.0, "locked": 0.0}
        balance = WalletBalance.from_dict(data, "test-wallet")
        
        assert balance.miner_id == "test-wallet"
        assert balance.balance == 50.0
        assert balance.pending == 5.0
    
    def test_epoch_from_dict(self):
        """Test Epoch.from_dict."""
        data = {
            "epoch": 100,
            "participants": 25,
            "total_rewards": 1000.0,
        }
        epoch = Epoch.from_dict(data)
        
        assert epoch.epoch_number == 100
        assert epoch.participants == 25
        assert epoch.total_rewards == 1000.0


class TestExceptions:
    """Tests for exceptions."""
    
    def test_rustchain_error(self):
        """Test RustChainError."""
        error = RustChainError("Test error", status_code=500)
        assert error.message == "Test error"
        assert error.status_code == 500
        assert str(error) == "Test error"
    
    def test_connection_error(self):
        """Test ConnectionError."""
        error = ConnectionError("Connection refused")
        assert error.message == "Connection refused"
        assert isinstance(error, RustChainError)
    
    def test_api_error(self):
        """Test APIError."""
        error = APIError("Not found", status_code=404)
        assert error.status_code == 404
        assert isinstance(error, RustChainError)


@pytest.mark.asyncio
class TestAsyncClient:
    """Tests for async client."""
    
    async def test_async_client_init(self):
        """Test async client initialization."""
        async with AsyncRustChainClient() as client:
            assert client.node_url == "https://50.28.86.131"
    
    @patch('rustchain_sdk.client.httpx.AsyncClient')
    async def test_async_health(self, mock_client_class):
        """Test async health endpoint."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"ok": True}
        
        mock_client = MagicMock()
        mock_client.request = MagicMock(return_value=mock_response)
        mock_client.aclose = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Make request an async mock
        async def async_request(*args, **kwargs):
            return mock_response
        mock_client.request = async_request
        
        async def async_close():
            pass
        mock_client.aclose = async_close
        
        async with AsyncRustChainClient() as client:
            health = await client.health()
        
        assert health.ok == True
