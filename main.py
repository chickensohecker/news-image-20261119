#!/usr/bin/env python3
"""news-image-20261119: draw one newspaper front page summing up the world
news of Thursday 19 November 2026, entirely in code (Pillow + DejaVu fonts).

Run:  mkdir -p out && python3 main.py
Writes: out/entry.png  (1400 x 1900, deterministic)
"""

import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

W, H = 1400, 1900
MARGIN = 60
CW = W - 2 * MARGIN  # 1280 content width

PAPER = (246, 241, 229)
INK = (26, 26, 26)
FAINT = (90, 84, 70)
RED = (178, 34, 34)
SKY = (214, 228, 240)
NAVY = (38, 54, 84)
GOLD = (198, 148, 44)

FONT_DIR = "/usr/share/fonts/truetype"


def font(name, size):
    for path in (
        os.path.join(FONT_DIR, "dejavu", name),
        os.path.join(FONT_DIR, "noto", name),
    ):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SERIF_I = lambda s: font("NotoSerif-Italic.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)


def text_width(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines that fit max_w."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        cur = ""
        for w in words:
            trial = f"{cur} {w}".strip()
            if text_width(draw, trial, fnt) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_w, leading, fill=INK):
    lines = wrap(draw, text, fnt, max_w)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def centered(draw, y, text, fnt, fill=INK):
    w = text_width(draw, text, fnt)
    draw.text(((W - w) / 2, y), text, font=fnt, fill=fill)
    return y + fnt.size


def rule(draw, y, thickness=3, x0=None, x1=None):
    x0 = MARGIN if x0 is None else x0
    x1 = W - MARGIN if x1 is None else x1
    draw.line([(x0, y), (x1, y)], fill=INK, width=thickness)


def double_rule(draw, y):
    rule(draw, y, 4)
    rule(draw, y + 9, 1)


# ---------------------------------------------------------------- flags
def draw_us_flag(draw, x, y, w, h):
    stripe = h / 13
    for i in range(13):
        c = (178, 34, 34) if i % 2 == 0 else (246, 241, 229)
        draw.rectangle([x, y + i * stripe, x + w, y + (i + 1) * stripe], fill=c)
    cw, ch = w * 0.4, stripe * 7
    draw.rectangle([x, y, x + cw, y + ch], fill=(60, 59, 110))
    for r in range(5):
        for c in range(6):
            sx = x + 8 + c * (cw - 16) / 5
            sy = y + 7 + r * (ch - 14) / 4
            draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 255, 255))


