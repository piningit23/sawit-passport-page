#!/usr/bin/env python3
"""The Passport Page of a Country That Isn't There.

Invented passport spread: Republic of Zaloria.
Pure Python 3.13 stdlib, no network, no external assets.
Own bitmap font, own raster helpers, own PNG encoder.
Fully deterministic: fixed data, no time, no randomness.
"""
import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
NAVY   = (22, 35, 63)
GOLD   = (201, 162, 39)
PAPER  = (245, 238, 220)
PAPER2 = (238, 229, 205)
INK    = (30, 36, 48)
GREY   = (107, 111, 118)
BURG   = (122, 31, 43)
TEAL   = (20, 101, 95)
STAMP_BLUE = (31, 95, 139)
STAMP_GREEN = (46, 107, 52)
RULE   = (169, 150, 104)
SPINE  = (185, 168, 127)
SKIN   = (216, 169, 131)
SKIN_D = (201, 151, 111)
HAIR   = (58, 42, 34)
JACKET = (34, 52, 78)
PHOTO_BG = (126, 143, 138)
WHITE  = (255, 255, 255)
CREAM2 = (253, 248, 234)

# ---------------------------------------------------------------- 5x7 font
FONT = {
 'A': ["01110","10001","10001","11111","10001","10001","10001"],
 'B': ["11110","10001","10001","11110","10001","10001","11110"],
 'C': ["01110","10001","10000","10000","10000","10001","01110"],
 'D': ["11110","10001","10001","10001","10001","10001","11110"],
 'E': ["11111","10000","10000","11110","10000","10000","11111"],
 'F': ["11111","10000","10000","11110","10000","10000","10000"],
 'G': ["01110","10001","10000","10111","10001","10001","01111"],
 'H': ["10001","10001","10001","11111","10001","10001","10001"],
 'I': ["01110","00100","00100","00100","00100","00100","01110"],
 'J': ["00111","00010","00010","00010","00010","10010","01100"],
 'K': ["10001","10010","10100","11000","10100","10010","10001"],
 'L': ["10000","10000","10000","10000","10000","10000","11111"],
 'M': ["10001","11011","10101","10101","10001","10001","10001"],
 'N': ["10001","11001","10101","10011","10001","10001","10001"],
 'O': ["01110","10001","10001","10001","10001","10001","01110"],
 'P': ["11110","10001","10001","11110","10000","10000","10000"],
 'Q': ["01110","10001","10001","10001","10101","10010","01101"],
 'R': ["11110","10001","10001","11110","10100","10010","10001"],
 'S': ["01111","10000","10000","01110","00001","00001","11110"],
 'T': ["11111","00100","00100","00100","00100","00100","00100"],
 'U': ["10001","10001","10001","10001","10001","10001","01110"],
 'V': ["10001","10001","10001","10001","10001","01010","00100"],
 'W': ["10001","10001","10001","10101","10101","11011","10001"],
 'X': ["10001","10001","01010","00100","01010","10001","10001"],
 'Y': ["10001","10001","01010","00100","00100","00100","00100"],
 'Z': ["11111","00001","00010","00100","01000","10000","11111"],
 '0': ["01110","10001","10011","10101","11001","10001","01110"],
 '1': ["00100","01100","00100","00100","00100","00100","01110"],
 '2': ["01110","10001","00001","00110","01000","10000","11111"],
 '3': ["11111","00010","00100","00010","00001","10001","01110"],
 '4': ["00010","00110","01010","10010","11111","00010","00010"],
 '5': ["11111","10000","11110","00001","00001","10001","01110"],
 '6': ["00110","01000","10000","11110","10001","10001","01110"],
 '7': ["11111","00001","00010","00100","01000","01000","01000"],
 '8': ["01110","10001","10001","01110","10001","10001","01110"],
 '9': ["01110","10001","10001","01111","00001","00010","01100"],
 ' ': ["00000","00000","00000","00000","00000","00000","00000"],
 '.': ["00000","00000","00000","00000","00000","01100","01100"],
 ',': ["00000","00000","00000","00000","01100","00100","01000"],
 '-': ["00000","00000","00000","01110","00000","00000","00000"],
 '/': ["00001","00010","00010","00100","01000","01000","10000"],
 '<': ["00010","00100","01000","10000","01000","00100","00010"],
 '>': ["01000","00100","00010","00001","00010","00100","01000"],
 '(': ["00010","00100","01000","01000","01000","00100","00010"],
 ')': ["01000","00100","00010","00010","00010","00100","01000"],
 ':': ["00000","01100","01100","00000","01100","01100","00000"],
 "'": ["00100","00100","01000","00000","00000","00000","00000"],
 '&': ["01100","10010","10100","01000","10101","10010","01101"],
 '+': ["00000","00100","00100","11111","00100","00100","00000"],
 '=': ["00000","00000","11111","00000","11111","00000","00000"],
 '%': ["11001","11010","00010","00100","01000","01011","10011"],
 '!': ["00100","00100","00100","00100","00100","00000","00100"],
 '?': ["01110","10001","00001","00010","00100","00000","00100"],
 '"': ["01010","01010","01010","00000","00000","00000","00000"],
 ';': ["00000","01100","01100","00000","01100","00100","01000"],
 '*': ["00000","10101","01110","11111","01110","10101","00000"],
}
BLANK = ["00000"] * 7


