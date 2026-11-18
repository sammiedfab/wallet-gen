#!/usr/bin/env python3
"""Generates the scene compositions + index.html for the Raenest 'Day in Ada's Money' film."""
import json, os, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMP = os.path.join(ROOT, "compositions")
os.makedirs(COMP, exist_ok=True)

INDIGO, VIOLET, CORAL, LIME, NIGHT = "#2E096F", "#4D3DD3", "#FF4F40", "#E5FE00", "#1A0645"

# scene id, start, duration, voice offset inside scene (None = no voice)
SCENES = [
    ("s01", 0.00, 5.04, 0.70),
    ("s02", 5.04, 7.71, 0.30),
    ("s03", 12.75, 14.13, 0.30),
    ("s04", 26.88, 9.82, 0.30),
    ("s05", 36.70, 11.10, 0.30),
    ("s06", 47.80, 9.72, 0.30),
    ("s07", 57.52, 6.75, 0.30),
    ("s08", 64.27, 9.93, 0.30),
    ("s09", 74.20, 4.00, None),
]
VOICE = {"s01": "s01-hook", "s02": "s02-what", "s03": "s03-receive", "s04": "s04-crypto",
         "s05": "s05-vault", "s06": "s06-card", "s07": "s07-send", "s08": "s08-cta"}
TOTAL = round(SCENES[-1][1] + SCENES[-1][2], 2)

COMMON_CSS = """
#root{position:absolute;inset:0;overflow:hidden}
.st{position:absolute;inset:0;overflow:hidden}
.bg{position:absolute;inset:0}
.disp{position:absolute;font-family:Inter,sans-serif;font-weight:900;letter-spacing:-0.035em;line-height:1.02;color:#fff;margin:0;white-space:nowrap}
.bd{position:absolute;font-family:Inter,sans-serif;font-weight:700;color:#fff;white-space:nowrap}
.wd{display:inline-block;white-space:pre}
.lime{color:#E5FE00}
.phone{position:absolute;width:460px;height:940px;border-radius:74px;background:#101014;padding:16px;box-shadow:0 40px 90px rgba(10,0,40,.38)}
.scr{position:relative;width:100%;height:100%;border-radius:58px;background:#fff;overflow:hidden;font-family:Inter,sans-serif;color:#1b1b1f}
.phone.sm{width:410px;height:840px;border-radius:66px;padding:14px}
.phone.sm .scr{border-radius:52px}
.isl{position:absolute;left:50%;top:14px;width:124px;height:36px;margin-left:-62px;border-radius:20px;background:#101014;z-index:9}
.sbar{position:absolute;left:38px;right:38px;top:20px;display:flex;justify-content:space-between;font:700 17px Inter,sans-serif;color:#1b1b1f}
.lay{position:absolute;inset:0;padding:84px 26px 0 26px}
.ap-h{font:700 30px Inter,sans-serif;margin:18px 0 4px}
.ap-s{font:400 17px Inter,sans-serif;color:#6b6b76}
.ap-tabs{display:flex;background:#f3f2f7;border-radius:14px;padding:5px;margin:18px 0;position:relative}
.ap-tabs div{flex:1;text-align:center;font:700 16px Inter,sans-serif;color:#6b6b76;padding:11px 0;position:relative;z-index:2}
.ap-tabs .ind{position:absolute;top:5px;bottom:5px;border-radius:10px;background:#fff;box-shadow:0 2px 8px rgba(0,0,0,.08);z-index:1}
.ap-row{display:flex;align-items:center;gap:14px;padding:16px 6px;border-bottom:1px solid #eeedf3;font:700 19px Inter,sans-serif}
.ap-btn{background:#4F3BD7;color:#fff;border-radius:14px;text-align:center;font:700 18px Inter,sans-serif;padding:16px 0}
.ap-ic{width:40px;height:40px;border-radius:50%;flex:none;display:flex;align-items:center;justify-content:center;font:900 16px Inter,sans-serif;color:#fff}
.callout{position:absolute;background:#fff;border-radius:30px;padding:30px 36px;box-shadow:0 30px 70px rgba(10,0,40,.30);font-family:Inter,sans-serif;color:#1b1b1f}
.tag{display:inline-flex;align-items:center;gap:14px;padding:14px 24px;border-radius:18px;font:700 34px Inter,sans-serif;background:#fff;color:#2E096F;margin-right:14px}
.tag img{width:40px;height:40px}
.clock{position:absolute;font-family:Inter,sans-serif;font-weight:900;color:#fff;letter-spacing:-0.04em;display:flex;line-height:1;transform-origin:0 0}
.clock .dg{display:inline-block;height:1em;overflow:hidden}
.clock .strip{display:flex;flex-direction:column;align-items:flex-start}
.clock .strip span{display:block;height:1em;line-height:1}
.clock .col{display:inline-block;height:1em;line-height:.92}
"""

# --- helpers ---------------------------------------------------------------

def words(text, cls="", start_ids=None):
    out = []
    for w in text.split(" "):
        lime = w.startswith("*")
        w = w.lstrip("*")
        out.append(f'<span class="wd{" lime" if lime else ""}">{w} </span>')
    return "".join(out).rstrip()


def clock(cid, old, new, px, left, top, extra=""):
    return (f'<div id="{cid}" class="clock" data-layout-allow-overflow data-layout-ignore style="font-size:{px}px;left:{left}px;top:{top}px;{extra}">'
            f'<span class="dg"><span class="strip chg"><span>{old}</span><span>{new}</span></span></span></div>')


def qr(seed, n=21, size=230):
    h = hashlib.sha256(seed.encode()).digest()
    bits = []
    k = 0
    while len(bits) < n * n:
        h = hashlib.sha256(h).digest()
        for byte in h:
            for j in range(8):
                bits.append((byte >> j) & 1)
    cells = []
    cs = size / n
    def finder(x, y):
        return (x < 7 and y < 7) or (x >= n - 7 and y < 7) or (x < 7 and y >= n - 7)
    for y in range(n):
        for x in range(n):
            on = bits[y * n + x]
            if finder(x, y):
                fx, fy = (x if x < 7 else x - (n - 7)), (y if y < 7 else y - (n - 7))
                on = 1 if (fx in (0, 6) or fy in (0, 6) or (2 <= fx <= 4 and 2 <= fy <= 4)) else 0
            if on:
                cells.append(f'<rect x="{x*cs:.2f}" y="{y*cs:.2f}" width="{cs+0.3:.2f}" height="{cs+0.3:.2f}"/>')
    return f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" fill="#1b1b1f">{"".join(cells)}</svg>'


