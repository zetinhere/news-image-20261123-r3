#!/usr/bin/env python3
"""The World in One Day — Monday 23 November 2026.

One image, one idea: the day as a clock. A 24-hour dial sits in the
middle of the page; eight stories from the day sit on the dial like
hours, each with a drawn pictogram, and their headlines run in two
columns beside it, joined to the dial by leader lines. The centre of
the dial carries the date itself: 23 NOVEMBER.

Everything is drawn from scratch with PIL: no network, no downloaded
images, no randomness, no timestamps. The same command always writes
the same bytes. Run: python3 draw.py  ->  entry.png (1024x1024)
"""
import math

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# Warm newsprint palette: cream paper, dark ink, one accent per story.
PAPER = (246, 239, 224)
PAPER_SOFT = (238, 228, 204)
INK = (30, 42, 56)
MUTED = (102, 108, 112)
FAINT = (176, 164, 140)
GOLD = (198, 142, 44)
WHITE = (255, 255, 255)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def load(path, size):
    return ImageFont.truetype(path, size)


def flow_text(draw, text, fnt, width):
    """Greedy word wrap: lines of `text` that each fit `width` pixels."""
    lines = []
    for chunk in text.split("\n"):
        words = chunk.split()
        cur = ""
        for word in words:
            trial = (cur + " " + word).strip()
            if draw.textlength(trial, font=fnt) <= width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines


# ---------------------------------------------------------------- icons
# Each pictogram is drawn in white inside a coloured disc of radius ~30.
# Chunky shapes only, so they stay readable when the image is small.

def icon_broken_globe(d, cx, cy, s):
    d.ellipse([cx - s, cy - s, cx + s, cy + s], outline=WHITE, width=4)
    d.arc([cx - s, cy - s, cx + s, cy + s], 200, 340, fill=WHITE, width=3)
    d.line([cx - s, cy, cx + s, cy], fill=WHITE, width=3)
    d.line([(cx - 2, cy - s + 2), (cx + 4, cy - 4), (cx - 3, cy + 5),
            (cx + 5, cy + s - 3)], fill=WHITE, width=3)


def icon_missiles(d, cx, cy, s):
    for k, off in enumerate((-9, 0, 9)):
        x0, y0 = cx - 12 + off, cy + 12 - off
        x1, y1 = cx + 10 + off, cy - 10 - off
        d.line([x0, y0, x1, y1], fill=WHITE, width=4)
        d.polygon([(x1, y1), (x1 - 8, y1 - 1), (x1 - 1, y1 - 8)],
                  fill=WHITE)


def icon_warship(d, cx, cy, s):
    d.polygon([(cx - 16, cy + 6), (cx + 16, cy + 6), (cx + 11, cy + 14),
               (cx - 11, cy + 14)], fill=WHITE)
    d.line([cx - 2, cy + 6, cx - 2, cy - 12], fill=WHITE, width=4)
    d.line([cx - 2, cy - 12, cx + 8, cy - 8], fill=WHITE, width=3)
    d.arc([cx - 18, cy + 12, cx - 6, cy + 22], 180, 360, fill=WHITE, width=3)
    d.arc([cx + 6, cy + 12, cx + 18, cy + 22], 180, 360, fill=WHITE, width=3)


def icon_tanker_flame(d, cx, cy, s):
    d.polygon([(cx - 16, cy + 4), (cx + 16, cy + 4), (cx + 12, cy + 14),
               (cx - 12, cy + 14)], fill=WHITE)
    d.rectangle([cx - 10, cy - 2, cx - 2, cy + 4], fill=WHITE)
    d.rectangle([cx + 4, cy - 2, cx + 12, cy + 4], fill=WHITE)
    d.polygon([(cx, cy - 18), (cx + 7, cy - 6), (cx + 2, cy - 6),
               (cx + 5, cy - 1), (cx - 5, cy - 1), (cx - 2, cy - 6),
               (cx - 7, cy - 6)], fill=WHITE)


def icon_truck(d, cx, cy, s):
    d.rectangle([cx - 17, cy - 4, cx + 2, cy + 10], fill=WHITE)
    d.polygon([(cx + 2, cy + 2), (cx + 12, cy + 2), (cx + 16, cy + 10),
               (cx + 2, cy + 10)], fill=WHITE)
    d.ellipse([cx - 12, cy + 8, cx - 4, cy + 16], fill=WHITE)
    d.ellipse([cx + 8, cy + 8, cx + 16, cy + 16], fill=WHITE)
    d.line([cx - 17, cy - 4, cx - 17, cy - 10], fill=WHITE, width=3)
    d.line([cx - 17, cy - 10, cx - 8, cy - 10], fill=WHITE, width=3)