def text_width(s, scale, spacing=0.0):
    if not s:
        return 0.0
    return len(s) * 6.0 * scale + (len(s) - 1) * spacing


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def fill_rect(self, x, y, w, h, c):
        x0, y0 = max(0, int(x)), max(0, int(y))
        x1, y1 = min(self.w, int(x + w)), min(self.h, int(y + h))
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect_outline(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            if t <= 1:
                self.set(x0, y0, c)
            else:
                self.fill_rect(x0 - t // 2, y0 - t // 2, t, t, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def polyline(self, pts, c, t=1, closed=False):
        n = len(pts)
        for i in range(n - 1):
            self.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], c, t)
        if closed and n > 2:
            self.line(pts[-1][0], pts[-1][1], pts[0][0], pts[0][1], c, t)

    def fill_poly(self, pts, c):
        if len(pts) < 3:
            return
        ys = sorted(p[1] for p in pts)
        y0, y1 = int(math.ceil(min(ys))), int(math.floor(max(ys)))
        n = len(pts)
        for y in range(y0, y1 + 1):
            xs = []
            for i in range(n):
                x1, yy1 = pts[i]
                x2, yy2 = pts[(i + 1) % n]
                if (yy1 <= y < yy2) or (yy2 <= y < yy1):
                    if yy2 != yy1:
                        xs.append(x1 + (y - yy1) * (x2 - x1) / (yy2 - yy1))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                xa, xb = int(math.ceil(xs[k])), int(math.floor(xs[k + 1]))
                for x in range(xa, xb + 1):
                    self.set(x, y, c)

    def fill_ellipse(self, cx, cy, rx, ry, c):
        for y in range(int(cy - ry), int(cy + ry) + 1):
            dy = (y - cy) / ry if ry else 0
            if abs(dy) > 1:
                continue
            dx = rx * math.sqrt(max(0.0, 1.0 - dy * dy))
            for x in range(int(cx - dx), int(cx + dx) + 1):
                self.set(x, y, c)

    def ellipse_outline(self, cx, cy, rx, ry, c, t=1, rot=0.0):
        pts = []
        steps = 72
        for i in range(steps + 1):
            a = 2.0 * math.pi * i / steps
            ex, ey = rx * math.cos(a), ry * math.sin(a)
            if rot:
                co, si = math.cos(rot), math.sin(rot)
                ex, ey = ex * co - ey * si, ex * si + ey * co
            pts.append((cx + ex, cy + ey))
        self.polyline(pts, c, t)

    # ---- text ----
    def _glyph_pixels(self, s, scale):
        """Yield (local_x, local_y) pixel centres for the text, origin top-left."""
        x = 0.0
        for ch in s:
            g = FONT.get(ch, BLANK)
            for r in range(7):
                row = g[r]
                for col in range(5):
                    if row[col] == '1':
                        yield (x + col * scale, r * scale)
            x += 6.0 * scale

    def text(self, x, y, s, scale, c, align='l', spacing=0.0, bold=False, angle=0.0):
        """Draw text. (x,y) is top-left for align 'l', centre-top for 'c',
        right-top for 'r'. angle rotates around the text-block centre."""
        s = s.upper()
        wdt = text_width(s, scale, spacing)
        hgt = 7.0 * scale
        if align == 'c':
            x = x - wdt / 2.0
        elif align == 'r':
            x = x - wdt
        cx, cy = x + wdt / 2.0, y + hgt / 2.0
        passes = [(0, 0), (1, 0)] if bold else [(0, 0)]
        for dx, dy in passes:
            for (px, py) in self._glyph_pixels(s, scale):
                # scale each glyph pixel into a filled square
                fx, fy = x + px + dx, y + py + dy
                if angle:
                    rx, ry = fx - cx, fy - cy
                    co, si = math.cos(angle), math.sin(angle)
                    fx, fy = cx + rx * co - ry * si, cy + rx * si + ry * co
                    # draw a small square so rotated text stays solid
                    sz = max(1, int(round(scale)))
                    self.fill_rect(int(round(fx)) - sz // 2, int(round(fy)) - sz // 2,
                                   sz, sz, c)
                else:
                    x0, y0 = int(round(fx)), int(round(fy))
                    x1, y1 = int(round(fx + scale)), int(round(fy + scale))
                    self.fill_rect(x0, y0, max(1, x1 - x0), max(1, y1 - y0), c)

    def text_lines_rot(self, cx, cy, lines, scale, c, angle, line_h=None, bold=False):
        """Centre a stack of text lines at (cx, cy), rotated by angle (radians)."""
        if line_h is None:
            line_h = 7.0 * scale + 6.0
        n = len(lines)
        for i, ln in enumerate(lines):
            ly = cy + (i - (n - 1) / 2.0) * line_h
            # anchor: centre of this line; rotate offset from stack centre
            dx, dy = 0.0, ly - cy
            co, si = math.cos(angle), math.sin(angle)
            rx, ry = dx * co - dy * si, dx * si + dy * co
            self.text(cx + rx, cy + ry - 7.0 * scale / 2.0, ln, scale, c,
                      align='c', bold=bold, angle=angle)


