# REVIEW — A Day in Ada's Money (review cut 1 + edits, not yet re-rendered)

Edits after cut 1: opening clock now 09:02 → 09:03 (voice re-recorded "Nine oh three"); clock removed from the USDT scene (s03); hashtags removed from the CTA card.

**File:** `renders/video.mp4` · 1920×1080 · 30 fps · 78.2 s · voiceover only (no music / SFX, as asked)

## Creative calls
- Storyline #2 "A Day in Ada's Money", told by a rolling clock: 09:02 → 09:03 → 12:30 → 18:00 → 21:15 → Friday.
  Not built: One Coin's Journey, The Receipt, Departures, Close the Tabs.
- Look = Raenest's own flat brand plates (indigo #2E096F, violet #4D3DD3, coral #FF4F40, lime #E5FE00), Inter type.
- Product visuals are Raenest's own: the real "Add money" screen, the Cards screen, the virtual-card widget,
  the card-in-hand photo, the 3D coins and vault renders, and the official logo SVG — all from raenest.com.
  Other app screens (USDT details with Ethereum/Tron/Solana, Stablecoin wallet, Send money) are **rebuilt in
  HTML from Raenest's real screens and blog walkthroughs**, using their real labels. Names/amounts
  (Ada Okafor, 500 USDT, 120 USDC, the wallet addresses) are illustrative.
- Logo sting copies the beats of Raenest's own reel ending: white flash → lavender → indigo, the mark resolving
  from blur while it turns, wordmark rising, "Your global money partner", thin bar wiping in.
- Voice: Kokoro `af_heart` (free, on-device) at 1.1×; "Raenest" respelled "Ray-nest" so it is pronounced right.

## Facts checked against raenest.com (Sep & Nov 2026 blog posts)
- 7% is always "up to 7% variable APY" and only ever beside USDC/USDT; footnote "Eligible USDC & USDT balances · APY varies".
- SOL/BTC/ETH deposits are converted to USDC, "usually in 10–30 min" (not instant).
- Card spends directly from USDC/USDT balances, no converting first. Send networks: Ethereum, Binance, Solana, Polygon.

## Measured vs looked at
- `hyperframes check`: passes (0 errors). Snapshots of every scene's fullest frame and every cut were inspected.
- Audio was **measured, not heard** — nobody has listened to the voice yet.

## Warnings kept on purpose
- `text_below_floor`: small text inside the phone screens is context UI; every line the viewer must read is ≥ 28 px.
- `first_frame_empty`: false positive — frame 0 shows the large "09:01" clock (the clock is excluded from the
  layout audit because its rolling-digit window trips the occlusion check).
- `duplicate_media_discovery_risk`: the USDT/USDC icons are reused on purpose.

## Weakest shot / next changes
- s06 (21:15 card): three product pieces in 9 s feels busy; with more time I'd drop the virtual-card widget.
- Runtime is 78 s (longer than the ~60 s planned) because six required features each get a beat. Easiest cut:
  trim s02 or merge s07 into s08.
- Not yet: music bed + SFX, captions, 9:16 cut for TikTok/Instagram, a HeyGen voice (needs sign-in).

## Scene ids (for targeted edits)
s01 hook 0–5.0 · s02 what-is 5.0–12.8 · s03 receive USDT/Solana 12.8–26.9 · s04 SOL→USDC 26.9–36.7 ·
s05 Vault 36.7–47.8 · s06 cards 47.8–57.5 · s07 send 57.5–64.3 · s08 CTA 64.3–74.2 · s09 logo 74.2–78.2

## v2 restyle (after the "Pulse" reference reel) — not yet rendered
- Generator: `.work/gen2.py` (v1 kept as `.work/gen.py`). Same story, voice and timings.
- Text flow: one centred line that grows word by word and re-centres as it grows; typewriter caret
  ("No wire delays."); keywords in lime pills; two-line side captions with the second line in accent;
  chip chains joined by arrows ("Get paid → Save → Spend → Send", "BTC ETH SOL → USDC", "1 USDT ≈ $1.00").
- UI flow: large frameless app screens on a light ground, cropped by the frame; camera pans/pushes;
  a big cursor clicks (Solana tab, Copy, Crypto tab, Withdraw, Pay from, Stablecoin, Send);
  notification cards pop over a violet wash (USDT received, Add money successful, Interest earned, Paid, Sent).
- Colours stay Raenest's (indigo text beats, light UI beats, lime/violet accents) in place of the reel's black/white/green.
