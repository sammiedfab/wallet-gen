---
workflow: general-video
flow: automation
storyboard: yes
message: "The market puts a number on every Premier League match. Make your call on worm."
destination: x-feed
aspect: 1920x1080
language: en
audience: Superteam Earn judges and football fans on X
length: 41s
angle: proof-walkthrough
---

## Intent

An entry for the Superteam Earn bounty "Create Content on Premier League Predictions with worm".
Concept: "The Market Says…". Pundits argue, the market puts a number on it. The video has to show
that the creator really used worm. Real screen recordings are the core, with annotations, a clear
explanation that the % is the market's chance, and a call to action with the referral link.
Tone: sharp, punchy, sports-broadcast energy.

## Assets

- assets/predict-flow.mp4 (from the user's .mov, 66s): Spain vs England market, Yes on Spain at 49¢, $1 amount,
  Submit Buy, "Share your call" confetti card, the live position. The "My call" and "Proof" beats use it.
- assets/profile-ref.mp4 (from the user's .mp4 at 30–57.5s): @sammiedfab profile, Invite & Earn page with
  worm.wtf/r/sammiedfab, Positions list with Spain vs England. Source 0–30s left out (it shows a Google account picker and a browser menu with names and emails).
- assets/pl-arsenal.mp4 (the user's PL clip, 37s): Premier League tab, EPL: 2027 Champion, Arsenal 77%, Yes on Arsenal at 77¢, $1 → $1.33,
  Submit, the "To win $1" card, the live Arsenal position. The main proof footage.
- assets/brand/favicon.png: the worm 3D chrome W, from worm.wtf.
- assets/fonts: Instrument Sans (worm.wtf's own font), DejaVu Sans Mono (terminal), VT323 (CRT/pixel).
- assets/sfx/: click, key (typing), whoosh, whoosh-deep, pop, boom. CC0/bundled, matched to the SFX palette of the
  reference post x.com/nexoxh/status/2121974531807998070 (see assets/sfx/CREDITS.md).
- assets/audio/polygon-bed.mp3: the full audio track (music with its sound effects baked in) from x.com/0xpolygon/status/2114723012045906233,
  as the user asked. 41.1s, 125 BPM. Beat drop at 8.5s, tail fade from 38.5s. Third-party audio, kept out of git.
- assets/sfx/: CC0 kit, kept as a fallback if the Polygon audio can't be used.
- PENDING: the user's ElevenLabs voiceover, recorded from SCRIPT.md.

## Customizations

- Match worm's own X videos (posts 2118395670449000814 and 2120928453092323553): Instrument Sans lowercase with tight tracking,
  word-by-word builds, typed terminal hook with a blinking cursor, CRT/RGB fringe hits, tilted floating UI panels,
  monochrome black/gray with app green/red only, worm W × lockup, white "worm.wtf" end card.

- Phone-frame presentation of the recordings with zoom-ins and callouts on the key UI.
- Burned-in captions/headlines (X autoplays muted).
- CTA shows https://www.worm.wtf/r/sammiedfab and @wormwtf.
- Persistent @sammiedfab handle in the lower-right corner for the whole video (inverts on the white end card).

## Notes

- Wording: say "predict", "make your call", "chance". Never "bet", "odds", "wager", "stake", "gamble".
- Crop out "Bigger bets, bigger fees" on the referral page, and leave out the Bitcoin market.
- Never show source A before 30s (PII).
- Product facts: all 20 PL clubs, live %, leverage up to 3x, 30% referral fee share.
