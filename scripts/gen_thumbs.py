#!/usr/bin/env python3
"""Generate 5 thumbnail options (1280x720) for the Prime Discovery video."""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
OUT = "/home/neilh/prime_video/thumbs"
os.makedirs(OUT, exist_ok=True)
DL = "/mnt/c/Users/neilh/Downloads"

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

FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def font(sz, bold=True):
    return ImageFont.truetype(FB if bold else FR, sz)

def new():
    img = Image.new("RGB", (W, H), BG)
    return img, ImageDraw.Draw(img)

# ---------- helpers ----------
def glow_rect(d, box, color, radius=18, width=3):
    d.rounded_rectangle(box, radius=radius, outline=color, width=width)

def draw_mod30(d, x, y, cell=26, survivors_only=False):
    """30 residue classes 0-29, gold = the 8 survivors {1,7,11,13,17,19,23,29}"""
    surv = {1,7,11,13,17,19,23,29}
    cols = 10
    for i in range(30):
        r, c = divmod(i, cols)
        cx, cy = x + c*cell, y + r*cell
        if survivors_only:
            if i in surv:
                d.rectangle([cx, cy, cx+cell-3, cy+cell-3], fill=GOLD)
            else:
                d.rectangle([cx, cy, cx+cell-3, cy+cell-3], fill=(30,34,40))
        else:
            col = GOLD if i in surv else (45,50,58)
            d.rectangle([cx, cy, cx+cell-3, cy+cell-3], fill=col)
            d.text((cx+cell//2-4, cy+cell//2-9), str(i), font=font(11), fill=(0,0,0) if i in surv else MUT, anchor="mm")

def credit(d):
    d.text((W-16, H-14), "Nello Gem / Neilbert G. Carillo", font=font(15, False), fill=MUT, anchor="rm")

# ================= THUMB 1: "HIDDEN LAW" + mod-30 grid =================
img, d = new()
d.text((W//2, 70), "I FOUND A", font=font(44), fill=MUT, anchor="mm")
d.text((W//2, 140), "HIDDEN LAW", font=font(96), fill=GOLD, anchor="mm")
d.text((W//2, 240), "OF PRIME NUMBERS", font=font(52), fill=TXT, anchor="mm")
glow_rect(d, [W//2-330, 300, W//2+330, 480], BLUE, width=4)
d.text((W//2, 322), "p % 30 ∈ { 1,7,11,13,17,19,23,29 }", font=font(34), fill=TXT, anchor="mm")
d.text((W//2, 385), "for EVERY prime p > 5", font=font(26, False), fill=MUT, anchor="mm")
# small survivor grid right
draw_mod30(d, W-300, 520, cell=24)
d.text((W-300+120, 610), "8 of 30 residue classes", font=font(18, False), fill=MUT, anchor="mm")
d.rounded_rectangle([30, 600, 330, 660], radius=12, fill=GREEN)
d.text((180, 630), "✓ KERNEL-VERIFIED IN LEAN 4", font=font(24), fill=(0,0,0), anchor="mm")
credit(d)
img.save(f"{OUT}/thumb_1.png"); img.save(f"{DL}/Prime Thumb 1.png")

# ================= THUMB 2: last-digit law =================
img, d = new()
d.text((W//2, 80), "EVERY PRIME > 5", font=font(48), fill=MUT, anchor="mm")
d.text((W//2, 160), "ENDS IN", font=font(44), fill=MUT, anchor="mm")
for i, dig in enumerate(["1","3","7","9"]):
    x = W//2 - 270 + i*180
    glow_rect(d, [x-70, 240, x+70, 420], GOLD if i%2==0 else BLUE, width=5)
    d.text((x, 330), dig, font=font(140), fill=(0,0,0) if i%2==0 else (0,0,0), anchor="mm")
d.text((W//2, 500), "p % 10 ∈ { 1, 3, 7, 9 }", font=font(56), fill=GOLD, anchor="mm")
d.text((W//2, 575), "a hidden law — discovered by table, proved by machine", font=font(26, False), fill=MUT, anchor="mm")
d.rounded_rectangle([30, 620, 400, 680], radius=12, fill=GREEN)
d.text((215, 650), "FORMALLY VERIFIED", font=font(24), fill=(0,0,0), anchor="mm")
credit(d)
img.save(f"{OUT}/thumb_2.png"); img.save(f"{DL}/Prime Thumb 2.png")

# ================= THUMB 3: sieve grid hero =================
img, d = new()
d.text((W//2, 60), "THE PRIME SIEVE", font=font(80), fill=TXT, anchor="mm")
d.text((W//2, 140), "8 of 30 residue classes survive — 73% eliminated", font=font(30, False), fill=MUT, anchor="mm")
draw_mod30(d, W//2-250, 210, cell=44)
d.text((W//2-250, 590), "gold = possible primes   gray = impossible", font=font(22, False), fill=MUT, anchor="mm")
glow_rect(d, [W//2-300, 630, W//2+300, 690], PURPLE, width=3)
d.text((W//2, 660), "THE REAL PRIME LATTICE", font=font(28), fill=PURPLE, anchor="mm")
credit(d)
img.save(f"{OUT}/thumb_3.png"); img.save(f"{DL}/Prime Thumb 3.png")

# ================= THUMB 4: human vs machine =================
img, d = new()
d.text((W//2, 60), "HUNCH → THEOREM", font=font(72), fill=GOLD, anchor="mm")
# left: handwritten-style note
x0, y0 = 90, 160
d.rounded_rectangle([x0, y0, x0+480, y0+420], radius=16, fill=PANEL, outline=GRID, width=2)
d.text((x0+30, y0+30), "THE DISCOVERY", font=font(28), fill=BLUE, anchor="lm")
notes = ["0-9 digit table...", "primes seem to skip", "2, 5, and evens", "always!", "", "what if it's a LAW?"]
ty = y0+90
for n_ in notes:
    d.text((x0+40, ty), n_, font=font(28, False), fill=TXT)
    ty += 48
# arrow
d.text((W//2, 380), "⟶", font=font(90), fill=GOLD, anchor="mm")
# right: verified stamp
x1 = W-570
d.rounded_rectangle([x1, y0, x1+480, y0+420], radius=16, fill=(10,20,14), outline=GREEN, width=4)
d.text((x1+30, y0+30), "THE MACHINE SAYS YES", font=font(28), fill=GREEN, anchor="lm")
d.text((x1+240, y0+160), "VERIFIED", font=font(72), fill=GREEN, anchor="mm")
d.text((x1+240, y0+250), "Lean 4 kernel", font=font(26, False), fill=MUT, anchor="mm")
d.text((x1+240, y0+300), "0 sorryAx · 3 axioms", font=font(22, False), fill=MUT, anchor="mm")
d.text((W//2, 660), "one afternoon  vs  humanity's 2,300 years", font=font(30, False), fill=MUT, anchor="mm")
credit(d)
img.save(f"{OUT}/thumb_4.png"); img.save(f"{DL}/Prime Thumb 4.png")

# ================= THUMB 5: question-hook =================
img, d = new()
d.text((W//2, 80), "WHAT IF EVERY PRIME", font=font(56), fill=MUT, anchor="mm")
d.text((W//2, 160), "FOLLOWS A SECRET PATTERN?", font=font(64), fill=GOLD, anchor="mm")
# big primes row with last digits highlighted
primes = ["7","11","13","17","19","23","29","31","37","41","43","47"]
dx = 80
for i, p in enumerate(primes):
    x = dx + i*95
    d.rounded_rectangle([x, 280, x+80, 400], radius=10, fill=PANEL, outline=GRID, width=2)
    d.text((x+40, 330), p, font=font(38), fill=TXT, anchor="mm")
    last = p[-1]
    col = GOLD if last in "1379" else RED
    d.rectangle([x+30, 380, x+50, 392], fill=col)
d.text((W//2, 480), "last digit: 1 · 3 · 7 · 9 — never 0,2,4,5,6,8", font=font(30), fill=TXT, anchor="mm")
glow_rect(d, [W//2-320, 540, W//2+320, 610], BLUE, width=3)
d.text((W//2, 575), "PROVED — not just observed", font=font(34), fill=BLUE, anchor="mm")
credit(d)
img.save(f"{OUT}/thumb_5.png"); img.save(f"{DL}/Prime Thumb 5.png")

print("5 thumbnails generated")