# ---------------------------------------------------------------- MRZ checks
def mrz_value(ch):
    if ch.isdigit():
        return int(ch)
    if 'A' <= ch <= 'Z':
        return ord(ch) - 55
    return 0  # '<' and anything else


def mrz_check(s):
    weights = (7, 3, 1)
    total = 0
    for i, ch in enumerate(s):
        total += mrz_value(ch) * weights[i % 3]
    return str(total % 10)


def build_mrz():
    line1 = "P<ZLO" + "VOSS<<ELENA<MARA"
    line1 = line1 + "<" * (44 - len(line1))
    doc = "ZL0048217"
    c1 = mrz_check(doc)
    dob, c2 = "940612", mrz_check("940612")
    exp, c3 = "330314", mrz_check("330314")
    pers = "<" * 14
    c4 = mrz_check(pers)
    body = doc + c1 + "ZLO" + dob + c2 + "F" + exp + c3 + pers + c4
    c5 = mrz_check(body)
    line2 = body + c5
    assert len(line1) == 44 and len(line2) == 44, (len(line1), len(line2))
    return line1, line2


# ---------------------------------------------------------------- portrait
def draw_portrait(cv, x0, y0, x1, y1):
    # frame
    cv.fill_rect(x0, y0, x1 - x0, y1 - y0, PHOTO_BG)
    cv.fill_rect(x0, y0, x1 - x0, 26, (140, 156, 150))  # lighter band top
    cx = (x0 + x1) // 2
    # shoulders / jacket
    cv.fill_poly([(x0 + 8, y1), (x0 + 18, y1 - 42), (cx - 28, y1 - 52),
                  (cx + 28, y1 - 52), (x1 - 18, y1 - 42), (x1 - 8, y1)], JACKET)
    # shirt + tie
    cv.fill_poly([(cx - 16, y1 - 50), (cx + 16, y1 - 50), (cx, y1 - 18)], WHITE)
    cv.fill_poly([(cx - 6, y1 - 48), (cx + 6, y1 - 48), (cx + 4, y1 - 22),
                  (cx - 4, y1 - 22)], BURG)
    # neck
    cv.fill_rect(cx - 11, y1 - 78, 22, 30, SKIN_D)
    # ears
    cv.fill_ellipse(x0 + 40, y0 + 62, 5, 9, SKIN)
    cv.fill_ellipse(x1 - 40, y0 + 62, 5, 9, SKIN)
    # head
    cv.fill_ellipse(cx, y0 + 60, 30, 38, SKIN)
    # soft shade on the right side of the face
    cv.fill_poly([(cx + 12, y0 + 26), (cx + 26, y0 + 34), (cx + 24, y0 + 88),
                  (cx + 10, y0 + 96), (cx + 14, y0 + 60)], SKIN_D)
    # hair: cap over the top of the head, swept to one side
    cv.fill_poly([(cx - 31, y0 + 62), (cx - 30, y0 + 30), (cx - 12, y0 + 18),
                  (cx + 10, y0 + 18), (cx + 28, y0 + 28), (cx + 31, y0 + 58),
                  (cx + 22, y0 + 44), (cx + 4, y0 + 34), (cx - 16, y0 + 36),
                  (cx - 24, y0 + 48)], HAIR)
    # eyebrows
    cv.line(cx - 20, y0 + 52, cx - 8, y0 + 50, HAIR, 2)
    cv.line(cx + 8, y0 + 50, cx + 20, y0 + 52, HAIR, 2)
    # eyes
    cv.line(cx - 19, y0 + 58, cx - 9, y0 + 58, INK, 2)
    cv.line(cx + 9, y0 + 58, cx + 19, y0 + 58, INK, 2)
    # nose
    cv.polyline([(cx + 1, y0 + 60), (cx - 1, y0 + 74), (cx + 3, y0 + 77)],
                (168, 123, 82), 2)
    # mouth
    cv.line(cx - 10, y0 + 88, cx + 10, y0 + 88, (138, 90, 59), 2)
    # frame border
    cv.rect_outline(x0, y0, x1 - x0, y1 - y0, INK, 2)
    cv.rect_outline(x0 + 4, y0 + 4, x1 - x0 - 8, y1 - y0 - 8, WHITE, 1)