def phone(pid, left, top, inner, extra="", cls=""):
    return (f'<div id="{pid}" class="phone{cls}" style="left:{left}px;top:{top}px;{extra}"><div class="scr">'
            f'<div class="isl"></div><div class="sbar"><span>9:41</span><span>5G ▮</span></div>{inner}</div></div>')


JS_HELPERS = """
const $ = (s) => document.querySelector(s);
const $$ = (s) => Array.from(document.querySelectorAll(s));
function inn(tl, el, from, to, t){ tl.fromTo(el, from, Object.assign({ease:'expo.out',duration:.7}, to), t); }
function out(tl, el, from, to, t){ tl.fromTo(el, from, Object.assign({ease:'power3.in',duration:.3, immediateRender:false}, to), t); }
function wordsIn(tl, sel, times){ $$(sel+' .wd').forEach((w,i)=>{ const t = Array.isArray(times) ? times[Math.min(i,times.length-1)] + (i>=times.length ? (i-times.length+1)*.08 : 0) : times + i*.08;
  tl.fromTo(w,{opacity:0,filter:'blur(6px)'},{opacity:1,filter:'blur(0px)',duration:.16,ease:'power2.out'},t); }); }
function blurOut(tl, sel, t){ tl.fromTo(sel,{opacity:1,filter:'blur(0px)'},{opacity:0,filter:'blur(8px)',duration:.22,ease:'power2.in',immediateRender:false},t); }
function roll(tl, cid, t){ tl.fromTo('#'+cid+' .strip.chg',{yPercent:0},{yPercent:-50,duration:.55,ease:'power3.inOut',stagger:.05},t);
  tl.fromTo('#'+cid+' .strip.chg span:first-child',{opacity:1},{opacity:0,duration:.4,ease:'power2.in',stagger:.05},t+.05);
  tl.fromTo('#'+cid+' .strip.chg span:last-child',{opacity:0},{opacity:1,duration:.4,ease:'power2.out',stagger:.05},t+.1); }
function count(tl, el, from, to, dec, t, d, suffix){ const o={v:from}; const e=$(el); e.textContent=from.toFixed(dec)+(suffix||'');
  tl.fromTo(o,{v:from},{v:to,duration:d,ease:'power2.out',onUpdate:()=>{e.textContent=o.v.toFixed(dec)+(suffix||'');}},t); }
"""


def scene(sid, dur, css, body, js):
    return f"""<template>
<style>
{COMMON_CSS}
{css}
</style>
<div id="root" data-composition-id="{sid}" data-width="1920" data-height="1080">
<div id="{sid}-st" class="st clip" data-start="0" data-duration="{dur}" data-layout-allow-overflow>
{body}
</div>
</div>
<script>
(() => {{
{JS_HELPERS}
const tl = gsap.timeline({{ paused: true }});
{js}
window.__timelines["{sid}"] = tl;
}})();
</script>
</template>
"""

# ---------------------------------------------------------------------------
S = {}

# s01 — HOOK: 09:02 Lagos, client in New York pays
S["s01"] = ("""
#s01-bg{background:%s}
#s01-bubble{left:1060px;top:360px;width:660px;border-radius:34px 34px 34px 8px}
#s01-bubble .who{font:700 28px Inter,sans-serif;color:#6b6b76;margin-bottom:12px}
#s01-bubble .msg{font:900 50px Inter,sans-serif;letter-spacing:-.02em;line-height:1.12}
#s01-route{left:1060px;top:640px;font-size:40px;color:rgba(255,255,255,.85)}
""" % INDIGO, f"""
<div id="s01-bg" class="bg"></div>
{clock('s01-clock','09:01','09:02',300,530,330)}
<div id="s01-city" class="bd" style="left:540px;top:660px;font-size:52px;color:rgba(255,255,255,.8)">{words('Lagos, Nigeria')}</div>
<div id="s01-bubble" class="callout"><div class="who">Mike · Studio Nine, New York</div><div class="msg">Invoice paid. Sent you <span style="color:#4F3BD7">500 USDT</span>.</div></div>
<div id="s01-route" class="bd">New York <span class="lime">→</span> Lagos</div>
""", """

roll(tl,'s01-clock',.5);
wordsIn(tl,'#s01-city',[1.12,1.3]);
tl.fromTo(['#s01-clock'],{x:0,y:0,scale:1},{x:-338,y:-30,scale:.86,duration:.65,ease:'power3.inOut'},2.35);
tl.fromTo('#s01-city',{x:0,y:0},{x:-348,y:-70,duration:.65,ease:'power3.inOut'},2.35);
inn(tl,'#s01-bubble',{opacity:0,x:140,filter:'blur(10px)'},{opacity:1,x:0,filter:'blur(0px)',duration:.75},2.55);
inn(tl,'#s01-route',{opacity:0,filter:'blur(6px)'},{opacity:1,filter:'blur(0px)',duration:.4},3.95);
""")

# s02 — WHAT: no wire delays, no juggling apps -> one place
tiles = [("Bank", 1110, 470), ("Exchange", 1300, 400), ("P2P chat", 1490, 480), ("Card app", 1200, 660), ("Savings", 1420, 680)]
tiles_html = "".join(
    f'<div class="s02-tile" style="left:{x}px;top:{y}px"><div class="s02-tile-in">{n}</div></div>' for n, x, y in tiles)
