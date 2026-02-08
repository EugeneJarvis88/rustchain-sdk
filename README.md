# RustChain SDK

Python SDK for [RustChain](https://github.com/Scottcjn/Rustchain) Proof-of-Antiquity blockchain.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation

```bash
# From GitHub
pip install git+https://github.com/EugeneJarvis88/rustchain-sdk.git

# Or clone and install locally
git clone https://github.com/EugeneJarvis88/rustchain-sdk.git
cd rustchain-sdk
pip install -e .
```

## Quick Start

```python
from rustchain_sdk import RustChainClient

# Create client (uses default node URL)
client = RustChainClient()

# Check node health
health = client.health()
print(f"Node OK: {health.ok}")

# Get all active miners
miners = client.get_miners()
for miner in miners:
    print(f"{miner.miner_id}: {miner.hardware_class} x{miner.multiplier}")

# Check wallet balance
balance = client.get_balance("my-wallet")
print(f"Balance: {balance.balance} RTC")

# Get current epoch
epoch = client.get_epoch()
print(f"Epoch: {epoch.epoch_number}")
```

## Async Support

```python
import asyncio
from rustchain_sdk import AsyncRustChainClient

async def main():
    async with AsyncRustChainClient() as client:
        miners = await client.get_miners()
        print(f"Active miners: {len(miners)}")
        
        # Parallel requests
        balances = await asyncio.gather(*[
            client.get_balance(m.miner_id) for m in miners[:5]
        ])

asyncio.run(main())
```

## CLI Tool

```bash
# Check node health
rustchain-cli health

# List miners
rustchain-cli miners

# Check balance
rustchain-cli balance my-wallet

# Get epoch info
rustchain-cli epoch

# Check lottery eligibility
rustchain-cli eligibility my-wallet

# JSON output
rustchain-cli miners --json

# Custom node
rustchain-cli --node https://custom-node.example.com miners
```

## API Reference

### RustChainClient

```python
client = RustChainClient(
    node_url="https://50.28.86.131",  # Default RustChain node
    verify_ssl=False,                  # Disable SSL verification (self-signed cert)
    timeout=30.0,                      # Request timeout in seconds
    retries=3,                         # Number of retry attempts
    backoff=1.0,                       # Initial backoff delay (exponential)
)
```

### Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `health()` | Check node health | `HealthStatus` |
| `is_healthy()` | Quick boolean health check | `bool` |
| `get_miners()` | List all active miners | `List[Miner]` |
| `get_miner(id)` | Get specific miner | `Optional[Miner]` |
| `get_balance(id)` | Get wallet balance | `WalletBalance` |
| `get_epoch()` | Get current epoch info | `Epoch` |
| `check_eligibility(id)` | Check lottery eligibility | `LotteryEligibility` |
| `submit_attestation(payload)` | Submit attestation | `Attestation` |
| `transfer(from, to, amount, key)` | Transfer RTC | `TransferResult` |

### Models

```python
@dataclass
class Miner:
    miner_id: str
    hardware_class: Optional[str]
    multiplier: Optional[float]
    last_attestation: Optional[datetime]
    total_attestations: Optional[int]
    rtc_earned: Optional[float]

@dataclass
class WalletBalance:
    miner_id: str
    balance: float
    pending: Optional[float]
    locked: Optional[float]

@dataclass
class Epoch:
    epoch_number: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    total_rewards: Optional[float]
    participants: Optional[int]
```

## Error Handling

```python
from rustchain_sdk import RustChainClient, RustChainError, ConnectionError, APIError

try:
    client = RustChainClient()
    balance = client.get_balance("my-wallet")
except ConnectionError as e:
    print(f"Connection failed: {e.message}")
except APIError as e:
    print(f"API error ({e.status_code}): {e.message}")
except RustChainError as e:
    print(f"Error: {e.message}")
```

## SSL Certificates

The default RustChain node uses a self-signed certificate. SSL verification is disabled by default. To enable it:

```python
client = RustChainClient(verify_ssl=True)
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=rustchain_sdk
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [RustChain Main Repo](https://github.com/Scottcjn/Rustchain)
- [RustChain Bounties](https://github.com/Scottcjn/rustchain-bounties)
- [Node Explorer](https://50.28.86.131/explorer)
