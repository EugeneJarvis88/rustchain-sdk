"""RustChain CLI tool."""

import argparse
import json
import sys
from typing import Optional

from .client import RustChainClient, DEFAULT_NODE_URL
from .exceptions import RustChainError


def main():
    parser = argparse.ArgumentParser(
        prog="rustchain-cli",
        description="RustChain Proof-of-Antiquity CLI",
    )
    parser.add_argument(
        "--node", "-n",
        default=DEFAULT_NODE_URL,
        help=f"Node URL (default: {DEFAULT_NODE_URL})",
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # health
    subparsers.add_parser("health", help="Check node health")
    
    # miners
    subparsers.add_parser("miners", help="List active miners")
    
    # balance
    balance_parser = subparsers.add_parser("balance", help="Get wallet balance")
    balance_parser.add_argument("miner_id", help="Miner/wallet ID")
    
    # epoch
    subparsers.add_parser("epoch", help="Get current epoch info")
    
    # eligibility
    elig_parser = subparsers.add_parser("eligibility", help="Check lottery eligibility")
    elig_parser.add_argument("miner_id", help="Miner ID")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    try:
        with RustChainClient(node_url=args.node) as client:
            result = None
            
            if args.command == "health":
                health = client.health()
                if args.json:
                    result = {"ok": health.ok, "version": health.version}
                else:
                    status = "✅ Healthy" if health.ok else "❌ Unhealthy"
                    print(f"Node Status: {status}")
                    if health.version:
                        print(f"Version: {health.version}")
            
            elif args.command == "miners":
                miners = client.get_miners()
                if args.json:
                    result = [
                        {
                            "id": m.miner_id,
                            "hardware": m.hardware_class,
                            "multiplier": m.multiplier,
                            "rtc": m.rtc_earned,
                        }
                        for m in miners
                    ]
                else:
                    print(f"Active Miners ({len(miners)}):\n")
                    for m in miners:
                        mult = f"x{m.multiplier}" if m.multiplier else ""
                        hw = m.hardware_class or "unknown"
                        rtc = f"{m.rtc_earned:.2f} RTC" if m.rtc_earned else ""
                        print(f"  • {m.miner_id} [{hw}] {mult} {rtc}")
            
            elif args.command == "balance":
                bal = client.get_balance(args.miner_id)
                if args.json:
                    result = {"miner_id": bal.miner_id, "balance": bal.balance}
                else:
                    print(f"Wallet: {bal.miner_id}")
                    print(f"Balance: {bal.balance:.4f} RTC")
                    if bal.pending:
                        print(f"Pending: {bal.pending:.4f} RTC")
            
            elif args.command == "epoch":
                epoch = client.get_epoch()
                if args.json:
                    result = {"epoch": epoch.epoch_number}
                else:
                    print(f"Current Epoch: {epoch.epoch_number}")
                    if epoch.participants:
                        print(f"Participants: {epoch.participants}")
                    if epoch.total_rewards:
                        print(f"Total Rewards: {epoch.total_rewards:.2f} RTC")
            
            elif args.command == "eligibility":
                elig = client.check_eligibility(args.miner_id)
                if args.json:
                    result = {
                        "miner_id": elig.miner_id,
                        "eligible": elig.eligible,
                        "tickets": elig.tickets,
                    }
                else:
                    status = "✅ Eligible" if elig.eligible else "❌ Not Eligible"
                    print(f"Lottery Status: {status}")
                    if elig.tickets:
                        print(f"Tickets: {elig.tickets}")
                    if elig.reason:
                        print(f"Reason: {elig.reason}")
            
            if args.json and result:
                print(json.dumps(result, indent=2))
    
    except RustChainError as e:
        print(f"Error: {e.message}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
