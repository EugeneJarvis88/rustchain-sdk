"""Tests for RustChain SDK"""

import pytest
from rustchain import RustChainClient, Wallet
from rustchain.wallet import generate_mnemonic


class TestWallet:
    def test_generate_wallet(self):
        wallet = Wallet.generate()
        assert wallet.address.startswith("RTC-")
        assert wallet.public_key is not None
        assert wallet.private_key is not None
    
    def test_wallet_from_mnemonic(self):
        mnemonic = generate_mnemonic()
        wallet1 = Wallet.from_mnemonic(mnemonic)
        wallet2 = Wallet.from_mnemonic(mnemonic)
        assert wallet1.address == wallet2.address
    
    def test_sign_transaction(self):
        wallet = Wallet.generate()
        sig_bytes, sig_hex = wallet.sign_transaction(
            to_address="RTC-test-addr-1234",
            amount=10.0
        )
        assert len(sig_bytes) == 32
        assert len(sig_hex) == 64
    
    def test_generate_mnemonic(self):
        mnemonic = generate_mnemonic(12)
        words = mnemonic.split()
        assert len(words) == 12


class TestClientIntegration:
    """Integration tests - require live node"""
    
    @pytest.fixture
    def client(self):
        return RustChainClient("https://50.28.86.131", verify_ssl=False)
    
    @pytest.mark.integration
    def test_health(self, client):
        health = client.health()
        assert health.status is not None
    
    @pytest.mark.integration
    def test_get_miners(self, client):
        miners = client.get_miners()
        assert isinstance(miners, list)
    
    @pytest.mark.integration
    def test_get_epoch(self, client):
        epoch = client.get_epoch()
        assert epoch.epoch >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
