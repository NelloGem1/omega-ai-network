#!/usr/bin/env python3
"""Regenerate fixed slides: s02_digits, s03_odds, s08_sieve, s11_cta, s13_endcard."""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
OUT = "/home/neilh/prime_video/slides"
os.makedirs(OUT, exist_ok=True)

BG = (13, 17, 23)
PANEL = (22, 27, 34)
GRID = (48, 54, 61)
TXT = (230, 237, 243)
MUT = (139, 148, 158)
GOLD = (240, 180, 41)
GREEN = (63, 185, 80)
RED = (248, 81, 73)
BLUE = (88, 166, 255)
PURPLE = (210, 168, 255)
CODEC = (170, 215, 255)

FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def font(sz, bold=True):
    return ImageFont.truetype(FB if bold else FR, sz)

def slide():
    img = Image.new("RGB", (W, H), BG)
    return img, ImageDraw.Draw(img)

def header(d, title, sub=None):
    d.text((90, 60), title, font=font(52), fill=GOLD)
    if sub:
        d.text((92, 130), sub, font=font(26, False), fill=MUT)
    d.line((90, 175, W-90, 175), fill=GRID, width=2)

def footer(d, txt="THE PRIME DISCOVERY · NELLO GEM / NEILBERT G. CARILLO × DEVIN"):
    d.text((90, H-70), txt, font=font(20, False), fill=MUT)

def save(img, name):
    img.save(os.path.join(OUT, name + ".png"))
    print("slide", name)

def cell(d, x, y, w, h, text, bg=None, fg=TXT, fs=22, bold=True):
    if bg: d.rectangle([x, y, x+w, y+h], fill=bg, outline=GRID)
    else: d.rectangle([x, y, x+w, y+h], outline=GRID)
    f = font(fs, bold)
    bb = d.textbbox((0,0), text, font=f)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    d.text((x+(w-tw)/2, y+(h-th)/2-4), text, font=f, fill=fg)

def table(d, x0, y0, cellw, cellh, data, header_row=True, fs=20,
          hl_cells=None, hl_bg=GOLD, hl_fg=(0,0,0)):
    for r, row in enumerate(data):
        for c, val in enumerate(row):
            x = x0 + c*cellw; y = y0 + r*cellh
            is_hdr = header_row and r == 0
            bg = PANEL if is_hdr else None
            fg = MUT if is_hdr else TXT
            if hl_cells and (r, c) in hl_cells:
                bg, fg = hl_bg, hl_fg
            cell(d, x, y, cellw, cellh, str(val), bg=bg, fg=fg, fs=fs, bold=not is_hdr)

# ============ S02 DIGITS (annotation moved right, clear of table) ============
img, d = slide()
header(d, "CHAPTER 1 — EVERYTHING STARTS AT 0",
       "The ten fundamental digits. Every number ever written is built from these ten cells.")
N = 10; cw = ch = 74; x0 = (W - N*cw)//2 - 40; y0 = 260
data = [["×"] + [str(c) for c in range(N)]]
for r in range(N):
    data.append([str(r)] + [str(r*c) for c in range(N)])
hl = {(r+1, c+1) for r in range(N) for c in range(N) if r == c}
table(d, x0, y0, cw, ch, data, fs=20, hl_cells=hl, hl_bg=(61, 47, 10), hl_fg=GOLD)
# annotation — moved right of the FULL 11-column table + lower, no overlap
d.text((x0 + 11*cw + 50, y0 + 120), "0×0 = 0\n1×1 = 1\n2×2 = 4\n...\n9×9 = 81",
       font=font(30, False), fill=MUT)
d.text((x0, y0+N*ch+40), "Diagonal squares highlighted — the pattern Neilbert pinned first.",
       font=font(24, False), fill=MUT)
footer(d)
save(img, "s02_digits")

# ============ S03 ODDS (mini table: gold = claimed primes, BLUE = r==c diagonal) ============
img, d = slide()
header(d, "CHAPTER 2 — THE SHOCK",
       "Diagonal where column + row = 19 produces consecutive odd numbers")
odds = [1,3,5,7,9,11,13,15,17,19]
cw2 = 150; x_start = (W - 10*cw2)//2; y = 300
for i, v in enumerate(odds):
    x = x_start + i*cw2
    cell(d, x, y, cw2-14, 130, str(v), bg=PANEL, fs=44)