# ---------------------------------------------------------------- emblem
def draw_emblem(cv, cx, cy):
    # shield
    pts = [(cx - 30, cy - 26), (cx + 30, cy - 26), (cx + 30, cy + 8),
           (cx, cy + 30), (cx - 30, cy + 8)]
    cv.fill_poly(pts, CREAM2)
    cv.polyline(pts, BURG, 2, closed=True)
    # star
    sx, sy, r = cx, cy - 12, 9
    star = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        star.append((sx + rr * math.cos(a), sy + rr * math.sin(a)))
    cv.fill_poly(star, BURG)
    # waves (the Meridian sea)
    for k, wy in enumerate((cy + 6, cy + 13, cy + 20)):
        wpts = []
        for t in range(0, 25):
            wx = cx - 20 + t * 40 / 24
            wpts.append((wx, wy + 2 * math.sin(t * 0.9 + k)))
        cv.polyline(wpts, TEAL, 2)


# ---------------------------------------------------------------- stamps
def stamp_oval(cv, cx, cy, rx, ry, angle_deg, color, lines, scale=1.5):
    a = math.radians(angle_deg)
    cv.ellipse_outline(cx, cy, rx, ry, color, 3, rot=a)
    cv.ellipse_outline(cx, cy, rx - 7, ry - 7, color, 1, rot=a)
    cv.text_lines_rot(cx, cy, lines, scale, color, a, bold=True)


def stamp_round(cv, cx, cy, r, angle_deg, color, lines, scale=1.5):
    a = math.radians(angle_deg)
    cv.ellipse_outline(cx, cy, r, r, color, 3, rot=a)
    cv.ellipse_outline(cx, cy, r - 7, r - 7, color, 1, rot=a)
    cv.text_lines_rot(cx, cy, lines, scale, color, a, bold=True)


def stamp_rect(cv, cx, cy, w, h, angle_deg, color, lines, scale=1.5):
    a = math.radians(angle_deg)
    co, si = math.cos(a), math.sin(a)

    def rot(px, py):
        return (cx + px * co - py * si, cy + px * si + py * co)
    hw, hh = w / 2.0, h / 2.0
    pts = [rot(-hw, -hh), rot(hw, -hh), rot(hw, hh), rot(-hw, hh)]
    cv.polyline(pts, color, 3, closed=True)
    pts2 = [rot(-hw + 7, -hh + 7), rot(hw - 7, -hh + 7),
            rot(hw - 7, hh - 7), rot(-hw + 7, hh - 7)]
    cv.polyline(pts2, color, 1, closed=True)
    cv.text_lines_rot(cx, cy, lines, scale, color, a, bold=True)