acc_screen = f"""
<div class="lay">
  <div style="display:flex;justify-content:space-between;align-items:center"><div class="ap-h">Accounts</div><div class="ap-btn" style="padding:10px 18px;font-size:15px">Create new</div></div>
  <div style="display:flex;gap:10px;margin-top:16px">
    <div style="background:#efedfb;border:2px solid #cfc9f5;border-radius:14px;padding:10px 14px;font:700 15px Inter">USD<br><span style="font-weight:400">2,800.00</span></div>
    <div style="border:1px solid #e6e5ec;border-radius:14px;padding:10px 14px;font:700 15px Inter">GBP<br><span style="font-weight:400">0.00</span></div>
    <div style="border:1px solid #e6e5ec;border-radius:14px;padding:10px 14px;font:700 15px Inter">NGN<br><span style="font-weight:400">2,800</span></div>
  </div>
  <div style="font:700 40px Inter;margin:26px 0 18px">$2,800.00</div>
  <div style="display:flex;justify-content:space-around;background:#f7f6fb;border-radius:16px;padding:18px 0;font:400 15px Inter;text-align:center">
    <div><div style="font-size:22px;color:#4F3BD7">⇄</div>Convert</div><div><div style="font-size:22px;color:#4F3BD7">➤</div>Send Money</div><div><div style="font-size:22px;color:#4F3BD7">···</div>More</div></div>
  <div style="display:flex;justify-content:space-between;margin:26px 0 12px;font:700 16px Inter"><span>Account details</span><span style="color:#4F3BD7">Share</span></div>
  <div style="background:#f7f6fb;border-radius:16px;padding:14px">
    <div style="display:flex;background:#fff;border-radius:12px;padding:4px;margin-bottom:10px;font:700 14px Inter;text-align:center"><div style="flex:1;background:#efedfb;color:#4F3BD7;border-radius:9px;padding:9px">Domestic</div><div style="flex:1;padding:9px;color:#6b6b76">International</div></div>
    <div style="background:#fff;border-radius:12px;padding:12px;font:700 16px Inter;margin-bottom:8px">Ada Okafor<br><span style="font-weight:400;color:#6b6b76;font-size:14px">US Dollar</span></div>
    <div style="background:#fff;border-radius:12px;padding:12px;font:400 14px Inter;color:#6b6b76">Account number<br><span style="font:700 16px Inter;color:#1b1b1f">•••• •••• 4821</span></div>
  </div>
</div>"""
S["s02"] = ("""
#s02-bg{background:%s}
#s02-flood{background:%s;clip-path:circle(0px at 1380px 520px)}
.s02-tile{position:absolute;width:170px;height:170px}
.s02-tile-in{width:100%%;height:100%%;border-radius:40px;background:rgba(255,255,255,.16);border:2px solid rgba(255,255,255,.35);display:flex;align-items:flex-end;justify-content:center;padding-bottom:22px;font:700 26px Inter,sans-serif;color:#fff}
#s02-tags{position:absolute;left:192px;top:560px;white-space:nowrap}
""" % (INDIGO, VIOLET), f"""
<div id="s02-bg" class="bg"></div>
<div id="s02-flood" class="bg"></div>
<h1 id="s02-l1" class="disp" style="left:192px;top:200px;font-size:112px">{words('No wire delays.')}</h1>
<h1 id="s02-l2" class="disp" style="left:192px;top:330px;font-size:112px">{words('No juggling five apps.')}</h1>
{tiles_html}
{phone('s02-phone',1230,70,acc_screen)}
<h1 id="s02-l3" class="disp" style="left:192px;top:250px;font-size:120px">{words('*One place')}<br>{words('for her money.')}</h1>
<div id="s02-tags">{''.join(f'<span class="tag">{c}</span>' for c in ['USD','GBP','EUR','NGN','USDT','USDC'])}</div>
<div id="s02-l4" class="bd" style="left:192px;top:700px;font-size:52px">{words('Across currencies. Across borders.')}</div>
""", """
tl.fromTo('#s02-flood',{clipPath:'circle(0px at 1380px 520px)'},{clipPath:'circle(2300px at 1380px 520px)',duration:.55,ease:'power2.inOut'},0);
wordsIn(tl,'#s02-l1',[.3,.5,.88]);
wordsIn(tl,'#s02-l2',[1.57,1.76,2.54,2.93]);
$$('.s02-tile').forEach((t,i)=>{ tl.fromTo(t,{opacity:0,scale:.6},{opacity:1,scale:1,duration:.5,ease:'back.out(1.6)'},1.8+i*.12); });
blurOut(tl,['#s02-l1','#s02-l2'],3.3);
$$('.s02-tile').forEach((t,i)=>{
  tl.fromTo(t,{x:0,y:0,scale:1,opacity:1},{x:1460-(parseFloat(t.style.left)+85),y:540-(parseFloat(t.style.top)+85),scale:.15,opacity:0,duration:.42,ease:'power3.in',immediateRender:false},3.28+i*.03); });
inn(tl,'#s02-phone',{opacity:0,y:240,scale:.92},{opacity:1,y:0,scale:1,duration:.85},3.55);
wordsIn(tl,'#s02-l3',[4.0,4.18,4.6,4.78,4.94]);
$$('#s02-tags .tag').forEach((t,i)=>{ inn(tl,t,{opacity:0,y:30,filter:'blur(6px)'},{opacity:1,y:0,filter:'blur(0px)',duration:.45},5.55+i*.07); });
wordsIn(tl,'#s02-l4',[5.3,5.6,6.75,6.93]);
""")

