# seed-alert

Watches a Telegram channel (default: **@SecretSocietyOfNinjas**) and alerts you when
a seed phrase is posted. Before alerting, it runs a **read-only safety check**
on the wallet so you can see whether it's a trap.

> ⚠️ "Free seed phrase" giveaways are almost always **gas-trap / sweeper scams**.
> The wallet shows tokens but has no gas. When you send ETH or BNB in to pay the fee,
> a bot takes it within seconds. **Never send any funds to a wallet whose seed phrase is public.**
> This tool only reads from the blockchain. It never signs or sends anything.

## What the check looks for (Ethereum, BNB Chain, Polygon, Base, Arbitrum)

| Result | Meaning |
|---|---|
| 🚨 DANGER | Wallet is delegated to a contract (EIP-7702 sweeper), has contract code, or is sending transactions right now |
| 🪤 GAS TRAP | Holds USDT/USDC but almost no gas coin |
| ⚠️ SUSPICIOUS | Many outgoing transactions and an empty balance: something keeps draining it |
| ∅ EMPTY | Nothing found on the checked chains (it may be on Tron/Solana, or hold other tokens) |

## Setup (one time)

You need Python 3.10+ on a computer (or an Android phone with Termux) that stays on.

```bash
cd seed-alert
python -m venv venv
# Windows: venv\Scripts\activate     macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env
```

Open `.env` in a text editor and fill in:

1. **TG_API_ID / TG_API_HASH**: free from https://my.telegram.org → *API development tools*.
2. **BOT_TOKEN** (recommended): message **@BotFather** → `/newbot` → copy the token.
   Then open your new bot and press **Start** once.
   Without a bot, alerts go to your *Saved Messages*, which **don't make a sound** on your phone.

Keep `.env` and the `seed_alert.session` file private. Together they give access to your Telegram account.

## Run

```bash
python seed_alert.py test-alert   # first run: asks for your phone number + login code, sends a test alert
python seed_alert.py              # start watching (leave the window open)
python seed_alert.py check        # check any seed phrase by hand (input is hidden)
```

## Notes

- Text posts are scanned, including numbered lists and edited posts. Seeds posted **as images** can't be
  read; with `ALERT_ALL_POSTS=1` you still get pinged for every new post.
- Only the standard address (`m/44'/60'/0'/0/0`, the one MetaMask and Trust Wallet use) is checked.
