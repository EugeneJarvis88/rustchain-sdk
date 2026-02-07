# RustChain Python SDK

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official Python SDK for [RustChain](https://github.com/Scottcjn/Rustchain) - a Proof-of-Antiquity blockchain that rewards vintage hardware.

## Installation

```bash
pip install git+https://github.com/EugeneJarvis88/rustchain-sdk.git
```

Or install from source:
```bash
git clone https://github.com/EugeneJarvis88/rustchain-sdk.git
cd rustchain-sdk
pip install -e .
```

## Quick Start

```python
from rustchain import RustChainClient

# Connect to RustChain node
client = RustChainClient("https://50.28.86.131")

# Get node health
health = client.health()
print(f"Node status: {health.status}, version: {health.version}")

# List active miners
miners = client.get_miners()
for miner in miners:
    print(f"Miner: {miner.miner_id}, Hardware: {miner.hardware}, Multiplier: {miner.multiplier}x")

# Check balance
balance = client.get_balance("my-miner-id")
print(f"Balance: {balance} RTC")

# Get epoch info
epoch = client.get_epoch()
print(f"Current epoch: {epoch.epoch}, Rewards: {epoch.total_rewards} RTC")
```

## Async Support

```python
import asyncio
from rustchain.client import AsyncRustChainClient

async def main():
    async with AsyncRustChainClient() as client:
        miners = await client.get_miners()
        print(f"Found {len(miners)} active miners")

asyncio.run(main())
```

## Wallet Management

```python
from rustchain import Wallet
from rustchain.wallet import generate_mnemonic

# Generate new wallet
wallet = Wallet.generate()
print(f"Address: {wallet.address}")

# From mnemonic
mnemonic = generate_mnemonic()
wallet = Wallet.from_mnemonic(mnemonic)

# Sign transaction
signature, sig_hex = wallet.sign_transaction(
    to_address="RTC-abcd1234-efgh5678-ijkl9012",
    amount=10.0
)
```

## API Reference

### RustChainClient

| Method | Description |
|--------|-------------|
| `health()` | Get node health status |
| `get_miners()` | List all active miners |
| `get_balance(miner_id)` | Get wallet balance |
| `get_epoch()` | Get current epoch info |
| `check_eligibility(miner_id)` | Check lottery eligibility |
| `submit_attestation(payload)` | Submit hardware attestation |
| `transfer(from, to, amount, sig)` | Transfer RTC |

### Configuration

```python
client = RustChainClient(
    node_url="https://50.28.86.131",  # Node URL
    verify_ssl=False,                  # SSL verification (False for self-signed)
    timeout=30.0,                      # Request timeout
    max_retries=3,                     # Retry attempts
    retry_delay=1.0,                   # Initial retry delay (exponential backoff)
)
```

## Error Handling

```python
from rustchain import RustChainClient, ConnectionError, APIError

try:
    client = RustChainClient()
    miners = client.get_miners()
except ConnectionError as e:
    print(f"Failed to connect: {e}")
except APIError as e:
    print(f"API error (status {e.status_code}): {e}")
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## Resources

- [RustChain Repo](https://github.com/Scottcjn/Rustchain)
- [Bounties](https://github.com/Scottcjn/rustchain-bounties)
- [Node API](https://50.28.86.131/health)

## License

MIT License - see LICENSE file.

---

Built for [RustChain Bounty #36](https://github.com/Scottcjn/rustchain-bounties/issues/36)

Wallet: `zARG9WZCiRRzghuCzx1kqSynhYanBnGdjfz4kjSjvin`
