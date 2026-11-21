"""One day, one page -- Saturday 21 November 2026.

A 1024x1024 newspaper front page drawn entirely by this program with
nothing but the Python 3.13 standard library. No input files, no network,
no clock, no randomness: every run writes exactly the same PNG bytes.

The page leads with the Russian missile that came down in south-east
Poland and Warsaw's charge of a deliberate provocation, then the overnight
bombardment of Ukraine, the Wall Street sell-off, the first trilateral
Trump-Xi-Putin meeting in Shenzhen, the world court's genocide finding
against Myanmar, and the UK-EU deals -- with the rest of the day running
in a ticker along the foot of the page. Every story on it was first
reported on Saturday 21 November 2026.
"""

import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (247, 242, 230)
INK = (24, 22, 20)
RED = (178, 34, 34)
NAVY = (28, 58, 108)
TEAL = (18, 96, 88)
GOLD = (198, 152, 46)
GREY = (120, 114, 100)
PALE = (224, 217, 200)
SKY = (196, 216, 232)
CREAM = (252, 248, 238)


class Canvas:
    """An RGB pixel buffer and the few shapes this front page needs."""

    def __init__(self, width, height, colour):
        self.width = width
        self.height = height
        self.pixels = bytearray(bytes(colour) * (width * height))

    def px(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            at = (y * self.width + x) * 3
            self.pixels[at:at + 3] = bytes(colour)

    def rect(self, x, y, w, h, colour):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.px(xx, yy, colour)

    def hline(self, x, y, w, colour, thick=1):
        self.rect(x, y, w, thick, colour)

    def vline(self, x, y, h, colour, thick=1):
        self.rect(x, y, thick, h, colour)

    def frame(self, x, y, w, h, colour, thick=2):
        self.hline(x, y, w, colour, thick)
        self.hline(x, y + h - thick, w, colour, thick)
        self.vline(x, y, h, colour, thick)
        self.vline(x + w - thick, y, h, colour, thick)

    def line(self, x0, y0, x1, y1, colour):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.px(x0, y0, colour)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            span = int((r * r - (yy - cy) * (yy - cy)) ** 0.5)
            for xx in range(cx - span, cx + span + 1):
                self.px(xx, yy, colour)

    def ring(self, cx, cy, r, colour, thick=3):
        for yy in range(cy - r - thick, cy + r + thick + 1):
            for xx in range(cx - r - thick, cx + r + thick + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if r - thick / 2 <= d <= r + thick / 2:
                    self.px(xx, yy, colour)

    def starburst(self, cx, cy, r, colour):
        for k in range(16):
            ang = k * 3.14159265 / 8.0
            rr = r if k % 2 == 0 else r // 2
            import math as _m
            self.line(cx, cy,
                      cx + int(rr * _m.cos(ang)), cy + int(rr * _m.sin(ang)),
                      colour)
        self.disc(cx, cy, r // 3, colour)


# A 5x7 bitmap alphabet, drawn for this page. '#' is ink, '.' is clear.
GLYPHS = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01111", "10000", "10000", "10011", "10001", "10001", "01110"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10011", "10101", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "00100", "00100", "00100"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "00000", "01100", "01000"),
    ':': ("00000", "00000", "01100", "00000", "01100", "00000", "00000"),
    ';': ("00000", "00000", "01100", "00000", "01100", "01100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    '%': ("10001", "10010", "00010", "00100", "01000", "01001", "10001"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00001", "00010", "00100", "01000", "10000", "10000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '&': ("01100", "10010", "10010", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "01010", "00100", "11111", "00100", "01010", "00000"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
}

BLANK = ("00000",) * 7


def glyph(ch):
    return GLYPHS.get(ch, BLANK)


def text_w(s, scale):
    return len(s) * (5 * scale + scale)


def draw_text(cv, x, y, s, scale, colour):
    s = s.upper()
    for ch in s:
        rows = glyph(ch)
        for ry in range(7):
            for rx in range(5):
                if rows[ry][rx] == '1':
                    cv.rect(x + rx * scale, y + ry * scale, scale, scale,
                            colour)
        x += 6 * scale
    return x


def draw_centred(cv, cx, y, s, scale, colour):
    draw_text(cv, cx - text_w(s, scale) // 2, y, s, scale, colour)


def wrap(s, width_chars):
    words = s.split()
    lines, cur = [], ""
    for w in words:
        nxt = (cur + " " + w).strip()
        if len(nxt) <= width_chars:
            cur = nxt
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(cv, x, y, s, scale, colour, width_chars, leading=None):
    for ln in wrap(s, width_chars):
        draw_text(cv, x, y, ln, scale, colour)
        y += (leading if leading is not None else 10 * scale)
    return y


def encode_png(cv):
    raw = bytearray()
    stride = cv.width * 3
    for yy in range(cv.height):
        raw.append(0)
        raw += cv.pixels[yy * stride:(yy + 1) * stride]

    def chunk(tag, payload):
        out = struct.pack(">I", len(payload)) + tag + payload
        out += struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)
        return out

    header = struct.pack(">IIBBBBB", cv.width, cv.height, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
            chunk(b"IEND", b""))


def masthead(cv):
    cv.rect(0, 0, W, 8, RED)
    cv.rect(0, 8, W, 92, INK)
    draw_centred(cv, W // 2, 26, "THE WORLD IN ONE DAY", 6, PAPER)
    cv.hline(36, 112, W - 72, RED, 5)
    draw_centred(cv, W // 2, 128, "SATURDAY  -  21 NOVEMBER 2026", 3, INK)
    cv.hline(36, 158, W - 72, INK, 2)


def lead_story(cv):
    # Headline, left; sky panel with the missile arc, right.
    draw_text(cv, 36, 178, "RUSSIAN MISSILE", 5, RED)
    draw_text(cv, 36, 222, "HITS POLAND", 5, RED)
    para(cv, 36, 278,
         "A RUSSIAN KH-101 CRUISE MISSILE CAME DOWN IN SOUTH-EAST "
         "POLAND DURING THE OVERNIGHT ATTACK ON UKRAINE. WARSAW CALLS "
         "IT A DELIBERATE PROVOCATION. NO ONE WAS HURT.",
         2, INK, 46)
    para(cv, 36, 368,
         "NATO JETS WERE SCRAMBLED AND THE ALLIANCE CALLED IT A GRAVE "
         "VIOLATION OF ITS AIRSPACE.",
         2, NAVY, 46)
    # Sky panel: dotted arc, impact burst, field line.
    cv.rect(640, 172, 348, 240, SKY)
    cv.frame(640, 172, 348, 240, INK, 2)
    cv.hline(640, 372, 348, (90, 120, 70), 4)
    for t in range(0, 101, 4):
        ax = 660 + int(t * 2.6)
        ay = 350 - int(150 * (t / 100.0) * (2 - t / 100.0))
        cv.disc(ax, ay, 3, RED)
    cv.starburst(920, 300, 42, RED)
    cv.disc(920, 300, 10, (255, 220, 90))
    draw_text(cv, 656, 186, "NOWY LIPOWIEC", 2, INK)
    draw_text(cv, 656, 384, "60 KM FROM THE BORDER", 1, INK)


def ukraine_panel(cv):
    cv.frame(36, 436, 460, 158, INK, 2)
    draw_text(cv, 52, 450, "UKRAINE POUNDED", 3, INK)
    draw_text(cv, 52, 478, "OVERNIGHT", 3, INK)
    para(cv, 52, 512,
         "MORE THAN 400 DRONES AND 110 MISSILES. AT LEAST 8 KILLED, "
         "DOZENS WOUNDED. KYIV AND KRYVYI RIH HIT.",
         1, INK, 52)
    # Bars: drones 400+, missiles 110+.
    cv.rect(392, 470, 26, 108, RED)
    cv.rect(428, 520, 26, 58, NAVY)
    draw_text(cv, 384, 448, "400+", 1, RED)
    draw_text(cv, 424, 448, "110+", 1, NAVY)
    draw_text(cv, 380, 582, "DRONES  MISSILES", 1, GREY)


def markets_panel(cv):
    cv.frame(528, 436, 460, 158, INK, 2)
    draw_text(cv, 544, 450, "WALL STREET SLUMPS", 3, RED)
    # Falling line chart, kept clear of the text lines below it.
    pts = [(560, 484), (610, 490), (660, 494), (710, 492), (760, 500),
           (810, 504), (860, 508), (910, 512)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], RED)
        cv.line(a[0], a[1] + 1, b[0], b[1] + 1, RED)
    for p in pts:
        cv.disc(p[0], p[1], 3, RED)
    draw_text(cv, 544, 522, "S&P 500  -3.7%  INTO CORRECTION", 2, INK)
    draw_text(cv, 544, 548, "NASDAQ  -5.3%    NVIDIA  -14%", 2, INK)
    draw_text(cv, 544, 574, "AI SELL-OFF DEEPENS", 2, GREY)


def summit_panel(cv):
    cv.frame(36, 614, 460, 158, INK, 2)
    draw_text(cv, 52, 628, "TRUMP, XI AND PUTIN MEET", 2, INK)
    for i, (cx, col, ch) in enumerate(
            ((120, NAVY, "T"), (210, RED, "X"), (300, TEAL, "P"))):
        cv.disc(cx, 700, 34, col)
        cv.ring(cx, 700, 34, INK, 2)
        draw_centred(cv, cx, 686, ch, 3, PAPER)
    draw_text(cv, 360, 668, "SHENZHEN", 2, INK)
    draw_text(cv, 360, 692, "FIRST-EVER", 2, INK)
    draw_text(cv, 360, 716, "TRILATERAL", 2, INK)
    para(cv, 52, 742,
         "SUMMIT ENDS WITH FEW CONCRETE RESULTS. US PRESSES FOR A "
         "UKRAINE PEACE DEAL BY JANUARY.",
         1, INK, 52)


def court_panel(cv):
    cv.frame(528, 614, 460, 158, INK, 2)
    draw_text(cv, 544, 628, "WORLD COURT: MYANMAR", 2, INK)
    draw_text(cv, 544, 652, "GUILTY OF GENOCIDE", 2, RED)
    # Scales of justice.
    cv.vline(930, 690, 62, GOLD, 5)
    cv.hline(880, 690, 100, GOLD, 5)
    cv.line(880, 690, 866, 736, GOLD)
    cv.line(880, 690, 894, 736, GOLD)
    cv.line(980, 690, 966, 736, GOLD)
    cv.line(980, 690, 994, 736, GOLD)
    cv.hline(856, 736, 28, GOLD, 4)
    cv.hline(966, 736, 28, GOLD, 4)
    cv.hline(900, 752, 60, GOLD, 5)
    para(cv, 544, 690,
         "THE HAGUE FINDS MYANMAR'S FORCES COMMITTED STATE GENOCIDE "
         "AGAINST THE ROHINGYA.",
         1, INK, 30)


def deals_strip(cv):
    cv.rect(36, 792, 952, 52, NAVY)
    draw_text(cv, 52, 806, "UK AND EU SIGN THREE DEALS: FOOD, CARBON, "
              "YOUTH MOBILITY", 2, PAPER)
    draw_text(cv, 52, 828, "BRUSSELS SUMMIT  -  PM BURNHAM", 1, (200, 210, 235))


def ticker(cv):
    cv.rect(36, 862, 952, 96, INK)
    draw_centred(cv, W // 2, 874, "ALSO TODAY", 2, GOLD)
    draw_centred(cv, W // 2, 900,
                 "PANCREATIC-CANCER PILL HAILED AS BREAKTHROUGH", 1, PAPER)
    draw_centred(cv, W // 2, 920,
                 "ESTONIA SHUTS BORDER CROSSINGS TO RUSSIA  -  TRUMP: NO RUSH ON IRAN", 1, PAPER)
    draw_centred(cv, W // 2, 940,
                 "US SENATE REJECTS IRAN WAR-POWERS 51-48", 1, PAPER)


def build_page():
    cv = Canvas(W, H, PAPER)
    masthead(cv)
    lead_story(cv)
    ukraine_panel(cv)
    markets_panel(cv)
    summit_panel(cv)
    court_panel(cv)
    deals_strip(cv)
    ticker(cv)
    cv.hline(36, 976, W - 72, INK, 2)
    draw_centred(cv, W // 2, 986,
                 "ALL STORIES FIRST REPORTED SATURDAY 21 NOVEMBER 2026 - "
                 "DRAWN ENTIRELY BY CODE", 1, GREY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    with open(target, "wb") as handle:
        handle.write(encode_png(build_page()))


if __name__ == "__main__":
    main()