def signature(cv, x, y, w, color):
    # a flowing handwritten squiggle, fixed points (deterministic)
    pts = [(x + int(dx * w), y + int(dy * 14)) for dx, dy in
           [(0.00, 0.55), (0.06, 0.10), (0.10, 0.75), (0.15, 0.20),
            (0.20, 0.60), (0.26, 0.05), (0.30, 0.80), (0.36, 0.30),
            (0.42, 0.65), (0.48, 0.15), (0.54, 0.70), (0.60, 0.35),
            (0.66, 0.60), (0.72, 0.20), (0.78, 0.65), (0.84, 0.40),
            (0.90, 0.55), (0.96, 0.30), (1.00, 0.50)]]
    cv.polyline(pts, color, 2)


# ---------------------------------------------------------------- PNG encode
def chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def encode_png(cv):
    raw = bytearray()
    rowlen = W * 3
    for y in range(H):
        raw.append(0)
        raw += cv.px[y * rowlen:(y + 1) * rowlen]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


# ---------------------------------------------------------------- build
def field(cv, x, y, label, value, label_c=GREY, value_c=INK, vscale=2.0):
    cv.text(x, y, label, 1.5, label_c)
    cv.text(x, y + 13, value, vscale, value_c, bold=True)


def build():
    cv = Canvas(W, H, NAVY)
    # gold keyline around the spread
    cv.rect_outline(44, 44, 936, 936, GOLD, 2)
    # the open book: two cream pages
    cv.fill_rect(48, 48, 928, 928, PAPER)
    cv.fill_rect(512, 48, 464, 928, PAPER2)
    # page inner rules
    cv.rect_outline(58, 58, 444, 908, RULE, 1)
    cv.rect_outline(522, 58, 444, 908, RULE, 1)
    # spine shadow + line
    cv.fill_rect(504, 48, 8, 928, (226, 216, 186))
    cv.fill_rect(512, 48, 8, 928, (226, 216, 186))
    cv.line(512, 48, 512, 976, SPINE, 2)

    # ================= LEFT PAGE: data page =================
    draw_emblem(cv, 280, 100)
    cv.text(280, 140, "REPUBLIC OF ZALORIA", 3.0, INK, align='c', bold=True)
    cv.text(280, 172, "PASSPORT", 4.0, BURG, align='c', bold=True, spacing=6.0)
    cv.text(280, 210, "ZALORIAN - ENGLISH", 1.5, GREY, align='c')
    cv.line(96, 230, 464, 230, RULE, 1)

    # portrait
    draw_portrait(cv, 76, 246, 216, 406)

    # fields beside the portrait
    field(cv, 232, 250, "TYPE", "P")
    field(cv, 232, 292, "CODE", "ZLO")
    field(cv, 232, 334, "PASSPORT NO.", "ZL 0048217")
    field(cv, 232, 376, "NATIONALITY", "ZALORIAN")

    # fields below the portrait
    field(cv, 76, 424, "SURNAME", "VOSS")
    field(cv, 76, 462, "GIVEN NAMES", "ELENA MARA")
    field(cv, 76, 500, "DATE OF BIRTH", "12 JUN 1994")
    field(cv, 330, 500, "SEX", "F")
    field(cv, 76, 538, "PLACE OF BIRTH", "PORT MERIDIAN")
    field(cv, 76, 576, "DATE OF ISSUE", "14 MAR 2023")
    field(cv, 330, 576, "DATE OF EXPIRY", "14 MAR 2033")
    field(cv, 76, 614, "AUTHORITY", "MINISTRY OF THE INTERIOR")

    # holder signature
    signature(cv, 76, 668, 200, INK)
    cv.line(76, 690, 276, 690, INK, 1)
    cv.text(76, 696, "HOLDER'S SIGNATURE", 1.5, GREY)

    # machine-readable zone
    cv.line(76, 730, 484, 730, RULE, 1)
    mrz1, mrz2 = build_mrz()
    cv.text(280, 746, mrz1, 1.5, INK, align='c')
    cv.text(280, 778, mrz2, 1.5, INK, align='c')

    # property note
    cv.text(280, 826, "THIS PASSPORT IS THE PROPERTY OF", 1.5, GREY, align='c')
    cv.text(280, 846, "THE REPUBLIC OF ZALORIA", 1.5, GREY, align='c')
    cv.text(280, 872, "LOST OR FOUND PASSPORTS MUST BE", 1.5, GREY, align='c')
    cv.text(280, 892, "RETURNED TO THE NEAREST CONSULATE", 1.5, GREY, align='c')
    cv.text(280, 938, "2", 1.5, GREY, align='c')

    # ================= RIGHT PAGE: visas and stamps =================
    cv.text(744, 76, "VISAS", 3.0, INK, align='c', bold=True)
    cv.text(744, 106, "ENDORSEMENTS - ENTRY AND EXIT STAMPS", 1.5, GREY, align='c')
    cv.line(560, 128, 928, 128, RULE, 1)

    # --- visa sticker: Kestrel Republic ---
    vx0, vy0, vx1, vy1 = 540, 142, 948, 282
    cv.fill_rect(vx0, vy0, vx1 - vx0, vy1 - vy0, CREAM2)
    cv.rect_outline(vx0, vy0, vx1 - vx0, vy1 - vy0, TEAL, 3)
    cv.rect_outline(vx0 + 6, vy0 + 6, vx1 - vx0 - 12, vy1 - vy0 - 12, TEAL, 1)
    cv.fill_rect(vx0, vy0, vx1 - vx0, 30, TEAL)
    cv.text(744, vy0 + 5, "VISA", 3.0, WHITE, align='c', bold=True, spacing=4.0)
    cv.text(744, vy0 + 40, "KESTREL REPUBLIC", 2.0, BURG, align='c', bold=True)
    cv.text(744, vy0 + 64, "SINGLE ENTRY - 30 DAYS", 1.5, INK, align='c')
    cv.text(744, vy0 + 86, "VALID 02 JUN 2023 TO 01 JUL 2023", 1.5, INK, align='c')
    cv.text(744, vy0 + 100, "FEE 40 TALERS PAID", 2.0, BURG, align='c', bold=True)
    cv.text(928, vy0 + 122, "No. KV-1187", 1.5, GREY, align='r')

    # --- stamps, chronological, all after issue 14 MAR 2023 ---
    stamp_oval(cv, 644, 378, 96, 62, -7, STAMP_BLUE,
               ["KESTREL REPUBLIC", "ENTRY", "02 JUN 2023", "HALDOR GATE"])
    stamp_oval(cv, 844, 378, 96, 62, 5, STAMP_BLUE,
               ["KESTREL REPUBLIC", "EXIT", "18 JUN 2023", "HALDOR GATE"])
    stamp_round(cv, 644, 548, 80, -4, BURG,
                ["UNITED PROVINCES", "OF TARN", "ENTRY", "05 SEP 2024"], scale=1.3)
    stamp_round(cv, 844, 548, 80, 8, BURG,
                ["UNITED PROVINCES", "OF TARN", "EXIT", "21 SEP 2024"], scale=1.3)
    stamp_rect(cv, 644, 718, 196, 112, -6, STAMP_GREEN,
               ["FREE STATE", "OF VELMAR", "ENTRY", "11 FEB 2026"])
    # signature block, right page bottom right
    signature(cv, 764, 668, 170, INK)
    cv.line(764, 690, 934, 690, INK, 1)
    cv.text(764, 696, "HOLDER'S SIGNATURE", 1.5, GREY)
    cv.text(764, 722, "PASSPORT NO. ZL 0048217", 1.5, INK, bold=True)

    # exit stamp for the last trip, under the Velmar entry
    stamp_rect(cv, 744, 830, 220, 76, 4, STAMP_GREEN,
               ["VELMAR", "EXIT 02 MAR 2026"], scale=1.5)

    cv.text(744, 938, "3", 1.5, GREY, align='c')
    return cv


def main():
    cv = build()
    data = encode_png(cv)
    os.makedirs("/output", exist_ok=True)
    with open("/output/entry.png", "wb") as f:
        f.write(data)
    print("wrote /output/entry.png", len(data), "bytes")


if __name__ == "__main__":
    main()
