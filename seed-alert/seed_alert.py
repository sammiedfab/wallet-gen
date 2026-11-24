#!/usr/bin/env python3
"""
seed-alert: watch a Telegram channel for posted seed phrases and run a
READ-ONLY safety check on each one before alerting you.

This script never signs, sends or broadcasts anything. It derives the
public address from a posted seed phrase and asks public blockchain RPC
nodes about it (balances, transaction count, contract code), then tells
you whether the wallet looks like a gas trap / sweeper.

Usage:
  python seed_alert.py              # watch the channel (default)
  python seed_alert.py check        # check a seed phrase you paste in
  python seed_alert.py test-alert   # send yourself a test notification
"""

import asyncio
import json
import os
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from getpass import getpass
from pathlib import Path

from eth_account import Account
from eth_account.hdaccount.mnemonic import Language, Mnemonic

HERE = Path(__file__).resolve().parent
Account.enable_unaudited_hdwallet_features()
MNEMONIC = Mnemonic(Language.ENGLISH)
BIP39_WORDS = set(MNEMONIC.wordlist)
PHRASE_LENGTHS = (24, 21, 18, 15, 12)
DERIVATION_PATH = "m/44'/60'/0'/0/0"  # standard path used by MetaMask, Trust Wallet, etc.

# EVM chains to check. Public RPCs, no API key needed.
CHAINS = {
    "Ethereum": {
        "rpc": "https://ethereum-rpc.publicnode.com",
        "coin": "ETH",
        "explorer": "https://etherscan.io/address/",
        "tokens": {
            "USDT": ("0xdAC17F958D2ee523a2206206994597C13D831ec7", 6),
            "USDC": ("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", 6),
        },
    },
    "BNB Chain": {
        "rpc": "https://bsc-rpc.publicnode.com",
        "coin": "BNB",
        "explorer": "https://bscscan.com/address/",
        "tokens": {
            "USDT": ("0x55d398326f99059fF775485246999027B3197955", 18),
            "USDC": ("0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d", 18),
        },
    },
    "Polygon": {
        "rpc": "https://polygon-bor-rpc.publicnode.com",
        "coin": "POL",
        "explorer": "https://polygonscan.com/address/",
        "tokens": {
            "USDT": ("0xc2132D05D31c914a87C6611C10748AEb04B58e8F", 6),
            "USDC": ("0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359", 6),
        },
    },
    "Base": {
        "rpc": "https://base-rpc.publicnode.com",
        "coin": "ETH",
        "explorer": "https://basescan.org/address/",
        "tokens": {
            "USDC": ("0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", 6),
            "USDT": ("0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2", 6),
        },
    },
    "Arbitrum": {
        "rpc": "https://arbitrum-one-rpc.publicnode.com",
        "coin": "ETH",
        "explorer": "https://arbiscan.io/address/",
        "tokens": {
            "USDT": ("0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9", 6),
            "USDC": ("0xaf88d065e77c8cC2239327C5EDb3A432268e5831", 6),
        },
    },
}

# Below this native balance a wallet can't realistically pay for a token transfer.
DUST_NATIVE = 0.0002
# Many outgoing transactions + empty balance = something keeps draining it.
SWEEPER_NONCE = 10


# ---------------------------------------------------------------- config