# s03 — RECEIVE USDT on Solana, 1:1 with USD
addr = "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
usdt_details = f"""
<div class="lay" id="s03-scrA">
  <div style="font-size:22px">←</div>
  <div class="ap-h">USDT details</div>
  <div class="ap-s">Choose the network your sender is using</div>
  <div class="ap-tabs" id="s03-tabs"><div class="ind" id="s03-ind" style="left:5px;width:calc((100% - 10px)/3)"></div><div>Ethereum</div><div>Tron</div><div id="s03-sol">Solana</div></div>
  <div style="display:flex;justify-content:center;margin:16px 0 18px"><div style="padding:14px;border:1px solid #eeedf3;border-radius:18px">{qr('usdt-solana-ada')}</div></div>
  <div style="font:400 15px Inter;color:#6b6b76">USDT address</div>
  <div style="font:700 16px Inter;word-break:break-all;margin:6px 0 16px">{addr}</div>
  <div style="display:flex;gap:10px"><div class="ap-btn" style="flex:1">Copy</div><div class="ap-btn" style="flex:1;background:#efedfb;color:#4F3BD7">Share</div></div>
  <div style="margin-top:16px;background:#f7f6fb;border-radius:12px;padding:12px;font:400 14px Inter;color:#6b6b76">Transfers may take up to 1 to 20 minutes.</div>
</div>"""
usdt_wallet = f"""
<div class="lay" id="s03-scrB" style="background:#fff">
  <div class="ap-h">Accounts</div>
  <div class="ap-tabs"><div class="ind" style="left:calc(50% + 0px);width:calc(50% - 5px)"></div><div>Global</div><div style="color:#4F3BD7">Stablecoin</div></div>
  <div style="text-align:center;margin-top:28px"><img src="assets/brand/usdt.png" style="width:64px;height:64px"><div style="font:700 18px Inter;color:#6b6b76;margin-top:10px">USDT balance</div>
  <div style="font:900 52px Inter;letter-spacing:-.02em;margin-top:6px"><span id="s03-bal">0.00</span></div>
  <div style="display:inline-block;margin-top:10px;background:#f3f2f7;border-radius:10px;padding:8px 12px;font:400 14px Inter;color:#6b6b76">7xKX…gAsU</div></div>
  <div style="display:flex;justify-content:center;gap:22px;margin:26px 0;font:400 14px Inter;text-align:center">{''.join(f'<div><div style="width:54px;height:54px;border-radius:16px;background:{"#4F3BD7" if i==0 else "#efedfb"};color:{"#fff" if i==0 else "#4F3BD7"};display:flex;align-items:center;justify-content:center;font:700 22px Inter;margin:0 auto 6px">{g}</div>{n}</div>' for i,(g,n) in enumerate([("+","Add"),("➤","Send"),("⇄","Convert"),("···","More")]))}</div>
  <div style="font:700 17px Inter;margin-bottom:6px">Recent transactions</div>
  <div class="ap-row" id="s03-txn" style="font-size:16px"><div class="ap-ic" style="background:#e9f8f1;color:#13a36b">↓</div><div style="flex:1">Received USDT<br><span style="font:400 14px Inter;color:#6b6b76">Solana network · 09:03</span></div><div style="color:#13a36b">+500.00</div></div>
</div>"""
S["s03"] = ("""
#s03-bg{background:%s}
#s03-addr{left:830px;top:330px;width:900px}
#s03-addr .k{font:700 28px Inter,sans-serif;color:#6b6b76}
#s03-addr .v{font:700 38px 'JetBrains Mono',monospace;margin-top:12px;word-break:break-all;line-height:1.25}
#s03-copied{position:absolute;left:830px;top:560px;font-size:34px;background:#E5FE00;color:#2E096F}
#s03-in{left:830px;top:330px;width:900px}
#s03-in .k{font:700 30px Inter,sans-serif;color:#6b6b76}
#s03-in .v{font:900 96px Inter,sans-serif;letter-spacing:-.03em;color:#13a36b;margin-top:6px}
""" % VIOLET, f"""
<div id="s03-bg" class="bg"></div>
<img id="s03-coins" src="assets/brand/coins_on_violet.png" style="position:absolute;left:830px;top:40px;width:960px;height:718px">
{clock('s03-clock','09:02','09:03',96,192,110)}
{phone('s03-phone',220,236,usdt_details+usdt_wallet,cls=' sm')}
<h1 id="s03-h" class="disp" style="left:830px;top:170px;font-size:110px">{words('Fast.')} {words('*Low cost.')}</h1>
<div id="s03-addr" class="callout"><div class="k">Her USDT address · Solana</div><div class="v">{addr}</div></div>
<span id="s03-copied" class="tag">Copied</span>
<div id="s03-in" class="callout"><div class="k">Sent on Solana · from New York</div><div class="v">+500.00 USDT</div></div>
<div id="s03-stab" class="bd" style="left:830px;top:770px;font-size:46px">{words('A stablecoin holds its value:')}</div>
<h1 id="s03-eq" class="disp" style="left:830px;top:840px;font-size:110px">{words('1 USDT')} {words('*≈ $1.00')}</h1>
""", """

roll(tl,'s03-clock',.25);
inn(tl,'#s03-phone',{opacity:0,y:260},{opacity:1,y:0,duration:.85},.45);
tl.fromTo('#s03-ind',{x:0},{x:238,duration:.55,ease:'power3.inOut'},1.35);
tl.fromTo('#s03-sol',{color:'#6b6b76'},{color:'#4F3BD7',duration:.2},1.75);
inn(tl,'#s03-addr',{opacity:0,x:-120,scale:.9,filter:'blur(10px)'},{opacity:1,x:0,scale:1,filter:'blur(0px)',duration:.7},2.55);
tl.fromTo('#s03-copied',{opacity:0,scale:.7},{opacity:1,scale:1,duration:.4,ease:'back.out(1.8)'},3.35);
blurOut(tl,['#s03-addr','#s03-copied'],4.25);
inn(tl,'#s03-in',{opacity:0,y:40,filter:'blur(10px)'},{opacity:1,y:0,filter:'blur(0px)',duration:.6},4.5);
tl.fromTo('#s03-scrB',{opacity:0},{opacity:1,duration:.3,ease:'power2.inOut'},4.6);
tl.fromTo('#s03-scrA',{opacity:1},{opacity:0,duration:.2,immediateRender:false},4.9);
count(tl,'#s03-bal',0,500,2,5.0,1.3);
inn(tl,'#s03-txn',{opacity:0,y:20},{opacity:1,y:0,duration:.5},5.9);
wordsIn(tl,'#s03-h',[6.35,6.95,7.15]);
blurOut(tl,['#s03-h','#s03-in'],7.95);
inn(tl,'#s03-coins',{opacity:0,x:220,filter:'blur(16px)'},{opacity:1,x:0,filter:'blur(0px)',duration:1.0},8.1);
wordsIn(tl,'#s03-stab',[9.3,9.5,9.7,10.7,11.1]);
wordsIn(tl,'#s03-eq',[12.05,12.25,13.4,13.55]);
""")

# s04 — LUNCH: SOL deposit converted to USDC; BTC & ETH same
def crow(sym, color, label, rid):
    return (f'<div class="s04-r" id="{rid}"><div class="ap-ic" style="width:56px;height:56px;font-size:16px;background:{color}">{sym}</div>'
            f'<div style="flex:1">{label}</div></div>')
