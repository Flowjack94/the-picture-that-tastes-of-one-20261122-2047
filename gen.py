#!/usr/bin/env python3
"""Draw ONE INGREDIENT: a single ripe strawberry, fully in code (PIL).

Output: entry.png, 1024x1024, < 1 MiB. No photos, no assets, no network.
Rendered at 4x (4096) and downscaled with LANCZOS for smooth edges.
"""
import math
import os
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 4096            # supersampled canvas
OUT = 1024
CX = S // 2
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# ---------------------------------------------------------------- background
def vertical_gradient(w, h, top, bottom):
    g = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / (h - 1)
        g.putpixel((0, y), tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return g.resize((w, h))

img = vertical_gradient(S, S, (16, 66, 30), (7, 32, 15)).convert("RGBA")

# soft radial glow behind the berry
glow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([CX - 1650, 700, CX + 1650, 4000], fill=(58, 140, 74, 110))
glow = glow.filter(ImageFilter.GaussianBlur(320))
img.alpha_composite(glow)

# faint darker vignette at the corners
vig = Image.new("RGBA", (S, S), (0, 0, 0, 0))
vd = ImageDraw.Draw(vig)
vd.ellipse([-700, -700, S + 700, S + 700], outline=(0, 0, 0, 120), width=700)
vig = vig.filter(ImageFilter.GaussianBlur(260))
img.alpha_composite(vig)

# ---------------------------------------------------------------- strawberry body
# Closed smooth outline via Catmull-Rom through control points (right side,
# top -> tip, then mirrored). Berry: top y=1080, tip y=3160, max half-width 1180.
ctrl_right = [
    (CX, 1080), (CX + 420, 1090), (CX + 820, 1180), (CX + 1060, 1420),
    (CX + 1170, 1780), (CX + 1140, 2180), (CX + 1000, 2560),
    (CX + 760, 2880), (CX + 460, 3090), (CX + 170, 3160), (CX, 3165),
]

def catmull_rom(points, samples=24):
    pts = [points[0]] + points + [points[-1]]
    out = []
    for i in range(len(pts) - 3):
        p0, p1, p2, p3 = pts[i], pts[i + 1], pts[i + 2], pts[i + 3]
        for j in range(samples):
            t = j / samples
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t
                       + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t
                       + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(points[-1])
    return out

right = catmull_rom(ctrl_right)
left = [(2 * CX - x, y) for (x, y) in reversed(right)]
outline = right + left

mask = Image.new("L", (S, S), 0)
ImageDraw.Draw(mask).polygon(outline, fill=255)

# red body: vertical gradient, clipped by the mask
body_grad = vertical_gradient(S, S, (255, 77, 61), (143, 15, 30)).convert("RGBA")
body = Image.new("RGBA", (S, S), (0, 0, 0, 0))
body.paste(body_grad, (0, 0), mask)
img.alpha_composite(body)

# shading: darker red on the right flank + deep red at the bottom, clipped
shade = Image.new("RGBA", (S, S), (0, 0, 0, 0))
sd = ImageDraw.Draw(shade)
sd.ellipse([CX + 250, 1200, CX + 1350, 3200], fill=(120, 8, 22, 150))
sd.ellipse([CX - 900, 2600, CX + 900, 3350], fill=(110, 6, 20, 130))
shade = shade.filter(ImageFilter.GaussianBlur(220))
shade.putalpha(Image.composite(shade.split()[3], Image.new("L", (S, S), 0), mask))
img.alpha_composite(shade)

# big soft highlight, upper left of the berry, clipped
hi = Image.new("RGBA", (S, S), (0, 0, 0, 0))
hd = ImageDraw.Draw(hi)
hd.ellipse([CX - 1050, 1150, CX + 150, 2350], fill=(255, 190, 170, 120))
hi = hi.filter(ImageFilter.GaussianBlur(260))
hi.putalpha(Image.composite(hi.split()[3], Image.new("L", (S, S), 0), mask))
img.alpha_composite(hi)

# small crisp gloss streak, upper left
gloss = Image.new("RGBA", (S, S), (0, 0, 0, 0))
gd2 = ImageDraw.Draw(gloss)
gd2.ellipse([CX - 830, 1330, CX - 330, 1980], fill=(255, 255, 255, 90))
gloss = gloss.filter(ImageFilter.GaussianBlur(90))
gloss.putalpha(Image.composite(gloss.split()[3], Image.new("L", (S, S), 0), mask))
img.alpha_composite(gloss)

# ---------------------------------------------------------------- seeds (achenes)
def inside_mask(x, y):
    return 0 <= x < S and 0 <= y < S and mask.getpixel((int(x), int(y))) > 128

seed_layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
sdd = ImageDraw.Draw(seed_layer)
row = 0
for y in range(1420, 2980, 250):
    # find body extent on this row by scanning the mask
    xs = [x for x in range(CX - 1250, CX + 1250, 40) if inside_mask(x, y)]
    if not xs:
        continue
    lo, hi_x = min(xs) + 170, max(xs) - 170
    off = 130 if row % 2 else 0
    x = lo + off
    while x < hi_x:
        # soft shadow under the seed
        sdd.ellipse([x - 30, y - 38, x + 44, y + 66], fill=(90, 5, 15, 110))
        # pale seed, slightly teardrop: ellipse + pointed bottom
        sdd.ellipse([x - 34, y - 52, x + 34, y + 52], fill=(255, 223, 142, 255),
                    outline=(190, 130, 40, 255), width=7)
        sdd.ellipse([x - 12, y - 40, x + 4, y - 18], fill=(255, 255, 255, 170))
        x += 265
    row += 1
seed_layer.putalpha(Image.composite(seed_layer.split()[3], Image.new("L", (S, S), 0), mask))
img.alpha_composite(seed_layer)

# ---------------------------------------------------------------- dew drops
rng = random.Random(7)
dew = Image.new("RGBA", (S, S), (0, 0, 0, 0))
dd = ImageDraw.Draw(dew)
placed = 0
tries = 0
while placed < 26 and tries < 600:
    tries += 1
    x = rng.uniform(CX - 1050, CX + 1050)
    y = rng.uniform(1250, 3050)
    if not inside_mask(x, y):
        continue
    r = rng.uniform(22, 52)
    dd.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 75))
    dd.ellipse([x - r * 0.45, y - r * 0.55, x + r * 0.25, y - r * 0.05],
               fill=(255, 255, 255, 170))
    placed += 1