def load_env(path: Path) -> None:
    """Minimal .env loader so we don't need python-dotenv."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env(HERE / ".env")


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


# ---------------------------------------------------------------- seed detection

def find_seed_phrases(text: str) -> list[str]:
    """Return every valid BIP39 phrase (checksum verified) found in the text.

    Handles plain lists, numbered lists ("1. word 2. word"), commas, new lines.
    """
    tokens = re.findall(r"[a-zA-Z]+", text.lower())
    runs, current = [], []
    for tok in tokens:
        if tok in BIP39_WORDS:
            current.append(tok)
        else:
            if len(current) >= 12:
                runs.append(current)
            current = []
    if len(current) >= 12:
        runs.append(current)

    found = []
    for run in runs:
        i = 0
        while i <= len(run) - 12:
            for length in PHRASE_LENGTHS:
                if i + length > len(run):
                    continue
                phrase = " ".join(run[i:i + length])
                if MNEMONIC.is_mnemonic_valid(phrase):
                    if phrase not in found:
                        found.append(phrase)
                    i += length - 1
                    break
            i += 1
    return found


def address_from_seed(phrase: str) -> str:
    return Account.from_mnemonic(phrase, account_path=DERIVATION_PATH).address


# ---------------------------------------------------------------- read-only chain checks

def rpc(url: str, method: str, params: list):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json", "User-Agent": "seed-alert"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
    if "error" in data:
        raise RuntimeError(data["error"].get("message", str(data["error"])))
    return data["result"]


def erc20_balance(url: str, token: str, owner: str) -> int:
    # balanceOf(address) selector = 0x70a08231
    call = {"to": token, "data": "0x70a08231" + owner[2:].lower().rjust(64, "0")}
    result = rpc(url, "eth_call", [call, "latest"])
    return int(result, 16) if result and result != "0x" else 0


def check_chain(name: str, cfg: dict, address: str) -> dict:
    url = cfg["rpc"]
    out = {"chain": name, "coin": cfg["coin"], "explorer": cfg["explorer"] + address, "flags": []}
    try:
        out["native"] = int(rpc(url, "eth_getBalance", [address, "latest"]), 16) / 1e18
        out["nonce"] = int(rpc(url, "eth_getTransactionCount", [address, "latest"]), 16)
        out["pending_nonce"] = int(rpc(url, "eth_getTransactionCount", [address, "pending"]), 16)
        out["code"] = rpc(url, "eth_getCode", [address, "latest"])
        out["tokens"] = {}
        for sym, (token, decimals) in cfg["tokens"].items():
            try:
                bal = erc20_balance(url, token, address) / (10 ** decimals)
                if bal > 0:
                    out["tokens"][sym] = bal
            except Exception:
                pass
    except Exception as exc:
        out["error"] = str(exc)
        return out

    code = (out["code"] or "0x").lower()
    has_tokens = any(v > 0 for v in out["tokens"].values())
    native = out["native"]

    if code.startswith("0xef0100"):
        delegate = "0x" + code[8:48]
        out["flags"].append(
            ("DANGER", f"Wallet is EIP-7702 delegated to contract {delegate}. "
                       "This is how modern sweepers work: anything sent in is forwarded out automatically.")
        )
    elif code not in ("0x", "0x0"):
        out["flags"].append(("DANGER", "Address has contract code. A normal seed-phrase wallet does not."))

    if out["pending_nonce"] > out["nonce"]:
        out["flags"].append(
            ("DANGER", f"{out['pending_nonce'] - out['nonce']} pending outgoing transaction(s) right now. "
                       "Someone else is actively moving funds from this wallet.")
        )

    if has_tokens and native < DUST_NATIVE:
        out["flags"].append(
            ("TRAP", f"Has tokens but almost no {cfg['coin']} for gas. Classic gas trap: "
                     f"if you send {cfg['coin']} in, a sweeper bot takes it.")
        )

    if out["nonce"] >= SWEEPER_NONCE and native < DUST_NATIVE:
        out["flags"].append(
            ("WARN", f"{out['nonce']} outgoing transactions and an empty balance. "
                     "Something keeps draining this wallet (sweeper pattern).")
        )

    if native >= DUST_NATIVE and not out["flags"]:
        out["flags"].append(
            ("INFO", f"Holds {native:.6f} {cfg['coin']}. Anyone with this seed can move it; "
                     "bots usually do it within seconds.")
        )
    return out


def is_active(r: dict) -> bool:
    return bool(r.get("error") or r.get("flags") or r.get("native", 0) > 0
                or r.get("tokens") or r.get("nonce", 0) > 0)


def safety_check(phrase: str) -> tuple[str, list[dict]]:
    address = address_from_seed(phrase)
    with ThreadPoolExecutor(max_workers=len(CHAINS)) as pool:
        results = list(pool.map(lambda kv: check_chain(kv[0], kv[1], address), CHAINS.items()))
    return address, results


def verdict(results: list[dict]) -> str:
    levels = {lvl for r in results for lvl, _ in r.get("flags", [])}
    if "DANGER" in levels:
        return "🚨 DANGER: sweeper / drainer detected"
    if "TRAP" in levels:
        return "🪤 GAS TRAP: tokens but no gas"
    if "WARN" in levels:
        return "⚠️ SUSPICIOUS: looks drained by a bot"
    if not any(is_active(r) for r in results):
        return "∅ EMPTY: nothing on the checked chains"
    return "ℹ️ No trap signs found on the checked chains"


def format_report(phrase: str, address: str, results: list[dict], source: str = "") -> str:
    lines = [verdict(results), ""]
    if source:
        lines.append(f"Post: {source}")
    lines.append(f"Address: {address}")
    lines.append(f"Seed: {len(phrase.split())} words, starts '{' '.join(phrase.split()[:2])} …'")
    lines.append("")
    for r in results:
        if not is_active(r):
            continue
        if r.get("error"):
            lines.append(f"• {r['chain']}: could not check ({r['error'][:80]})")
            continue
        toks = ", ".join(f"{v:,.2f} {k}" for k, v in r["tokens"].items())
        lines.append(
            f"• {r['chain']}: {r['native']:.6f} {r['coin']}"
            + (f" | {toks}" if toks else "")
            + f" | {r['nonce']} txs sent"
        )
        for lvl, msg in r["flags"]:
            lines.append(f"   [{lvl}] {msg}")
        lines.append(f"   {r['explorer']}")
    if not any(is_active(r) for r in results):
        lines.append("Checked: " + ", ".join(CHAINS) + ". It may be on another chain (Tron, Solana, …)")
        lines.append("or hold tokens this script doesn't list. Look the address up on a block explorer.")
    lines += [
        "",
        "❌ Never send gas or any funds to a wallet whose seed phrase is public.",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------- notifications

def bot_send(token: str, chat_id: int, text: str) -> None:
    body = json.dumps({"chat_id": chat_id, "text": text, "disable_web_page_preview": True}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=body, headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(req, timeout=15).read()


class Notifier:
    """Sends alerts with your own bot (real push notification) or to Saved Messages."""

    def __init__(self, client, my_id: int):
        self.client = client
        self.my_id = my_id
        self.bot_token = env("BOT_TOKEN")

    async def send(self, text: str) -> None:
        print("\n" + text + "\n", flush=True)
        print("\a", end="", flush=True)  # terminal beep
        if self.bot_token:
            try:
                await asyncio.to_thread(bot_send, self.bot_token, self.my_id, text)
                return
            except Exception as exc:
                print(f"[bot send failed: {exc}] (did you press Start on your bot?) "
                      "Falling back to Saved Messages.", flush=True)
        await self.client.send_message("me", text, link_preview=False)


# ---------------------------------------------------------------- Telegram listener

async def make_client():
    from telethon import TelegramClient

    api_id, api_hash = env("TG_API_ID"), env("TG_API_HASH")
    if not api_id or not api_hash:
        sys.exit("Missing TG_API_ID / TG_API_HASH. Copy .env.example to .env and fill them in.")
    client = TelegramClient(str(HERE / "seed_alert"), int(api_id), api_hash)
    await client.start()  # first run asks for your phone number + login code
    me = await client.get_me()
    return client, me


async def watch() -> None:
    from telethon import events

    channel = env("CHANNEL", "SecretSocietyOfNinjas").lstrip("@").replace("https://t.me/", "")
    alert_all = env("ALERT_ALL_POSTS", "0").lower() in ("1", "true", "yes")

    client, me = await make_client()
    notifier = Notifier(client, me.id)
    entity = await client.get_entity(channel)
    seen: set[str] = set()

    async def handle(event, kind: str):
        msg = event.message
        text = msg.message or ""
        link = f"https://t.me/{channel}/{msg.id}"
        phrases = [p for p in find_seed_phrases(text) if p not in seen]
        if not phrases:
            if alert_all and kind == "new":
                preview = text[:200] + ("…" if len(text) > 200 else "")
                media = " (has image/media: check it yourself, seeds in pictures can't be read)" if msg.media else ""
                await notifier.send(f"📢 New post in @{channel}{media}\n{link}\n\n{preview}")
            return
        for phrase in phrases:
            seen.add(phrase)
            await notifier.send(f"🎁 Seed phrase posted in @{channel}. Running safety check…\n{link}")
            address, results = await asyncio.to_thread(safety_check, phrase)
            await notifier.send(format_report(phrase, address, results, source=link))

    @client.on(events.NewMessage(chats=entity))
    async def on_new(event):
        await handle(event, "new")

    @client.on(events.MessageEdited(chats=entity))
    async def on_edit(event):
        await handle(event, "edit")

    title = getattr(entity, "title", channel)
    mode = "your bot" if env("BOT_TOKEN") else "Saved Messages (no push sound, see README)"
    print(f"Logged in as {me.first_name}. Watching '{title}' (@{channel}). Alerts go to {mode}.")
    print("Leave this window open. Ctrl+C to stop.", flush=True)
    await client.run_until_disconnected()


async def test_alert() -> None:
    client, me = await make_client()
    notifier = Notifier(client, me.id)
    await notifier.send("✅ seed-alert test: notifications are working.")
    await client.disconnect()


def manual_check() -> None:
    text = getpass("Paste the seed phrase (hidden), then press Enter: ")
    phrases = find_seed_phrases(text)
    if not phrases:
        sys.exit("No valid 12–24 word BIP39 seed phrase found (wrong word or failed checksum).")
    for phrase in phrases:
        print("Checking (read-only)…")
        address, results = safety_check(phrase)
        print("\n" + format_report(phrase, address, results))


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "watch"
    if cmd == "watch":
        try:
            asyncio.run(watch())
        except KeyboardInterrupt:
            print("\nStopped.")
    elif cmd == "check":
        manual_check()
    elif cmd == "test-alert":
        asyncio.run(test_alert())
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