S["s04"] = ("""
#s04-bg{background:%s}
#s04-wipe{background:%s;clip-path:inset(100%% 0 0 0)}
#s04-list{left:192px;top:300px;width:760px;padding:26px 34px}
#s04-list .t{display:flex;gap:40px;font:700 30px Inter,sans-serif;color:#6b6b76;border-bottom:2px solid #eeedf3;padding-bottom:14px;margin-bottom:6px}
.s04-r{display:flex;align-items:center;gap:22px;padding:14px 12px;font:700 36px Inter,sans-serif;border-radius:16px}
#s04-ok{left:192px;top:300px;width:760px;padding:34px 40px}
#s04-also{position:absolute;left:192px;top:850px;white-space:nowrap}
""" % (VIOLET, CORAL), f"""
<div id="s04-bg" class="bg"></div>
<div id="s04-wipe" class="bg"></div>
<img id="s04-phone" src="assets/ui/addmoney.png" style="position:absolute;left:1090px;top:125px;width:650px;height:960px">
{clock('s04-clock','09:03','12:30',260,192,380)}
<div id="s04-list" class="callout"><div class="t"><span>Global</span><span style="color:#4F3BD7;border-bottom:4px solid #4F3BD7;padding-bottom:10px;margin-bottom:-16px">Crypto</span></div>
{crow('<img src="assets/brand/usdc.png" style="width:56px;height:56px">','#fff','USDC','s04-r1')}
{crow('<img src="assets/brand/usdt.png" style="width:56px;height:56px">','#fff','USDT','s04-r2')}
{crow('<span style="font-size:20px">BTC</span>','#8a8794','Bitcoin (BTC)','s04-btc')}
{crow('<span style="font-size:20px">ETH</span>','#8a8794','Ethereum (ETH)','s04-eth')}
{crow('<span style="font-size:20px">SOL</span>','#4F3BD7','Solana (SOL)','s04-sol')}
</div>
<div id="s04-ok" class="callout">
  <div style="display:flex;align-items:center;gap:20px"><div style="width:72px;height:72px;border-radius:50%;background:#13a36b;color:#fff;display:flex;align-items:center;justify-content:center;font:900 40px Inter">✓</div><div style="font:900 44px Inter;letter-spacing:-.02em">Add money successful</div></div>
  <div style="display:flex;align-items:center;gap:22px;margin-top:30px;font:900 64px Inter;letter-spacing:-.03em"><span>SOL</span><span id="s04-arr" style="color:#FF4F40">→</span><span id="s04-usdc" style="display:flex;align-items:center;gap:22px"><img src="assets/brand/usdc.png" style="width:64px;height:64px"><span>USDC</span></span></div>
  <div id="s04-cred" style="font:700 30px Inter;color:#6b6b76;margin-top:18px">In her USDC wallet, usually in 10–30 min</div>
</div>
<div id="s04-also"><span class="tag" id="s04-t1">BTC</span><span class="tag" id="s04-t2">ETH</span><span class="bd" id="s04-tw" style="position:relative;font-size:44px">{words('work the same way.')}</span></div>
""", """
tl.fromTo('#s04-wipe',{clipPath:'inset(100% 0 0 0)'},{clipPath:'inset(0% 0 0 0)',duration:.5,ease:'power2.inOut'},0);

roll(tl,'s04-clock',.35);
tl.fromTo('#s04-clock',{x:0,y:0,scale:1},{x:0,y:-270,scale:.37,duration:.6,ease:'power3.inOut'},1.05);
inn(tl,'#s04-phone',{opacity:0,y:320},{opacity:1,y:0,duration:.85},.9);
inn(tl,'#s04-list',{opacity:0,y:60,filter:'blur(10px)'},{opacity:1,y:0,filter:'blur(0px)',duration:.6},1.3);
tl.fromTo('#s04-sol',{backgroundColor:'rgba(79,59,215,0)',boxShadow:'0 0 0 0px rgba(79,59,215,0)'},{backgroundColor:'rgba(79,59,215,.10)',boxShadow:'0 0 0 4px rgba(79,59,215,1)',duration:.3,ease:'power2.out'},1.95);
blurOut(tl,'#s04-list',3.35);
inn(tl,'#s04-ok',{opacity:0,scale:.92,filter:'blur(10px)'},{opacity:1,scale:1,filter:'blur(0px)',duration:.6},3.45);
inn(tl,'#s04-arr',{opacity:0,x:-30},{opacity:1,x:0,duration:.4},4.15);
inn(tl,'#s04-usdc',{opacity:0,x:-40,filter:'blur(8px)'},{opacity:1,x:0,filter:'blur(0px)',duration:.5},5.3);
inn(tl,'#s04-cred',{opacity:0,filter:'blur(6px)'},{opacity:1,filter:'blur(0px)',duration:.4},6.5);
inn(tl,'#s04-t1',{opacity:0,y:30},{opacity:1,y:0,duration:.45},7.45);
inn(tl,'#s04-t2',{opacity:0,y:30},{opacity:1,y:0,duration:.45},8.15);
wordsIn(tl,'#s04-tw',[8.6,8.95,9.15,9.3]);
""")