def icon_capitol(d, cx, cy, s):
    d.pieslice([cx - 11, cy - 14, cx + 11, cy + 8], 180, 360, fill=WHITE)
    d.rectangle([cx - 13, cy + 4, cx + 13, cy + 10], fill=WHITE)
    d.rectangle([cx - 17, cy + 10, cx + 17, cy + 15], fill=WHITE)
    d.line([cx, cy - 14, cx, cy - 19], fill=WHITE, width=3)
    d.polygon([(cx, cy - 19), (cx + 7, cy - 17), (cx, cy - 15)], fill=WHITE)


def icon_exam(d, cx, cy, s):
    d.rectangle([cx - 11, cy - 15, cx + 11, cy + 15], outline=WHITE, width=3)
    for yy in (-7, 0, 7):
        d.line([cx - 6, cy + yy, cx + 6, cy + yy], fill=WHITE, width=2)
    d.line([cx - 8, cy - 12, cx + 8, cy + 12], fill=WHITE, width=4)
    d.line([cx + 8, cy - 12, cx - 8, cy + 12], fill=WHITE, width=4)


def icon_target(d, cx, cy, s):
    d.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], outline=WHITE, width=4)
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], outline=WHITE, width=3)
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=WHITE)
    d.line([cx - 19, cy, cx - 15, cy], fill=WHITE, width=3)
    d.line([cx + 15, cy, cx + 19, cy], fill=WHITE, width=3)
    d.line([cx, cy - 19, cx, cy - 15], fill=WHITE, width=3)
    d.line([cx, cy + 15, cx, cy + 19], fill=WHITE, width=3)


# ---------------------------------------------------------------- stories
# Ordered clockwise from the top-right of the dial, roughly in the order
# the news broke through the day (UTC). Headlines are short; captions
# are one reported fact each. Every fact below was reported on 23 Nov 2026.

STORIES = [
    dict(tag="CLIMATE · ANTALYA", accent=(196, 90, 38), icon=icon_broken_globe,
         head="Climate talks collapse",
         body="COP31 ends with no deal as the EU rejects a text that never mentions fossil fuels."),
    dict(tag="EUROPE · POLAND", accent=(52, 96, 140), icon=icon_missiles,
         head="Russian missiles enter Poland",
         body="Three cruise missiles cross into Poland; Warsaw calls emergency NATO talks."),
    dict(tag="LIBYA · BENGHAZI", accent=(24, 120, 116), icon=icon_warship,
         head="Ukraine sinks Russian warship",
         body="Naval drones sink the corvette Mercury off Benghazi, Ukraine says."),
    dict(tag="GULF · HORMUZ", accent=(178, 52, 44), icon=icon_tanker_flame,
         head="Iran hits Bahrain, tankers struck",
         body="Iranian missiles hit a Bahrain industrial site; tankers attacked in the Strait."),
    dict(tag="GAZA", accent=(110, 122, 60), icon=icon_truck,
         head="Aid truck hit; Gaza '99% contaminated'",
         body="Israeli strike kills three near a food truck; Oxfam warns of toxic contamination."),
    dict(tag="WASHINGTON", accent=(38, 64, 110), icon=icon_capitol,
         head="Democrats take 258 House seats",
         body="Largest House majority since 1992, the final midterm count shows."),
    dict(tag="SEOUL", accent=(122, 72, 110), icon=icon_exam,
         head="Minister quits over AI exam cheating",
         body="Education minister resigns as AI cheating upends the national exam."),
    dict(tag="COPENHAGEN", accent=(176, 124, 32), icon=icon_target,
         head="Denmark foils 'assassination plot'",
         body="Danish police say Russia plotted to kill a rapper at a concert; attaché expelled."),
]

