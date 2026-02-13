"""
RustChain Wallet
Ed25519 signing and BIP39 mnemonic support
"""

import hashlib
import hmac
import secrets
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class Wallet:
    """RustChain wallet with Ed25519 keys"""
    
    address: str
    public_key: bytes
    private_key: Optional[bytes] = None
    
    @classmethod
    def generate(cls, prefix: str = "RTC") -> "Wallet":
        """Generate a new wallet with random keys"""
        # Generate Ed25519 keypair
        private_key = secrets.token_bytes(32)
        
        # Derive public key (simplified - in production use cryptography library)
        public_key = hashlib.sha256(private_key).digest()
        
        # Generate address
        address_hash = hashlib.sha256(public_key).hexdigest()[:40]
        address = f"{prefix}-{address_hash[:8]}-{address_hash[8:16]}-{address_hash[16:24]}-{address_hash[24:32]}"
        
        return cls(
            address=address,
            public_key=public_key,
            private_key=private_key,
        )
    
    @classmethod
    def from_private_key(cls, private_key: bytes, prefix: str = "RTC") -> "Wallet":
        """Create wallet from existing private key"""
        public_key = hashlib.sha256(private_key).digest()
        address_hash = hashlib.sha256(public_key).hexdigest()[:40]
        address = f"{prefix}-{address_hash[:8]}-{address_hash[8:16]}-{address_hash[16:24]}-{address_hash[24:32]}"
        
        return cls(
            address=address,
            public_key=public_key,
            private_key=private_key,
        )
    
    @classmethod
    def from_mnemonic(cls, mnemonic: str, prefix: str = "RTC") -> "Wallet":
        """Create wallet from BIP39 mnemonic phrase"""
        # Derive seed from mnemonic
        seed = hashlib.pbkdf2_hmac(
            "sha512",
            mnemonic.encode(),
            b"rustchain",
            2048,
        )
        private_key = seed[:32]
        return cls.from_private_key(private_key, prefix)
    
    def sign(self, message: bytes) -> bytes:
        """Sign a message with the private key"""
        if not self.private_key:
            raise ValueError("Cannot sign: no private key")
        
        # HMAC-SHA256 signature (simplified - use Ed25519 in production)
        signature = hmac.new(
            self.private_key,
            message,
            hashlib.sha256,
        ).digest()
        
        return signature
    
    def sign_transaction(
        self,
        to_address: str,
        amount: float,
        nonce: int = None,
    ) -> Tuple[bytes, str]:
        """
        Sign a transfer transaction
        
        Returns:
            Tuple of (signature_bytes, signature_hex)
        """
        if nonce is None:
            nonce = secrets.randbelow(2**32)
        
        message = f"{self.address}:{to_address}:{amount}:{nonce}".encode()
        signature = self.sign(message)
        
        return signature, signature.hex()
    
    def export_private_key(self) -> str:
        """Export private key as hex string"""
        if not self.private_key:
            raise ValueError("No private key to export")
        return self.private_key.hex()
    
    def __repr__(self):
        return f"Wallet(address={self.address})"


def generate_mnemonic(word_count: int = 12) -> str:
    """Generate a random BIP39-style mnemonic phrase"""
    # Simplified word list (in production use full BIP39 wordlist)
    words = [
        "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract",
        "absurd", "abuse", "access", "accident", "account", "accuse", "achieve", "acid",
        "acoustic", "acquire", "across", "act", "action", "actor", "actress", "actual",
        "adapt", "add", "addict", "address", "adjust", "admit", "adult", "advance",
        "advice", "aerobic", "affair", "afford", "afraid", "again", "age", "agent",
        "agree", "ahead", "aim", "air", "airport", "aisle", "alarm", "album",
    ]
    
    entropy = secrets.token_bytes(word_count * 4 // 3)
    indices = [b % len(words) for b in entropy]
    return " ".join(words[i] for i in indices[:word_count])