# s05 — EVENING: Stablecoin Vault up to 7% variable APY on USDC & USDT
S["s05"] = ("""
#s05-bg{background:%s}
#s05-vault{position:absolute;left:130px;top:220px;width:860px;height:748px;-webkit-mask-image:linear-gradient(#000 82%%,transparent);mask-image:linear-gradient(#000 82%%,transparent)}
#s05-pct{left:1020px;top:300px;font-size:300px;line-height:1;color:#E5FE00}
#s05-tags{position:absolute;left:1030px;top:720px;white-space:nowrap}
""" % INDIGO, f"""
<div id="s05-bg" class="bg"></div>
<img id="s05-vault" src="assets/brand/vault.png">
{clock('s05-clock','12:30','18:00',260,192,380)}
<div id="s05-name" class="bd" style="left:1030px;top:200px;font-size:48px">{words('Stablecoin Vault')}</div>
<div id="s05-upto" class="bd" style="left:1030px;top:268px;font-size:56px;color:rgba(255,255,255,.85)">up to</div>
<h1 id="s05-pct" class="disp"><span id="s05-num">0</span>%</h1>
<div id="s05-apy" class="bd" style="left:1030px;top:620px;font-size:62px">{words('variable APY')}</div>
<div id="s05-tags"><span class="tag" id="s05-t1"><img src="assets/brand/usdc.png">USDC</span><span class="tag" id="s05-t2"><img src="assets/brand/usdt.png">USDT</span></div>
<div id="s05-daily" class="bd" style="left:1030px;top:835px;font-size:48px">{words('Paid daily. Withdraw anytime.')}</div>
<div id="s05-fn" class="bd" style="left:1030px;top:925px;font-size:28px;font-weight:400;color:rgba(255,255,255,.72)">Eligible USDC &amp; USDT balances · APY varies</div>
""", """

roll(tl,'s05-clock',.35);
tl.fromTo('#s05-clock',{x:0,y:0,scale:1},{x:0,y:-270,scale:.37,duration:.6,ease:'power3.inOut'},1.05);
inn(tl,'#s05-vault',{opacity:0,scale:.88,filter:'blur(16px)'},{opacity:1,scale:1,filter:'blur(0px)',duration:1.1},1.1);
wordsIn(tl,'#s05-name',[2.6,3.4]);
inn(tl,'#s05-upto',{opacity:0,filter:'blur(6px)'},{opacity:1,filter:'blur(0px)',duration:.2},4.45);
inn(tl,'#s05-pct',{opacity:0,filter:'blur(12px)'},{opacity:1,filter:'blur(0px)',duration:.25},4.7);
count(tl,'#s05-num',0,7,0,4.7,.55);
wordsIn(tl,'#s05-apy',[4.95,5.6]);
inn(tl,'#s05-fn',{opacity:0},{opacity:1,duration:.5},5.7);
inn(tl,'#s05-t1',{opacity:0,y:30},{opacity:1,y:0,duration:.45},6.0);
inn(tl,'#s05-t2',{opacity:0,y:30},{opacity:1,y:0,duration:.45},7.6);
wordsIn(tl,'#s05-daily',[8.8,9.2,9.8,10.3]);
""")

# s06 — DINNER: Raenest Visa card, physical tap + virtual, from stablecoin balance
S["s06"] = ("""
#s06-bg{background:%s}
#s06-cards{position:absolute;left:192px;top:240px;width:640px;height:704px;border-radius:30px;box-shadow:0 30px 70px rgba(0,0,0,.35)}
#s06-hand{position:absolute;left:1020px;top:150px;width:800px;height:927px}
#s06-paid{left:1180px;top:260px;padding:22px 30px;display:flex;align-items:center;gap:18px;font:900 46px Inter,sans-serif}
#s06-virt{position:absolute;left:192px;top:220px;width:820px;height:455px;border-radius:30px;box-shadow:0 30px 70px rgba(0,0,0,.35)}
#s06-pay{left:192px;top:520px;width:820px;padding:26px 34px}
#s06-pay .r{display:flex;align-items:center;gap:20px;padding:14px 10px;font:700 34px Inter,sans-serif;border-radius:14px}
#s06-pay .r .ck{margin-left:auto;width:40px;height:40px;border-radius:50%%;border:3px solid #d6d4df}
""" % NIGHT, f"""
<div id="s06-bg" class="bg"></div>
{clock('s06-clock','18:00','21:15',260,192,380)}
<img id="s06-cards" src="assets/photo/card_page.png">
<img id="s06-hand" src="assets/photo/hand_card.png" style="object-fit:contain">
<div id="s06-paid" class="callout"><div style="width:64px;height:64px;border-radius:50%;background:#13a36b;color:#fff;display:flex;align-items:center;justify-content:center;font:900 36px Inter">✓</div>Paid</div>
<img id="s06-virt" src="assets/photo/cards_ui.webp">
<div id="s06-pay" class="callout"><div style="font:700 28px Inter;color:#6b6b76;margin-bottom:6px">Pay from</div>
  <div class="r" id="s06-usdt"><img src="assets/brand/usdt.png" style="width:48px;height:48px">USDT balance<div class="ck" id="s06-ck"></div></div>
  <div class="r"><img src="assets/brand/usdc.png" style="width:48px;height:48px">USDC balance<div class="ck"></div></div>
</div>
<h1 id="s06-no" class="disp" style="left:192px;top:300px;font-size:104px">{words('No converting')}<br>{words('*first.')}</h1>
""", """

roll(tl,'s06-clock',.35);
tl.fromTo('#s06-clock',{x:0,y:0,scale:1},{x:0,y:-270,scale:.37,duration:.6,ease:'power3.inOut'},1.05);
inn(tl,'#s06-cards',{opacity:0,y:120,filter:'blur(10px)'},{opacity:1,y:0,filter:'blur(0px)',duration:.8},1.3);
inn(tl,'#s06-hand',{opacity:0,y:420},{opacity:1,y:0,duration:.75},2.55);
tl.fromTo('#s06-hand',{rotation:0,x:0},{rotation:-6,x:-40,duration:.25,ease:'power2.in',immediateRender:false},3.35);
tl.fromTo('#s06-hand',{rotation:-6,x:-40},{rotation:0,x:0,duration:.4,ease:'power2.out',immediateRender:false},3.6);
tl.fromTo('#s06-paid',{opacity:0,scale:.6},{opacity:1,scale:1,duration:.45,ease:'back.out(1.8)'},3.62);
out(tl,'#s06-cards',{opacity:1,x:0,filter:'blur(0px)'},{opacity:0,x:-160,filter:'blur(10px)',duration:.3},4.25);
inn(tl,'#s06-virt',{opacity:0,x:160,filter:'blur(10px)'},{opacity:1,x:0,filter:'blur(0px)',duration:.6},4.45);
tl.fromTo('#s06-virt',{y:0,scale:1},{y:-60,scale:.86,duration:.5,ease:'power3.inOut',immediateRender:false},5.75);
inn(tl,'#s06-pay',{opacity:0,y:50,filter:'blur(8px)'},{opacity:1,y:0,filter:'blur(0px)',duration:.55},5.9);
tl.fromTo('#s06-usdt',{backgroundColor:'rgba(79,59,215,0)'},{backgroundColor:'rgba(79,59,215,.10)',duration:.25},6.95);
tl.fromTo('#s06-ck',{backgroundColor:'rgba(79,59,215,0)',borderColor:'#d6d4df'},{backgroundColor:'#4F3BD7',borderColor:'#4F3BD7',duration:.25},6.95);
blurOut(tl,['#s06-virt','#s06-pay'],8.0);
wordsIn(tl,'#s06-no',[8.2,8.4,9.15]);
""")