dew.putalpha(Image.composite(dew.split()[3], Image.new("L", (S, S), 0), mask))
img.alpha_composite(dew)

# ---------------------------------------------------------------- calyx leaves + stem
leaf_layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
ld = ImageDraw.Draw(leaf_layer)
base = (CX, 1140)
tips = [(-560, -190), (-470, -360), (-280, -460), (0, -500),
        (280, -460), (470, -360), (560, -190)]
greens = [(46, 125, 50), (67, 160, 71)]
for i, (dx, dy) in enumerate(tips):
    tx, ty = CX + dx, 1140 + dy
    # leaf as a pointed petal: two side control points perpendicular to the spoke
    mx, my = (CX + tx) / 2, (1140 + ty) / 2
    px, py = -(ty - 1140), (tx - CX)          # perpendicular
    plen = math.hypot(px, py) or 1
    w = 105
    ux, uy = px / plen * w, py / plen * w
    col = greens[i % 2]
    ld.polygon([(CX - ux * 0.4, 1140 - uy * 0.4),
                (mx + ux, my + uy), (tx, ty),
                (mx - ux, my - uy)], fill=col + (255,))
    ld.line([(CX, 1140), (tx, ty)], fill=(27, 94, 32, 255), width=14)
leaf_layer = leaf_layer.filter(ImageFilter.GaussianBlur(3))
img.alpha_composite(leaf_layer)

# stem
stem = Image.new("RGBA", (S, S), (0, 0, 0, 0))
std = ImageDraw.Draw(stem)
std.rounded_rectangle([CX - 42, 660, CX + 42, 1000], radius=40, fill=(78, 122, 46, 255))
std.rounded_rectangle([CX - 42, 660, CX + 6, 1000], radius=40, fill=(104, 153, 66, 255))
img.alpha_composite(stem)

# ---------------------------------------------------------------- ground shadow
shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
shd = ImageDraw.Draw(shadow)
shd.ellipse([CX - 950, 3180, CX + 950, 3400], fill=(0, 0, 0, 130))
shadow = shadow.filter(ImageFilter.GaussianBlur(110))
img.alpha_composite(shadow)

# ---------------------------------------------------------------- text
def draw_text_centered(draw, text, y_center, size, fill, stroke_fill, stroke_w):
    font = ImageFont.truetype(FONT_PATH, size)
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_w)
    w = bbox[2] - bbox[0]
    draw.text((CX - w / 2 - bbox[0], y_center - (bbox[3] - bbox[1]) / 2 - bbox[1]),
              text, font=font, fill=fill, stroke_width=stroke_w,
              stroke_fill=stroke_fill)

txt = Image.new("RGBA", (S, S), (0, 0, 0, 0))
td = ImageDraw.Draw(txt)
# shadow pass, then bold white with dark-green outline
def text_pass(d, text, yc, size, fill, stroke, sw, dx=0, dy=0):
    font = ImageFont.truetype(FONT_PATH, size)
    bbox = d.textbbox((0, 0), text, font=font, stroke_width=sw)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text((CX - w / 2 - bbox[0] + dx, yc - h / 2 - bbox[1] + dy),
           text, font=font, fill=fill, stroke_width=sw, stroke_fill=stroke)

text_pass(td, "ONE INGREDIENT", 470, 300, (0, 0, 0, 110), (0, 0, 0, 110), 10, dx=12, dy=16)
text_pass(td, "ONE INGREDIENT", 470, 300, (255, 255, 255, 255), (10, 46, 20, 255), 14)
text_pass(td, "STRAWBERRY", 3620, 350, (0, 0, 0, 110), (0, 0, 0, 110), 10, dx=12, dy=16)
text_pass(td, "STRAWBERRY", 3620, 350, (255, 255, 255, 255), (10, 46, 20, 255), 14)
img.alpha_composite(txt)

# ---------------------------------------------------------------- downscale + save
final = img.convert("RGB").resize((OUT, OUT), Image.LANCZOS)
out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
final.save(out_path, "PNG", optimize=True)
print("saved", out_path, os.path.getsize(out_path), "bytes")