def draw_cn_flag(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    cx, cy = x + w * 0.17, y + h * 0.28
    r = h * 0.16
    pts = []
    import math
    for k in range(10):
        ang = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    draw.polygon(pts, fill=(255, 222, 0))
    for sx, sy in ((0.38, 0.12), (0.47, 0.24), (0.47, 0.42), (0.38, 0.55)):
        px, py = x + w * sx, y + h * sy
        draw.ellipse([px - 5, py - 5, px + 5, py + 5], fill=(255, 222, 0))


def draw_ru_flag(draw, x, y, w, h):
    for i, c in enumerate(((255, 255, 255), (0, 57, 166), (213, 0, 50))):
        draw.rectangle([x, y + i * h / 3, x + w, y + (i + 1) * h / 3], fill=c)


# ---------------------------------------------------------------- icons
def icon_tanker(draw, x, y, s):
    # hull + superstructure + flames on the water
    draw.rectangle([x, y + s * 0.55, x + s, y + s * 0.78], fill=INK)
    draw.rectangle([x + s * 0.62, y + s * 0.30, x + s * 0.86, y + s * 0.55], fill=INK)
    draw.line([x + s * 0.68, y + s * 0.30, x + s * 0.68, y + s * 0.16], fill=INK, width=4)
    for fx, fh in ((0.18, 0.30), (0.38, 0.42), (0.55, 0.26)):
        fx0 = x + s * fx
        fy0 = y + s * 0.55 - s * fh
        draw.polygon(
            [(fx0, fy0), (fx0 + s * 0.10, y + s * 0.55),
             (fx0 + s * 0.20, fy0 + s * 0.12), (fx0 + s * 0.10, fy0)],
            fill=(222, 90, 20),
        )
    for wy in (0.82, 0.90):
        draw.line([x, y + s * wy, x + s, y + s * wy], fill=FAINT, width=3)


def icon_scales(draw, x, y, s):
    cx, top = x + s / 2, y + s * 0.10
    draw.line([cx, top, cx, y + s * 0.72], fill=INK, width=5)
    draw.line([x + s * 0.12, top + s * 0.06, x + s * 0.88, top + s * 0.06],
              fill=INK, width=5)
    draw.ellipse([cx - 6, top - 6, cx + 6, top + 6], fill=INK)
    for px in (0.16, 0.84):
        px0 = x + s * px
        draw.line([px0, top + s * 0.06, px0, y + s * 0.52], fill=INK, width=3)
        draw.polygon([(px0 - s * 0.17, y + s * 0.52), (px0 + s * 0.17, y + s * 0.52),
                      (px0, y + s * 0.68)], outline=INK, width=3)
    draw.line([x + s * 0.30, y + s * 0.80, x + s * 0.70, y + s * 0.80],
              fill=INK, width=5)


def icon_controller(draw, x, y, s):
    draw.rounded_rectangle([x + s * 0.05, y + s * 0.28, x + s * 0.95, y + s * 0.80],
                           radius=int(s * 0.18), fill=INK)
    draw.ellipse([x + s * 0.16, y + s * 0.42, x + s * 0.30, y + s * 0.56],
                 fill=PAPER)
    for bx, by in ((0.70, 0.44), (0.80, 0.54), (0.60, 0.54)):
        draw.ellipse([x + s * bx - 7, y + s * by - 7, x + s * bx + 7, y + s * by + 7],
                     fill=(222, 90, 20))
    draw.line([x + s * 0.42, y + s * 0.50, x + s * 0.55, y + s * 0.50],
              fill=PAPER, width=4)


def icon_voyager(draw, x, y, s):
    # stars + dish probe flying out
    for sx, sy in ((0.1, 0.15), (0.3, 0.08), (0.85, 0.12), (0.9, 0.35), (0.15, 0.45)):
        draw.ellipse([x + s * sx - 3, y + s * sy - 3, x + s * sx + 3, y + s * sy + 3],
                     fill=INK)
    draw.polygon([(x + s * 0.30, y + s * 0.55), (x + s * 0.55, y + s * 0.30),
                  (x + s * 0.70, y + s * 0.55)], fill=INK)
    draw.line([x + s * 0.50, y + s * 0.42, x + s * 0.78, y + s * 0.30],
              fill=INK, width=4)
    draw.ellipse([x + s * 0.74, y + s * 0.22, x + s * 0.92, y + s * 0.40],
                 outline=INK, width=4)
    for k in range(3):
        draw.line([x + s * (0.24 - k * 0.06), y + s * (0.62 + k * 0.06),
                   x + s * (0.34 - k * 0.06), y + s * (0.72 + k * 0.06)],
                  fill=(222, 90, 20), width=5)


# ---------------------------------------------------------------- page
def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- nameplate (auto-fit so it never overflows the page)
    y = 34
    double_rule(d, y)
    y = 62
    name_size = 104
    while name_size > 60:
        nf = SERIF_B(name_size)
        if text_width(d, "THE WORLD IN ONE DAY", nf) <= CW:
            break
        name_size -= 2
    y = centered(d, y, "THE WORLD IN ONE DAY", SERIF_B(name_size))
    y += 6
    rule(d, y, 1)
    y += 14
    y = centered(d, y, "THURSDAY, 19 NOVEMBER 2026", SANS_B(30))
    y += 8
    y = centered(d, y, "ONE IMAGE  ·  THE WHOLE DAY  ·  PRICE: ONE GLANCE",
                 SANS(24), fill=FAINT)
    y += 18
    double_rule(d, y)

    # --- lead story: Shenzhen summit
    y = 300
    y = centered(d, y, "—  SUMMIT IN SHENZHEN  —", SANS_B(26), fill=RED)
    y += 14
    y = centered(d, y, "TRUMP, XI AND PUTIN", SERIF_B(72))
    y = centered(d, y, "SHAKE HANDS IN CHINA", SERIF_B(72))
    y += 16
    standfirst = ("Xi Jinping hugged Donald Trump on the tarmac as the US president "
                  "landed for a regional summit in Shenzhen; the three leaders are "
                  "due to sit down together on Thursday, with Ukraine and trade on the table.")
    y = draw_wrapped(d, MARGIN + 90, y, standfirst, SERIF_I(30), CW - 180, 40)
    y += 22

    # illustration panel: skyline + three flags
    px0, py0, px1, py1 = MARGIN, y, W - MARGIN, y + 315
    d.rectangle([px0, py0, px1, py1], fill=SKY, outline=INK, width=3)
    # skyline silhouettes
    import random
    rnd = random.Random(1911)
    base = py1 - 8
    bx = px0 + 14
    while bx < px1 - 90:
        bw = rnd.randint(46, 96)
        bh = rnd.randint(70, 210)
        d.rectangle([bx, base - bh, bx + bw, base], fill=NAVY)
        for wy in range(int(base - bh + 12), base - 10, 26):
            for wx in range(int(bx + 10), int(bx + bw - 8), 22):
                if rnd.random() < 0.45:
                    d.rectangle([wx, wy, wx + 8, wy + 10], fill=GOLD)
        bx += bw + 12
    # three flags on poles
    fw, fh = 210, 140
    fy = py0 + 46
    for i, fn in enumerate((draw_us_flag, draw_cn_flag, draw_ru_flag)):
        fx = px0 + 130 + i * 400
        d.line([fx + fw / 2, fy + fh, fx + fw / 2, py1 - 8], fill=INK, width=5)
        d.ellipse([fx + fw / 2 - 7, fy - 8, fx + fw / 2 + 7, fy + 6], fill=GOLD)
        fn(d, fx, fy, fw, fh)
        d.rectangle([fx, fy, fx + fw, fy + fh], outline=INK, width=2)
    caption = "SHENZHEN, CHINA — THE THREE LEADERS MEET"
    cap_w = text_width(d, caption, SANS_B(20))
    d.rectangle([px0 + 8, py1 - 40, px0 + 24 + cap_w, py1 - 8], fill=NAVY)
    d.text((px0 + 16, py1 - 34), caption,
           font=SANS_B(20), fill=(255, 255, 255))
    y = py1 + 26
    double_rule(d, y)

    # --- four stories in a 2 x 2 grid
    stories = [
        ("MIDDLE EAST", "TANKERS ABLAZE OFF HORMUZ",
         "Three oil tankers catch fire after hitting mines east of the Strait of "
         "Hormuz; the US strikes Iran's Qeshm Island and Gulf states say they "
         "repelled drone attacks.", icon_tanker),
        ("THE HAGUE", "WORLD COURT RULES ON ROHINGYA CASE TODAY",
         "The International Court of Justice delivers its verdict on Myanmar's "
         "alleged genocide of the Rohingya — a landmark ruling years in the making.",
         icon_scales),
        ("CULTURE", "GTA VI LAUNCHES WORLDWIDE",
         "Gamers enter Vice City as Grand Theft Auto VI begins its global rollout "
         "after a 13-year wait, landing to near-perfect reviews.", icon_controller),
        ("SPACE", "VOYAGER 1 REACHES A LIGHT-DAY",
         "NASA's farthest probe is now a full light-day from Earth — some 26 billion "
         "kilometres out — and still phoning home.", icon_voyager),
    ]
    col_w = (CW - 30) // 2
    row_h = 280
    gx, gy = MARGIN, y + 24
    for i, (kicker, head, body, icon) in enumerate(stories):
        cx = gx + (i % 2) * (col_w + 30)
        cy = gy + (i // 2) * (row_h + 22)
        icon(d, cx, cy + 6, 110)
        tx = cx + 128
        d.text((tx, cy + 2), kicker, font=SANS_B(21), fill=RED)
        hy = draw_wrapped(d, tx, cy + 32, head, SERIF_B(32), col_w - 128, 38)
        draw_wrapped(d, cx, hy + 10, body, SERIF(24), col_w, 31)
        if i % 2 == 0:
            d.line([cx + col_w + 15, cy, cx + col_w + 15, cy + row_h - 20],
                   fill=FAINT, width=1)
        if i < 2:
            rule(d, cy + row_h, 1, cx, cx + col_w)

    y = gy + 2 * row_h + 22 + 8
    double_rule(d, y)

    # --- also today strip
    y += 24
    d.text((MARGIN, y), "ALSO TODAY", font=SANS_B(24), fill=RED)
    y += 40
    also = [
        ("ART", "A Van Gogh sells for a record $190.4m after a row over its Nazi-era history."),
        ("TECH", "Claude-maker Anthropic is poised for a stock-market debut worth over $1.4tn."),
        ("EUROPE", "The EU proposes a €45bn loan for Ukraine, to be repaid once Russia pays reparations."),
    ]
    aw = (CW - 60) // 3
    for i, (tag, txt) in enumerate(also):
        ax = MARGIN + i * (aw + 30)
        d.text((ax, y), tag, font=SANS_B(22), fill=INK)
        draw_wrapped(d, ax, y + 32, txt, SERIF(23), aw, 28)
        if i < 2:
            d.line([ax + aw + 15, y, ax + aw + 15, y + 96], fill=FAINT, width=1)

    # --- footer
    fy = H - 58
    rule(d, fy - 14, 1)
    centered(d, fy, "Sources: NYT · BBC · AP · AFP · NDTV · The Manila Times — 19 Nov 2026  ·  Drawn entirely in code",
             SANS(20), fill=FAINT)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    img.save(path)
    print(f"wrote {path} {W}x{H}")


if __name__ == "__main__":
    main()
