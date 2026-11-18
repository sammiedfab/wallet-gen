# SPEC — "A Day in Ada's Money" (Raenest Global Bounty · Track C)

GOAL:    A viewer who has never heard of Raenest understands that one app lets a freelancer receive USDT/USDC
         (on Solana), fund with SOL/BTC/ETH, earn up to 7% variable APY on USDC/USDT in Vault, spend by card,
         and send out — then signs up with referral code **sammiedfab**.
OUTPUT:  HyperFrames, 1920 x 1080, 30 fps, MP4. Voiceover only (no music, no SFX — per request).
TIME:    ~78.2 s x 30 = ~2346 frames. Narrated: the voice is the clock (Kokoro af_heart, 1.1x).

LOOK:    Raenest's own brand fields, flat (no mesh gradients, no glow), one world per time of day:
           indigo #2E096F (night / logo), violet #4D3DD3 (brand / coins plate), coral #FF4F40 (Raenest's own
           blog plate, lunch), lime #E5FE00 (accent: ONE word per shot, and the CTA flood), white #FFFFFF ink,
           app ink #1B1B1F on app white, app primary #4F3BD7.
         Type: Inter. Display 900, 112-150 px (10-14% of height), tracking -0.035em. Body 600, 40-48 px.
           Clock digits Inter 900, 300 px, tabular. Nothing read on screen below 28 px except phone context UI.
         Medium: real Raenest product UI and Raenest's own 3D renders (vault, coins, card-in-hand) on flat
           colour plates. Phone = black bezel 18 px, radius 72 px, shadow 0 40px 80px rgba(0,0,0,.35).
OBJECTS: the clock (rolling digits, the day's spine) · a chat bubble from the New York client · the phone
         (Raenest app screens: Accounts/Stablecoin, USDT details with Ethereum/Tron/Solana, Add money,
         USDT Vault, Cards, Send money) · USDT/USD coins (Raenest render) · the vault (Raenest render) ·
         the physical Visa card in a hand (Raenest photo) · the Raenest mark + wordmark (official SVG).
MOTION:  enter expo.out 0.6-0.8 s · move power3.inOut 0.6 s · exit power3.in 0.3 s · colour flood
         power2.inOut 0.4 s · titles per-word blur 6px->0, 0.13 s, 0.08 s stagger, no translate.
         Clock: digit strips roll (power3.inOut 0.5 s). Exits 40-50% of entries. Landed titles hold still.

SHOTS (absolute s; V = voice start):
  s01 0.00-5.04   indigo. "09:02" rolls to "09:03" (hero, 300 px) · LAGOS label · NYC client bubble
                  "Invoice paid — 500 USDT sent" lands on "paid". Clock shrinks to top-left chapter mark.
  s02 5.04-12.75  violet. "No wire delays." "No juggling five apps." 5 grey app tiles collapse into the
                  Raenest phone (real render) on "Raenest"; currency chips USD GBP EUR NGN USDT USDC.
  s03 12.75-26.88 violet coins plate. (no clock) Phone: USDT details, network tabs Ethereum/Tron/Solana ->
                  Solana; address pill pulled out at 2x + "Copied"; balance 0.00 -> 500.00 USDT;
                  "fast · low cost"; coins render + "1 USDT ≈ 1 USD" on "one to one".
  s04 26.88-36.70 coral. 12:30. Real "Add money" screen (Crypto tab), rows extend with BTC ETH SOL;
                  SOL -> USDC conversion card; BTC / ETH chips light on their words.
  s05 36.70-47.80 indigo. 18:00. Vault render; "up to 7%" counts; "variable APY"; USDC + USDT chips;
                  "Paid daily" / "Withdraw anytime"; footnote "eligible USDC & USDT only".
  s06 47.80-57.52 indigo night. 21:15. Raenest Cards screen (real) -> hand with physical card (real)
                  taps -> "Paid" tick; virtual card; "Pay from: USDT" balance picker; "No converting".
  s07 57.52-64.27 violet. FRIDAY. Send money: receiver type -> Stablecoin; networks Ethereum Binance
                  Solana Polygon; "Sent 120 USDC" success.
  s08 64.27-74.20 lime flood. "Get paid. Save. Spend. Send." -> "All in one app." -> CTA card with
                  referral link + code sammiedfab (no hashtags), held >= 3 s.
  s09 74.20-78.20 logo sting copied from Raenest's own reel: white flash -> lavender -> indigo in 0.3 s,
                  mark resolves from blur with a continuous 3D turn, wordmark rises, "Your global money
                  partner", thin bar wipes in.

FACT GUARDRAILS (from raenest.com blog, Sep/Nov 2026):
  - 7% is always "up to 7% variable APY", always beside USDC/USDT, never beside SOL/BTC/ETH.
  - SOL/BTC/ETH deposits are converted to USDC (usually 10-30 min) — never "instant".
  - Send networks: Ethereum, Binance, Solana, Polygon. Card spends from USDC/USDT, Visa, no converting first.

BANNED:  glow/bloom/particles · mesh or purple gradients (flat brand plates only) · glass cards · everything
         centred · every element fade+slide-up · titles drifting after landing · logo docked in a corner ·
         three cards in a row · invented dashboards (all UI is rebuilt from Raenest's own screens) ·
         tilted product UI.
QA:      first frame not empty · every line ≥ its read time · 7% never next to SOL/BTC/ETH · CTA readable
         at 360 px · logo sting matches reference beats (flash, ring turn, wordmark, tagline, bar).