d.text((W//2, y+190), "1 + 3 + 5 + ... + 19  =  100", font=font(56), fill=GOLD, anchor="mm")
d.text((W//2, y+260), "a perfect square — N² where N = 10", font=font(30, False), fill=MUT, anchor="mm")
# mini division-table corner
mt = 26; x0 = (W - 21*mt)//2; y0 = 640
data = [[""] + [str(c) for c in range(21)]]
for r in range(21):
    row = [str(r)]
    for c in range(21):
        if r == 0 and c == 0: row.append("1")
        elif r == 0: row.append(str(c))
        elif c == 0: row.append(str(r))
        elif r == c: row.append("1")
        else: row.append(str(abs(c-r)))
    data.append(row)
hl = {(r+1, c+1) for r in range(21) for c in range(21) if r+c == 19 and c >= 10 and r <= 9}
table(d, x0, y0, mt, mt, data, fs=9, hl_cells=hl, hl_bg=GOLD, hl_fg=(0,0,0))
# second highlight: diagonal cells 0x0,1x1,...,20x20 in BLUE (data pos i,i for i=1..21)
for i in range(1, 22):
    x = x0 + i*mt; yy = y0 + i*mt
    cell(d, x, yy, mt, mt, data[i][i], bg=BLUE, fg=(0,0,0), fs=9)
d.text((x0, y0-40), "the 21×21 division table — GOLD = claimed 'prime' cells · BLUE = diagonal squares",
       font=font(22, False), fill=MUT)
footer(d)
save(img, "s03_odds")

# ============ S08 SIEVE (rebuilt: 0-29 grid color-coded by which sieve kills it) ============
img, d = slide()
header(d, "CHAPTER 7 — ONE LEVEL DEEPER: THE SIEVE",
       "30 = 2×3×5 catches all small prime divisors at once")
allowed = {1,7,11,13,17,19,23,29}
cw, ch = 112, 84
cols = 15; rows = 2
x0 = (W - cols*cw)//2; y0 = 280
for n in range(30):
    r, c = divmod(n, cols)
    x = x0 + c*cw; y = y0 + r*ch
    if n in allowed:
        bg, fg, tag = GOLD, (0,0,0), ""
    elif n % 2 == 0:
        bg, fg, tag = (80, 22, 22), (255, 170, 170), "÷2"
    elif n % 3 == 0:
        bg, fg, tag = (85, 55, 20), (255, 210, 150), "÷3"
    else:
        bg, fg, tag = (60, 22, 80), (220, 170, 255), "÷5"
    cell(d, x, y, cw-8, ch-8, str(n), bg=bg, fg=fg, fs=34)
    if tag:
        d.text((x+cw-16, y+8), tag, font=font(18, False), fill=fg, anchor="ra")
# legend + texts placed BELOW the grid, clear spacing
dy = y0 + rows*ch + 40
d.text((W//2, dy), "gold = survives 2, 3 AND 5  ·  colored tags show which sieve eliminates each number",
       font=font(24, False), fill=MUT, anchor="mm")
d.text((W//2, dy+70), "8 of 30 residue classes survive — 73% of numbers excluded", font=font(38), fill=GOLD, anchor="mm")
d.text((W//2, dy+135), "the real lattice primes live on — sieve of Eratosthenes, formalized", font=font(26, False), fill=MUT, anchor="mm")
footer(d)
save(img, "s08_sieve")

# ============ S11 CTA — VERIFY HUB (wider formula box, fitted cards, +gmail) ============
img, d = slide()
d.text((W//2, 66), "VERIFY IT YOURSELF", font=font(60), fill=GOLD, anchor="mm")
d.text((W//2, 118), "Don't take our word for it — check the theorem three ways", font=font(25, False), fill=MUT, anchor="mm")
# formula bar — taller, stacked centered lines, generous padding
fx0, fy0, fw, fh = 90, 148, 1740, 140
d.rounded_rectangle([fx0, fy0, fx0+fw, fy0+fh], radius=14, fill=PANEL, outline=GOLD, width=3)
d.text((W//2, fy0+26), "THE DISCOVERY FORMULA — for every prime p > 5:", font=font(23, False), fill=MUT, anchor="mm")
d.text((W//2, fy0+72), "p % 10  ∈  { 1, 3, 7, 9 }", font=font(34), fill=GOLD, anchor="mm")
d.text((W//2, fy0+116), "p % 30  ∈  { 1,7,11,13,17,19,23,29 }", font=font(34), fill=GOLD, anchor="mm")
# three verify cards
cards = [
    ("01", "PYTHON — 2 MINUTES", "Paste the script from the story page into any Python 3.\nTests every prime to 10 million.\nExpected output: 0 counterexamples.", BLUE),
    ("02", "LEAN 4 — THE PROOF", "Install Lean via elan (official installer),\nlake build the file. Kernel checks\nEVERY case — no sorryAx, 3 axioms.", GREEN),
    ("03", "AI CHECK — FASTEST", "Paste into ChatGPT or Claude:\n\"Prove every prime > 5 ends\nin 1, 3, 7, or 9.\" Watch it derive\nthe same four digits — the proof is real.", PURPLE),
]
cw3, ch3, gap, y3 = 540, 300, 60, 318
x3 = (W - (3*cw3 + 2*gap))//2
for i, (num, title, body, col) in enumerate(cards):
    x = x3 + i*(cw3+gap)
    d.rounded_rectangle([x, y3, x+cw3, y3+ch3], radius=16, fill=PANEL, outline=col, width=3)
    d.text((x+cw3//2, y3+42), num, font=font(38), fill=col, anchor="mm")
    d.text((x+cw3//2, y3+100), title, font=font(26), fill=TXT, anchor="mm")
    for j, line in enumerate(body.split("\n")):
        d.text((x+cw3//2, y3+152+j*33), line, font=font(19, False), fill=MUT, anchor="mm")
# links
ly = y3 + ch3 + 60
d.text((W//2, ly), "nellogem1.github.io/prime-discovery/verify.html", font=font(44), fill=BLUE, anchor="mm")
d.text((W//2, ly+56), "github.com/NelloGem1/prime-discovery  ·  full story, tables, Lean decoder, verify steps", font=font(23, False), fill=MUT, anchor="mm")
# credit + gmail
d.text((W//2, 880), "Nello Gem / Neilbert G. Carillo", font=font(30), fill=TXT, anchor="mm")
d.text((W//2, 925), "independent researcher · Pagadian City, Philippines   ×   Devin", font=font(23, False), fill=GOLD, anchor="mm")
d.text((W//2, 968), "neil.hkrmzn@gmail.com", font=font(24), fill=BLUE, anchor="mm")
footer(d, "nellogem1.github.io/prime-discovery/verify.html")
save(img, "s12_cta")

# ============ S13 END CARD (silent) + gmail ============
img, d = slide()
bx0, by0, bx1, by1 = 210, 185, 1710, 625
d.rounded_rectangle([bx0, by0, bx1, by1], radius=22, fill=PANEL, outline=GOLD, width=4)
d.text((W//2, by0+42), "THE METHOD OF MATHEMATICS", font=font(26, False), fill=MUT, anchor="mm")
quote = [
 "That loop — pattern → test → precise statement →",
 "machine verification — is the actual method of",
 "mathematics.",
 "",
 "It took humanity 2,300 years to prove primes are",
 "infinite; it took this project one afternoon.",
 "",
 "The gap between a hunch and a theorem is bridgeable —",
 "and now it's been bridged, once, for real.",
]
ty = by0 + 95
for ln_ in quote:
    if ln_ == "":
        ty += 16; continue
    d.text((W//2, ty), ln_, font=font(34), fill=GOLD if "loop" in ln_ or "bridgeable" in ln_ else TXT, anchor="mm")
    ty += 44
d.text((W//2, 680), "Nello Gem / Neilbert G. Carillo  ×  Devin", font=font(30), fill=TXT, anchor="mm")
d.text((W//2, 728), "neil.hkrmzn@gmail.com", font=font(26), fill=BLUE, anchor="mm")
d.text((W//2, 780), "nellogem1.github.io/prime-discovery", font=font(34), fill=BLUE, anchor="mm")
d.text((W//2, 832), "github.com/NelloGem1/prime-discovery", font=font(26, False), fill=MUT, anchor="mm")
d.text((W//2, 895), "theorems verified in Lean 4 · zero sorrys · 3 standard axioms", font=font(24, False), fill=GREEN, anchor="mm")
footer(d)
save(img, "s14_endcard")

# ============ S12 FORMULAS (titles fitted inside panels) ============
img, d = slide()
d.text((W//2, 62), "THE FORMULAS — CHECK THEM ANY WAY", font=font(46), fill=GOLD, anchor="mm")
d.text((W//2, 116), "everything below is copy-paste verifiable · verify.html has it all in one page", font=font(23, False), fill=MUT, anchor="mm")
def codepanel(x, y, w, h, title, subtitle, code_lines, accent):
    d.rounded_rectangle([x, y, x+w, y+h], radius=16, fill=PANEL, outline=accent, width=3)
    d.text((x+24, y+16), title, font=font(24), fill=accent)
    d.text((x+24, y+50), subtitle, font=font(17, False), fill=MUT)
    ty = y + 88
    for ln in code_lines:
        col = MUT if ln.strip().startswith("#") else CODEC
        d.text((x+24, ty), ln, font=font(19, False), fill=col)
        ty += 30
py = [
 "import sympy",
 "ok1 = ok2 = ok3 = 0",
 "for p in sympy.primerange(7, 10_000_000):",
 "    if p % 10 in (1,3,7,9): ok1 += 1",
 "    if p % 30 in (1,7,11,13,17,19,23,29): ok2 += 1",
 "    ok3 += 1",
 "print(f\"last-digit law: {ok1}/{ok3} primes pass\")",
 "print(f\"mod-30 sieve:   {ok2}/{ok3} primes pass\")",
 "print(f\"counterexamples: {ok3-ok1} and {ok3-ok2}\")  # both 0",
]
codepanel(90, 160, 860, 500, "PYTHON — verify_primes.py", "expects: 0 counterexamples", py, BLUE)
ln = [
 "theorem prime_gt_five_last_digit",
 "    (p : ℕ) (hp : p.Prime) (h5 : 5 < p) :",
 "  p % 10 = 1 ∨ p % 10 = 3 ∨ p % 10 = 7 ∨ p % 10 = 9",
 "",
 "theorem prime_mod30 (hp : p.Prime) (h5 : 5 < p) :",
 "  p % 30 = 1 ∨ p % 30 = 7 ∨ p % 30 = 11 ∨ p % 30 = 13 ∨",
 "       p % 30 = 17 ∨ p % 30 = 19 ∨ p % 30 = 23 ∨ p % 30 = 29",
 "",
 "#print axioms → [propext, Classical.choice, Quot.sound]",
]
codepanel(970, 160, 860, 500, "LEAN 4 — the theorems", "kernel-checked · clean axioms · no sorryAx", ln, GREEN)
d.rounded_rectangle([90, 688, 1830, 795], radius=14, fill=PANEL, outline=PURPLE, width=3)
d.text((110, 712), "AI CHECK — paste into ChatGPT or Claude:", font=font(24, False), fill=MUT)
d.text((110, 750), "\"Prove every prime greater than 5 ends in 1, 3, 7, or 9 — then prove the mod-30 version.\"", font=font(24), fill=PURPLE)
d.text((W//2, 830), "nellogem1.github.io/prime-discovery/verify.html", font=font(40), fill=BLUE, anchor="mm")
d.text((W//2, 885), "github.com/NelloGem1/prime-discovery", font=font(23, False), fill=MUT, anchor="mm")
d.text((W//2, 950), "Nello Gem / Neilbert G. Carillo — independent researcher, Pagadian City  ×  Devin", font=font(24), fill=TXT, anchor="mm")
footer(d, "nellogem1.github.io/prime-discovery/verify.html")
save(img, "s13_formulas")

# ============ S10 THE CODE (inserted after Ch.8 theorem slide) ============
img, d = slide()
header(d, "CHAPTER 8 — THE CODE ITSELF",
       "LeanLab — the actual files, kernel-checked")
def codepanel2(x, y, w, h, title, code_lines, accent, fs=16, lh=27):
    d.rounded_rectangle([x, y, x+w, y+h], radius=16, fill=(10,14,20), outline=accent, width=3)
    d.text((x+20, y+14), title, font=font(20), fill=accent)
    ty = y + 56
    for ln in code_lines:
        is_cm = ln.strip().startswith("--") or ln.strip().startswith("#print")
        col = MUT if is_cm else CODEC
        d.text((x+20, ty), ln, font=font(fs, False), fill=col)
        ty += lh
left_code = [
 "-- PrimeDigits.lean — the last-digit law",
 "theorem prime_gt_five_last_digit",
 "    (p : ℕ) (hp : p.Prime) (h5 : 5 < p) :",
 "    p % 10 = 1 ∨ p % 10 = 3 ∨",
 "        p % 10 = 7 ∨ p % 10 = 9 := by",
 "  -- p is odd; 5 ∤ p",
 "  have h2 : p % 2 = 1 := ...",
 "  have h5dvd : ¬ 5 ∣ p := ...",
 "  omega",
 "theorem ..._coprime ... :",
 "    Nat.Coprime (p % 10) 10 := by",
 "  rcases ... <;> rw [h] <;> decide",
 "-- sanity: all primes ≤ 200 via native_decide",
 "#print axioms → clean, no sorryAx",
]
codepanel2(55, 175, 580, 560, "PrimeDigits.lean — LAST-DIGIT LAW", left_code, BLUE)
left_code = [
 "-- the sieve: primes > 5 avoid 2, 3, 5",
 "theorem not_dvd_two (hp : p.Prime) (h5 : 5 < p)",
 "    : ¬ 2 ∣ p := by ...",
 "theorem not_dvd_three (hp : p.Prime) (h5 : 5 < p)",
 "    : ¬ 3 ∣ p := by ...",
 "theorem not_dvd_five (hp : p.Prime) (h5 : 5 < p)",
 "    : ¬ 5 ∣ p := by ...",
 "",
 "theorem prime_mod30 (hp : p.Prime) (h5 : 5 < p) :",
 "    p % 30 = 1 ∨ p % 30 = 7 ∨ p % 30 = 11 ∨",
 "        p % 30 = 13 ∨ p % 30 = 17 ∨ p % 30 = 19 ∨",
 "        p % 30 = 23 ∨ p % 30 = 29 := by",
 "  interval_cases m <;> omega",
 "  -- kernel checks all 30 residue classes",
]
codepanel2(670, 175, 580, 560, "PrimeSieve.lean — THE SIEVE", left_code, GOLD)
right_code = [
 "-- Euclid's proof — written by us, not imported",
 "theorem exists_prime_not_mem (s : Finset ℕ)",
 "    (hs : ∀ p ∈ s, p.Prime) :",
 "    ∃ q, q.Prime ∧ q ∉ s := by",
 "  -- N = (product of primes) + 1",
 "  -- any prime factor of N is new",
 "",
 "theorem infinite_primes_ours :",
 "    Set.Infinite {p : ℕ | p.Prime} := by",
 "  -- contradiction: finite set can't contain all",
 "",
 "#print axioms → [propext, Classical.choice,",
 "                 Quot.sound] — no sorryAx",
]
codepanel2(1285, 175, 580, 560, "PrimeSieve.lean — EUCLID, OURS", right_code, GREEN)
d.text((W//2, 790), "PrimeDigits.lean (39 lines) + PrimeSieve.lean (90 lines) — every step kernel-checked",
       font=font(26), fill=GOLD, anchor="mm")
d.text((W//2, 845), "same kernel that checked the 175,187-module RH proof — here it fits in 90 lines",
       font=font(24, False), fill=MUT, anchor="mm")
d.text((W//2, 890), "LeanLab: PrimeSieve.lean (90) · PrimeDigits.lean (39) · GapClaims.lean (110) · Basic.lean · More.lean · Gap.lean",
       font=font(22, False), fill=MUT, anchor="mm")
d.text((W//2, 920), "full file + all theorems: nellogem1.github.io/prime-discovery/verify.html",
       font=font(24, False), fill=BLUE, anchor="mm")
d.text((W//2, 965), "this code runs in Lean 4 only — but the CLAIMS can be tested in Python, JS, or any language",
       font=font(20, False), fill=MUT, anchor="mm")
footer(d, "LeanLab/PrimeSieve.lean · Lean 4 + Mathlib")
save(img, "s10_code")

print("ALL FIXED SLIDES DONE")
