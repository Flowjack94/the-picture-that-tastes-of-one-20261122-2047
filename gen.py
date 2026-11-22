#!/usr/bin/env python3
"""Render one hero picture: a single ripe strawberry, one ingredient.

Drawn procedurally with PIL at 4x supersampling, downscaled to 1024x1024.
No network, no external assets. Deterministic output.
"""
import math, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SS = 4                      # supersample factor
W = H = 1024 * SS
CX = W // 2
random.seed(20261122)

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

img = Image.new("RGB", (W, H), (8, 14, 10))
d = ImageDraw.Draw(img, "RGBA")

# ---------- background: dark green radial glow, warm amber heart ----------
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
for r in range(1500, 0, -6):
    a = int(46 * (1 - r / 1500) ** 2)
    gd.ellipse([CX - r, 1500 - r, CX + r, 1500 + r], fill=(255, 176, 92, a))
glow = glow.filter(ImageFilter.GaussianBlur(90))
img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"), (0, 0))
d = ImageDraw.Draw(img, "RGBA")

# soft bokeh dots
for _ in range(26):
    x = random.randint(60, W - 60); y = random.randint(60, H - 60)
    r = random.randint(18, 70)
    a = random.randint(8, 26)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(190, 255, 200, a))
    d.ellipse([x - r // 2, y - r // 2, x + r // 2, y + r // 2], fill=(255, 240, 200, a // 2))

# ---------- strawberry body ----------
TOP, BOT = int(0.225 * H), int(0.845 * H)     # shoulders .. tip
HALF = int(0.295 * W)                          # max half width

def half_w(t):
    """t: 0 top -> 1 tip. Round shoulders, widest upper-middle, taper to a point."""
    return HALF * (math.sin(math.pi * (0.18 + 0.72 * t)) ** 0.7) * ((1.0 - t) ** 0.18)

pts_right, pts_left = [], []
N = 90
for i in range(N + 1):
    t = i / N
    y = TOP + t * (BOT - TOP)
    pts_right.append((CX + half_w(t), y))
    pts_left.append((CX - half_w(t), y))
# gentle convex dome at the top where the calyx sits
top_curve = []
for i in range(41):
    s = i / 40  # -1 .. 1 across the top
    x = CX + s * half_w(0.0)
    y = TOP - int(0.014 * H) * (1 - s * s)
    top_curve.append((x, y))
outline = top_curve + pts_right[1:] + list(reversed(pts_left[1:]))

mask = Image.new("L", (W, H), 0)
md = ImageDraw.Draw(mask)
md.polygon(outline, fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(3))

# red gradient body: bright scarlet upper-left -> deep crimson lower-right
body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
bd = ImageDraw.Draw(body)
for y in range(TOP - 40, BOT + 40, 4):
    t = max(0.0, min(1.0, (y - TOP) / (BOT - TOP)))
    r = int(232 - 62 * t); g = int(38 + 6 * t); b = int(52 - 18 * t)
    bd.line([(CX - HALF - 40, y), (CX + HALF + 40, y)], fill=(r, g, b, 255), width=4)
# light from the left: soft bright wash
wash = Image.new("RGBA", (W, H), (0, 0, 0, 0))
wd = ImageDraw.Draw(wash)
wd.ellipse([CX - HALF - 160, TOP - 260, CX + int(HALF * 0.55), BOT + 120],
           fill=(255, 120, 110, 70))
wash = wash.filter(ImageFilter.GaussianBlur(160))
body = Image.alpha_composite(body, wash)
# dark shade on the right edge
shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(shade)
sd.ellipse([CX + int(HALF * 0.15), TOP - 120, CX + HALF + 220, BOT + 160],
           fill=(90, 0, 20, 95))
shade = shade.filter(ImageFilter.GaussianBlur(140))
body = Image.alpha_composite(body, shade)

# seeds: rows following the body, pale cream, set in dimples
seeds = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd2 = ImageDraw.Draw(seeds)
row_ts = [0.14, 0.23, 0.32, 0.41, 0.50, 0.59, 0.68, 0.77, 0.85, 0.92]
for ri, t in enumerate(row_ts):
    y = TOP + t * (BOT - TOP)
    hw = half_w(t) * 0.88
    n = max(3, int(hw / (0.075 * W) * 2))
    off = (ri % 2) * 0.5
    for k in range(n):
        s = -1 + (k + 0.5 + off * 0.5) / n * 2
        if abs(s) > 0.94:
            continue
        x = CX + s * hw
        sx, sy = 15, 26  # seed half-size
        # dimple shadow, then seed
        sd2.ellipse([x - sx, y - sy + 7, x + sx, y + sy + 7], fill=(120, 10, 25, 160))
        sd2.ellipse([x - sx, y - sy, x + sx, y + sy], fill=(255, 233, 168, 255))
        sd2.ellipse([x - sx + 4, y - sy + 5, x + sx - 5, y + sy - 8], fill=(255, 246, 205, 255))
seeds = seeds.filter(ImageFilter.GaussianBlur(1))
# keep seeds inside the body
body = Image.alpha_composite(body, Image.composite(seeds, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))

# gloss: soft diagonal sheen upper-left + one crisp sparkle
gloss = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sheen = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sh = ImageDraw.Draw(sheen)
sh.ellipse([CX - int(HALF * 1.05), TOP + int(0.06 * H), CX + int(HALF * 0.10), TOP + int(0.46 * H)],
           fill=(255, 255, 255, 60))
sheen = sheen.rotate(24, resample=Image.BICUBIC, center=(CX - int(HALF * 0.45), TOP + int(0.26 * H)))
sheen = sheen.filter(ImageFilter.GaussianBlur(70))
gloss = Image.alpha_composite(gloss, sheen)
gl2 = ImageDraw.Draw(gloss)
gl2.ellipse([CX - int(HALF * 0.62), TOP + int(0.12 * H), CX - int(HALF * 0.44), TOP + int(0.20 * H)],
            fill=(255, 255, 255, 130))
gloss = gloss.filter(ImageFilter.GaussianBlur(5))
body = Image.alpha_composite(body, Image.composite(gloss, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))

# water droplets on the body (few, small, upper half)
drops = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dd = ImageDraw.Draw(drops)
drop_spots = [(0.56, 0.28), (0.40, 0.36), (0.62, 0.44), (0.44, 0.50),
              (0.58, 0.20), (0.36, 0.46), (0.52, 0.58), (0.64, 0.34)]
for fx, fy in drop_spots:
    x = CX + int((fx - 0.5) * 2 * half_w(fy - 0.05) * 0.9)
    y = TOP + int(fy * (BOT - TOP))
    r = random.randint(11, 20)
    dd.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 40))
    dd.ellipse([x - r // 2, y - r // 2 - 2, x - r // 6, y - r // 6], fill=(255, 255, 255, 200))
drops = drops.filter(ImageFilter.GaussianBlur(1))
body = Image.alpha_composite(body, Image.composite(drops, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask))

# paste body, then soft contact shadow under it
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
shd = ImageDraw.Draw(shadow)
shd.ellipse([CX - int(HALF * 0.85), BOT - 40, CX + int(HALF * 0.85), BOT + 190],
            fill=(0, 0, 0, 170))
shadow = shadow.filter(ImageFilter.GaussianBlur(60))
img.paste(Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB"), (0, 0))
img.paste(Image.alpha_composite(img.convert("RGBA"),
                                Image.composite(body, Image.new("RGBA", (W, H), (0, 0, 0, 0)), mask)
                                ).convert("RGB"), (0, 0))
d = ImageDraw.Draw(img, "RGBA")

# ---------- calyx: green leaves + stem ----------
leaf_base = (CX, TOP + int(0.045 * H))
leaf_cols = [(34, 122, 52), (46, 148, 66), (28, 105, 44)]
for li, ang in enumerate([-72, -44, -18, 8, 34, 60]):
    a = math.radians(ang - 90)
    L = int(0.145 * H) if li % 2 == 0 else int(0.115 * H)
    tip = (leaf_base[0] + int(L * math.cos(a)), leaf_base[1] + int(L * math.sin(a)))
    pa = a + math.radians(13); pb = a - math.radians(13)
    wdt = int(0.030 * H)
    p1 = (leaf_base[0] + int(wdt * math.cos(pa)), leaf_base[1] + int(wdt * math.sin(pa)))
    p2 = (leaf_base[0] + int(wdt * math.cos(pb)), leaf_base[1] + int(wdt * math.sin(pb)))
    col = leaf_cols[li % 3]
    d.polygon([leaf_base, p1, tip, p2], fill=col + (255,))
    d.line([leaf_base, tip], fill=(190, 235, 170, 160), width=5)
# stem
d.line([(CX, TOP + int(0.02 * H)), (CX + 26, TOP - int(0.075 * H))],
       fill=(96, 140, 62, 255), width=26)
d.line([(CX, TOP + int(0.02 * H)), (CX + 26, TOP - int(0.075 * H))],
       fill=(150, 200, 110, 255), width=10)

# ---------- typography: bold, high contrast, reads small ----------
def tracked_text(draw, cx, y, text, font, fill, spacing):
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total / 2
    for ch, wch in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += wch + spacing

f_top = ImageFont.truetype(BOLD, 92)
f_bot = ImageFont.truetype(BOLD, 210)
# soft shadow pass then white
for (yy, ff, txt, sp, col) in [
        (118, f_top, "ONE INGREDIENT", 34, (0, 0, 0, 160)),
        (118, f_top, "ONE INGREDIENT", 34, (255, 255, 255, 255)),
        (3520, f_bot, "STRAWBERRY", 16, (0, 0, 0, 170)),
        (3512, f_bot, "STRAWBERRY", 16, (255, 255, 255, 255))]:
    pass
# draw shadows first (offset), then faces
tracked_text(d, CX, 126, "ONE INGREDIENT", f_top, (0, 0, 0, 150), 34)
tracked_text(d, CX, 118, "ONE INGREDIENT", f_top, (255, 255, 255, 255), 34)
d.line([(CX - 300, 268), (CX + 300, 268)], fill=(255, 190, 90, 255), width=8)
tracked_text(d, CX, 3528, "STRAWBERRY", f_bot, (0, 0, 0, 170), 16)
tracked_text(d, CX, 3520, "STRAWBERRY", f_bot, (255, 255, 255, 255), 16)

img = img.resize((1024, 1024), Image.LANCZOS)
img.save("/home/hatch/workspace/makefun/the-picture-that-tastes-of-one-20261122-2047/entry.png",
         optimize=True)
import os
print("saved", os.path.getsize("/home/hatch/workspace/makefun/the-picture-that-tastes-of-one-20261122-2047/entry.png"), "bytes")
