"""Data models for RustChain SDK."""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class HealthStatus:
    """Node health status."""
    ok: bool
    version: Optional[str] = None
    uptime: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HealthStatus":
        return cls(
            ok=data.get("ok", False),
            version=data.get("version"),
            uptime=data.get("uptime"),
        )


@dataclass
class Miner:
    """Active miner information."""
    miner_id: str
    hardware_class: Optional[str] = None
    multiplier: Optional[float] = None
    last_attestation: Optional[datetime] = None
    total_attestations: Optional[int] = None
    rtc_earned: Optional[float] = None
    cpu_info: Optional[str] = None
    os_info: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Miner":
        last_attest = data.get("last_attestation")
        if isinstance(last_attest, str):
            try:
                last_attest = datetime.fromisoformat(last_attest.replace("Z", "+00:00"))
            except:
                last_attest = None
        
        return cls(
            miner_id=data.get("miner_id", data.get("id", "")),
            hardware_class=data.get("hardware_class"),
            multiplier=data.get("multiplier"),
            last_attestation=last_attest,
            total_attestations=data.get("total_attestations"),
            rtc_earned=data.get("rtc_earned"),
            cpu_info=data.get("cpu_info"),
            os_info=data.get("os_info"),
        )


@dataclass
class Epoch:
    """Current epoch information."""
    epoch_number: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_rewards: Optional[float] = None
    participants: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Epoch":
        def parse_time(t):
            if isinstance(t, str):
                try:
                    return datetime.fromisoformat(t.replace("Z", "+00:00"))
                except:
                    return None
            return None
        
        return cls(
            epoch_number=data.get("epoch", data.get("epoch_number", 0)),
            start_time=parse_time(data.get("start_time")),
            end_time=parse_time(data.get("end_time")),
            total_rewards=data.get("total_rewards"),
            participants=data.get("participants"),
        )


@dataclass
class WalletBalance:
    """Wallet balance information."""
    miner_id: str
    balance: float
    pending: Optional[float] = None
    locked: Optional[float] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], miner_id: str = "") -> "WalletBalance":
        return cls(
            miner_id=data.get("miner_id", miner_id),
            balance=float(data.get("balance", 0)),
            pending=data.get("pending"),
            locked=data.get("locked"),
        )


@dataclass  
class Attestation:
    """Attestation submission/response."""
    miner_id: str
    hardware_fingerprint: Dict[str, Any]
    timestamp: Optional[datetime] = None
    accepted: Optional[bool] = None
    reward: Optional[float] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Attestation":
        ts = data.get("timestamp")
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except:
                ts = None
        
        return cls(
            miner_id=data.get("miner_id", ""),
            hardware_fingerprint=data.get("hardware_fingerprint", {}),
            timestamp=ts,
            accepted=data.get("accepted"),
            reward=data.get("reward"),
        )


@dataclass
class LotteryEligibility:
    """Lottery eligibility status."""
    miner_id: str
    eligible: bool
    reason: Optional[str] = None
    tickets: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], miner_id: str = "") -> "LotteryEligibility":
        return cls(
            miner_id=data.get("miner_id", miner_id),
            eligible=data.get("eligible", False),
            reason=data.get("reason"),
            tickets=data.get("tickets"),
        )


@dataclass
class TransferResult:
    """Transfer transaction result."""
    tx_id: str
    from_wallet: str
    to_wallet: str
    amount: float
    success: bool
    error: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TransferResult":
        return cls(
            tx_id=data.get("tx_id", ""),
            from_wallet=data.get("from", data.get("from_wallet", "")),
            to_wallet=data.get("to", data.get("to_wallet", "")),
            amount=float(data.get("amount", 0)),
            success=data.get("success", False),
            error=data.get("error"),
        )