# s07 — FRIDAY: send USDC to an external wallet on supported networks
send_a = """
<div class="lay" id="s07-scrA">
  <div style="font-size:22px">←</div>
  <div class="ap-h">Send money</div><div class="ap-s">Who are you sending to?</div>
  <div style="margin-top:20px">
  <div class="ap-row"><div class="ap-ic" style="background:#efedfb;color:#4F3BD7">▣</div>Bank Account</div>
  <div class="ap-row"><div class="ap-ic" style="background:#efedfb;color:#4F3BD7">▤</div>Mobile Money</div>
  <div class="ap-row"><div class="ap-ic" style="background:#efedfb;color:#4F3BD7">@</div>Raenest Tag</div>
  <div class="ap-row" id="s07-stab" style="border-radius:14px"><div class="ap-ic" style="background:#4F3BD7;color:#fff">$</div>Stablecoin</div>
  </div>
</div>"""
send_b = """
<div class="lay" id="s07-scrB" style="background:#fff">
  <div style="font-size:22px">←</div>
  <div class="ap-h">Send USDC</div><div class="ap-s">To an external wallet</div>
  <div style="font:700 15px Inter;color:#6b6b76;margin:22px 0 8px">Network</div>
  <div style="display:flex;flex-wrap:wrap;gap:8px">""" + "".join(
    f'<div style="border:{"2px solid #4F3BD7;color:#4F3BD7" if n=="Solana" else "1px solid #e6e5ec"};border-radius:12px;padding:10px 14px;font:700 15px Inter">{n}</div>'
    for n in ["Ethereum", "Binance", "Solana", "Polygon"]) + """</div>
  <div style="font:700 15px Inter;color:#6b6b76;margin:22px 0 8px">Recipient wallet address</div>
  <div style="border:1px solid #e6e5ec;border-radius:12px;padding:14px;font:400 15px Inter">9WzD…AWWM</div>
  <div style="font:700 15px Inter;color:#6b6b76;margin:22px 0 8px">Amount</div>
  <div style="border:1px solid #e6e5ec;border-radius:12px;padding:14px;font:700 22px Inter">120.00 USDC</div>
  <div class="ap-btn" style="margin-top:26px">Send</div>
  <div id="s07-sent" style="position:absolute;left:26px;right:26px;top:300px;bottom:0;background:#fff;text-align:center;padding-top:60px">
    <div style="width:96px;height:96px;border-radius:50%;background:#13a36b;color:#fff;display:inline-flex;align-items:center;justify-content:center;font:900 52px Inter">✓</div>
    <div style="font:900 30px Inter;margin-top:20px">Sent</div><div class="ap-s" style="margin-top:6px">120.00 USDC · Solana</div></div>
</div>"""
S["s07"] = ("""
#s07-bg{background:%s}
#s07-net{left:900px;top:520px;width:820px;padding:30px 36px}
#s07-net .k{font:700 30px Inter,sans-serif;color:#6b6b76;margin-bottom:18px}
#s07-net .n{display:inline-block;font:700 36px Inter,sans-serif;border:2px solid #e6e5ec;border-radius:16px;padding:14px 22px;margin:0 12px 12px 0}
""" % VIOLET, f"""
<div id="s07-bg" class="bg"></div>
<h1 id="s07-day" class="disp" style="left:192px;top:110px;font-size:96px">{words('Friday')}</h1>
{phone('s07-phone',260,236,send_a+send_b,cls=' sm')}
<h1 id="s07-h" class="disp" style="left:900px;top:250px;font-size:104px">{words('To any')}<br>{words('*external wallet.')}</h1>
<div id="s07-net" class="callout"><div class="k">Supported networks</div>{''.join(f'<span class="n" id="s07-n{i}">{n}</span>' for i,n in enumerate(['Ethereum','Binance','Solana','Polygon']))}</div>
""", """
tl.fromTo('#s07-day',{filter:'blur(8px)'},{filter:'blur(0px)',duration:.25,ease:'power2.out'},0);
inn(tl,'#s07-phone',{opacity:0,y:260},{opacity:1,y:0,duration:.8},.35);
tl.fromTo('#s07-stab',{backgroundColor:'rgba(79,59,215,0)'},{backgroundColor:'rgba(79,59,215,.12)',duration:.25},2.55);
tl.fromTo('#s07-scrB',{opacity:0,x:60},{opacity:1,x:0,duration:.4,ease:'power3.out'},3.0);
tl.fromTo('#s07-scrA',{opacity:1},{opacity:0,duration:.2,immediateRender:false},3.3);
tl.fromTo('#s07-sent',{opacity:0},{opacity:1,duration:.3},4.65);
wordsIn(tl,'#s07-h',[3.6,3.8,4.0,4.4]);
inn(tl,'#s07-net',{opacity:0,y:50,filter:'blur(8px)'},{opacity:1,y:0,filter:'blur(0px)',duration:.5},5.0);
[0,1,2,3].forEach(i=>{ tl.fromTo('#s07-n'+i,{borderColor:'#e6e5ec',color:'#1b1b1f'},{borderColor:'#4F3BD7',color:'#4F3BD7',duration:.2},5.35+i*.13); });
""")