ALSO = ("Belgrade floods after record rain  ·  Bangladesh vows to jail "
        "Hasina if she returns  ·  Russian drone hits a Kharkiv kindergarten")


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # --- masthead ------------------------------------------------------
    f_kicker = load(SANS_B, 19)
    f_title = load(SERIF_B, 62)
    f_date = load(SANS_B, 24)
    d.text((W // 2, 34), "ONE DAY  ·  ONE WORLD  ·  EIGHT STORIES",
           font=f_kicker, fill=MUTED, anchor="ma")
    d.text((W // 2, 62), "The World in One Day",
           font=f_title, fill=INK, anchor="ma")
    date_text = "MONDAY  ·  23 NOVEMBER 2026"
    date_w = d.textlength(date_text, font=f_date)
    d.line([90, 144, W // 2 - date_w / 2 - 18, 144], fill=FAINT, width=2)
    d.line([W // 2 + date_w / 2 + 18, 144, W - 90, 144], fill=FAINT, width=2)
    d.text((W // 2, 132), date_text,
           font=f_date, fill=(150, 60, 40), anchor="ma")

    # --- the dial ------------------------------------------------------
    cx, cy, R = 512, 560, 250
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=PAPER_SOFT,
              outline=INK, width=3)
    # hour ticks
    for k in range(12):
        a = math.radians(k * 30)
        r0, r1 = R - 14, R - 26
        d.line([cx + r0 * math.cos(a), cy + r0 * math.sin(a),
                cx + r1 * math.cos(a), cy + r1 * math.sin(a)],
               fill=MUTED, width=3 if k % 3 == 0 else 2)
    # hour labels (06 right, 12 bottom, 18 left; the sun takes the top)
    f_hour = load(SANS_B, 17)
    d.text((cx + R - 72, cy), "06", font=f_hour, fill=MUTED, anchor="mm")
    d.text((cx, cy + R - 72), "12", font=f_hour, fill=MUTED, anchor="mm")
    d.text((cx - R + 72, cy), "18", font=f_hour, fill=MUTED, anchor="mm")
    # sun at the top of the dial, moon at the bottom: the day's arc
    sun_y = cy - R + 74
    d.ellipse([cx - 20, sun_y - 20, cx + 20, sun_y + 20], fill=GOLD)
    for k in range(8):
        a = math.radians(k * 45)
        d.line([cx + 26 * math.cos(a), sun_y + 26 * math.sin(a),
                cx + 34 * math.cos(a), sun_y + 34 * math.sin(a)],
               fill=GOLD, width=3)
    moon_y = cy + R - 95
    d.ellipse([cx - 18, moon_y - 18, cx + 18, moon_y + 18], fill=(120, 130, 150))
    d.ellipse([cx - 10, moon_y - 20, cx + 24, moon_y + 14], fill=PAPER_SOFT)
    # the date itself, in the middle of the dial
    f_big = load(SERIF_B, 118)
    f_mid = load(SERIF_B, 26)
    f_small = load(SANS_B, 16)
    d.text((cx, cy - 38), "23", font=f_big, fill=INK, anchor="mm")
    d.text((cx, cy + 42), "NOVEMBER", font=f_mid, fill=INK, anchor="mm")
    d.line([cx - 70, cy + 66, cx + 70, cy + 66], fill=FAINT, width=2)
    d.text((cx, cy + 86), "EIGHT STORIES · ONE DAY",
           font=f_small, fill=MUTED, anchor="mm")

    # --- story nodes on the dial + labels beside it --------------------
    # Angles (degrees, 0 = east, clockwise because y grows downwards).
    # Right column first, top to bottom, then left column, bottom to top:
    # the eye travels clockwise around the dial.
    slots = [
        ("right", -67.5), ("right", -22.5), ("right", 22.5), ("right", 67.5),
        ("left", 112.5), ("left", 157.5), ("left", 202.5), ("left", 247.5),
    ]
    f_tag = load(SANS_B, 14)
    f_head = load(SANS_B, 20)
    f_body = load(SANS, 15)
    label_w = 228
    for story, (side, deg) in zip(STORIES, slots):
        a = math.radians(deg)
        nx = cx + R * math.cos(a)
        ny = cy + R * math.sin(a)
        accent = story["accent"]
        # leader line from the label column to the node's near edge
        if side == "right":
            x_from = 772
            x_to = nx - 32
        else:
            x_from = 252
            x_to = nx - 32
        d.line([x_from, ny, x_to, ny], fill=accent, width=2)
        # node disc with its pictogram
        d.ellipse([nx - 30, ny - 30, nx + 30, ny + 30],
                  fill=accent, outline=INK, width=2)
        story["icon"](d, nx, ny, 17)
        # label block, vertically centred on the node
        tag_lines = [story["tag"]]
        head_lines = flow_text(d, story["head"], f_head, label_w)
        body_lines = flow_text(d, story["body"], f_body, label_w)
        block_h = (len(tag_lines) * 18 + len(head_lines) * 24
                   + len(body_lines) * 18 + 6)
        y = ny - block_h / 2
        x = 772 if side == "right" else 24
        d.text((x, y), story["tag"], font=f_tag, fill=accent)
        y += 18
        for line in head_lines:
            d.text((x, y), line, font=f_head, fill=INK)
            y += 24
        y += 2
        for line in body_lines:
            d.text((x, y), line, font=f_body, fill=(64, 70, 76))
            y += 18

    # --- footer --------------------------------------------------------
    d.line([60, 918, W - 60, 918], fill=FAINT, width=2)
    f_also_b = load(SANS_B, 16)
    f_also = load(SANS, 16)
    d.text((W // 2, 934), "ALSO TODAY", font=f_also_b,
           fill=(150, 60, 40), anchor="ma")
    also_lines = flow_text(d, ALSO, f_also, W - 120)
    y = 958
    for line in also_lines:
        d.text((W // 2, y), line, font=f_also, fill=MUTED, anchor="ma")
        y += 21

    img.save("entry.png", optimize=True)


if __name__ == "__main__":
    main()