# s08 — CTA: lime flood, recap, referral
REF = "referral.raenest.com/WzbV/i?referral_code=sammiedfab"
S["s08"] = ("""
#s08-bg{background:%s}
#s08-flood{background:%s;clip-path:circle(0px at 960px 540px)}
.s08-d{color:#2E096F}
#s08-card{position:absolute;left:192px;top:600px;width:1536px;height:330px;background:#2E096F;border-radius:36px;padding:40px 52px;font-family:Inter,sans-serif;color:#fff}
#s08-card .k{font:900 52px Inter,sans-serif;letter-spacing:-.02em}
#s08-card .u{font:700 40px Inter,sans-serif;color:#E5FE00;margin-top:18px}
#s08-card .c{display:inline-block;margin-top:24px;font:700 36px Inter,sans-serif;background:#fff;color:#2E096F;border-radius:16px;padding:12px 22px}
#s08-card .h{position:absolute;right:52px;bottom:48px;text-align:right;font:700 32px Inter,sans-serif;color:rgba(255,255,255,.85);line-height:1.5}
""" % (VIOLET, LIME), f"""
<div id="s08-bg" class="bg"></div>
<div id="s08-flood" class="bg"></div>
<h1 id="s08-l1" class="disp s08-d" style="left:192px;top:110px;font-size:150px">{words('Get paid. Save.')}</h1>
<h1 id="s08-l2" class="disp s08-d" style="left:192px;top:262px;font-size:150px">{words('Spend. Send.')}</h1>
<div id="s08-l3" class="bd s08-d" style="left:196px;top:450px;font-size:72px;font-weight:900;letter-spacing:-.03em">{words('All in one app.')}</div>
<div id="s08-card" data-hold="true"><div class="k">Sign up with my link</div><div class="u">{REF}</div><div class="c">Referral code: sammiedfab</div>
<div class="h">#StablecoinsonRaenest<br>#RaenestBounty</div></div>
""", """
tl.fromTo('#s08-flood',{clipPath:'circle(0px at 960px 540px)'},{clipPath:'circle(1200px at 960px 540px)',duration:.5,ease:'power2.inOut'},0);
wordsIn(tl,'#s08-l1',[.3,.55,1.05]);
wordsIn(tl,'#s08-l2',[1.5,2.05]);
wordsIn(tl,'#s08-l3',[2.55,2.8,3.0,3.25]);
inn(tl,'#s08-card',{opacity:0,y:120,filter:'blur(10px)'},{opacity:1,y:0,filter:'blur(0px)',duration:.75},3.6);
inn(tl,'#s08-card .u',{opacity:0},{opacity:1,duration:.3},4.4);
inn(tl,'#s08-card .c',{opacity:0,scale:.8},{opacity:1,scale:1,duration:.45,ease:'back.out(1.6)'},5.0);
inn(tl,'#s08-card .h',{opacity:0},{opacity:1,duration:.4},5.8);
""")

# s09 — LOGO STING, after Raenest's own reel ending
S["s09"] = ("""
#s09-bg{background:#ffffff}
#s09-mk{position:absolute;left:810px;top:250px;width:300px;height:300px;perspective:900px}
#s09-mark{width:300px;height:300px;display:block}
#s09-word{position:absolute;left:720px;top:620px;width:480px;height:103px}
#s09-tag{left:0;right:0;top:752px;text-align:center;font-size:34px;color:rgba(255,255,255,.9)}
#s09-bar{position:absolute;left:850px;top:850px;width:220px;height:6px;border-radius:3px;background:#fff;transform-origin:0 50%%}
""", """
<div id="s09-bg" class="bg"></div>
<div id="s09-mk"><img id="s09-mark" src="assets/brand/raenest-mark.svg"></div>
<img id="s09-word" src="assets/brand/raenest-wordmark.svg">
<div id="s09-tag" class="bd">Your global money partner</div>
<div id="s09-bar"></div>
""", """
tl.fromTo('#s09-bg',{backgroundColor:'#ffffff'},{backgroundColor:'#8E7BDB',duration:.12,ease:'none'},0);
tl.fromTo('#s09-bg',{backgroundColor:'#8E7BDB'},{backgroundColor:'#2E096F',duration:.22,ease:'power2.out',immediateRender:false},.12);
tl.fromTo('#s09-mark',{opacity:0,scale:1.3,filter:'blur(28px)'},{opacity:1,scale:1,filter:'blur(0px)',duration:.6,ease:'expo.out'},.05);
tl.fromTo('#s09-mark',{rotation:-70},{rotation:110,duration:3.9,ease:'sine.inOut'},.05);
tl.fromTo('#s09-mark',{rotationY:0},{rotationY:28,duration:1.9,ease:'sine.inOut'},.05);
tl.fromTo('#s09-mark',{rotationY:28},{rotationY:0,duration:1.9,ease:'sine.inOut',immediateRender:false},1.95);
tl.fromTo('#s09-word',{opacity:0,y:40,filter:'blur(12px)'},{opacity:1,y:0,filter:'blur(0px)',duration:.6,ease:'expo.out'},.75);
tl.fromTo('#s09-tag',{opacity:0,filter:'blur(6px)'},{opacity:1,filter:'blur(0px)',duration:.4,ease:'power2.out'},1.05);
tl.fromTo('#s09-bar',{scaleX:0},{scaleX:1,duration:.6,ease:'power3.inOut'},1.3);
""")

# --- write scenes ---------------------------------------------------------
for sid, start, dur, _ in SCENES:
    css, body, js = S[sid]
    with open(os.path.join(COMP, f"{sid}.html"), "w") as f:
        f.write(scene(sid, dur, css, body, js))

hosts = "\n".join(
    f'      <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" data-start="{start}" '
    f'data-duration="{dur}" data-track-index="1" data-track-kind="graphics" data-width="1920" data-height="1080"></div>'
    for sid, start, dur, _ in SCENES)
meta = json.load(open(os.path.join(ROOT, "audio_meta.json")))
vdur = {}
for v in (meta["voices"].values() if isinstance(meta["voices"], dict) else meta["voices"]):
    vdur[v.get("id") or os.path.basename(v["path"])[:-4]] = v["duration_s"]
audios = "\n".join(
    f'      <audio id="vo-{sid}" class="clip" src="assets/voice/{VOICE[sid]}.wav" data-start="{round(start+off,2)}" '
    f'data-duration="{round(vdur[VOICE[sid]],3)}" data-track-index="2" data-volume="1"></audio>'
    for sid, start, dur, off in SCENES if off is not None)

index = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>A Day in Ada's Money — Raenest</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: {INDIGO}; }}
      #root {{ width: 100%; height: 100%; position: relative; font-family: Inter, sans-serif; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1920" data-height="1080">
{hosts}
{audios}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
open(os.path.join(ROOT, "index.html"), "w").write(index)
print("total", TOTAL)
