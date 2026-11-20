#!/usr/bin/env python3
"""GTA 6 meme for make.fun bounty gta6-meme-x-01.
Original PIL art + the real make.fun ghost from the press kit (mark-1024.png).
No Rockstar/GTA assets: 'GTA VI' on the TV is my own lettering (Anton font).
"""
import math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
MARK = os.path.join(HERE, "assets", "make-fun-press-kit", "mark-1024.png")
ANTON = "/home/hatch/workspace/makefun/cover-art-entry/app/fonts/Anton-Regular.ttf"
SANSB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W = H = 1200

def font(path, size):
    return ImageFont.truetype(path, size)

def vgrad(w, h, stops):
    """Vertical gradient from [(pos0to1, (r,g,b)), ...]."""
    strip = Image.new("RGB", (1, h))
    px = strip.load()
    for y in range(h):
        t = y / max(1, h - 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]; p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                f = 0 if p1 == p0 else (t - p0) / (p1 - p0)
                px[0, y] = tuple(int(c0[k] + (c1[k] - c0[k]) * f) for k in range(3))
                break
    return strip.resize((w, h))

def centered(draw, cx, y, text, fnt, fill, stroke=0, stroke_fill=(0, 0, 0)):
    draw.text((cx, y), text, font=fnt, fill=fill, anchor="ma",
              stroke_width=stroke, stroke_fill=stroke_fill)

def bone(draw, p0, p1, w=15):
    draw.line([p0, p1], fill=(10, 8, 10), width=w + 6)
    draw.line([p0, p1], fill=(245, 242, 235), width=w)

# ---------------------------------------------------------------- ghost cutout
def extract_ghost():
    mark = Image.open(MARK).convert("RGBA")
    pt = None
    for cand in [(512, 880), (200, 512), (830, 830), (512, 150)]:
        r, g, b, _ = mark.getpixel(cand)
        print("probe", cand, (r, g, b))
        if r > 150 and g < 110 and b > 90:
            pt = cand
            break
    assert pt, "no magenta disc point found"
    tmp = mark.copy()
    ImageDraw.floodfill(tmp, pt, (1, 2, 3, 255), thresh=48)
    import numpy as np
    a = np.array(tmp)
    sentinel = (a[:, :, 0] == 1) & (a[:, :, 1] == 2) & (a[:, :, 2] == 3)
    alpha = np.array(mark)[:, :, 3].copy()
    alpha[sentinel] = 0
    # the disc's black ring survives the flood fill; cut everything beyond the
    # disc's inner radius (ghost + coin stay well inside r=408 of the centre)
    yy, xx = np.mgrid[0:mark.height, 0:mark.width]
    alpha[(xx - 512) ** 2 + (yy - 512) ** 2 > 408 ** 2] = 0
    out = mark.copy()
    out.putalpha(Image.fromarray(alpha, "L"))
    # erode alpha 1px to kill the magenta fringe
    al = out.split()[3].filter(ImageFilter.MinFilter(3))
    out.putalpha(al)
    bbox = out.getbbox()
    print("ghost bbox:", bbox)
    return out.crop(bbox)

# ---------------------------------------------------------------- scene
img = vgrad(W, H, [
    (0.00, (26, 9, 51)), (0.30, (94, 24, 106)), (0.52, (178, 32, 95)),
    (0.585, (255, 94, 98)), (0.60, (255, 150, 66)),
]).convert("RGBA")
d = ImageDraw.Draw(img, "RGBA")

HORIZON = 700
# sea
sea = vgrad(W, H - HORIZON - 180, [(0, (122, 31, 92)), (1, (38, 12, 54))])
img.paste(sea, (0, HORIZON))
# sand
sand = vgrad(W, 320, [(0, (232, 176, 106)), (1, (196, 122, 58))])
img.paste(sand, (0, 880))
d = ImageDraw.Draw(img, "RGBA")
# sea sparkle streaks
for i, yy in enumerate(range(716, 866, 14)):
    half = 120 - i * 9
    d.line([(430 - half, yy), (430 + half, yy)], fill=(255, 205, 110, 130), width=4)

def palm(cx_base, top, flip=1):
    pts = []
    for t in range(21):
        f = t / 20
        pts.append((cx_base + flip * 150 * f, 900 - (900 - top) * f - 46 * f * f))
    d.line(pts, fill=(18, 8, 28), width=18)
    tx, ty = pts[-1]
    for deg in (-168, -140, -112, -84, -56, -28):
        a = math.radians(deg if flip > 0 else 180 - deg)
        frond = []
        for t in range(13):
            f = t / 12
            frond.append((tx + math.cos(a) * 128 * f,
                          ty + math.sin(a) * 60 * f + 74 * f * f))
        d.line(frond, fill=(18, 8, 28), width=9)

palm(30, 430, flip=1)
palm(1170, 420, flip=-1)

# ---------------------------------------------------------------- TV
d.rounded_rectangle([262, 430, 672, 760], radius=26, fill=(18, 14, 22), outline=(0, 0, 0), width=6)
scr = vgrad(358, 250, [(0, (10, 44, 63)), (1, (18, 92, 110))])
img.paste(scr, (288, 456))
d = ImageDraw.Draw(img, "RGBA")
centered(d, 467, 492, "GTA VI", font(ANTON, 118), (168, 243, 252), stroke=3)
centered(d, 467, 628, "OUT NOW", font(ANTON, 56), (255, 209, 102), stroke=2)
centered(d, 467, 716, "make.fun", font(SANSB, 25), (240, 240, 240))
d.polygon([(340, 760), (386, 760), (398, 808), (328, 808)], fill=(12, 10, 16))
d.polygon([(548, 760), (594, 760), (606, 808), (536, 808)], fill=(12, 10, 16))
d.ellipse([292, 796, 642, 824], fill=(0, 0, 0, 70))

# ---------------------------------------------------------------- skeleton
SX = 185  # skull centre x
d.ellipse([70, 936, 312, 984], fill=(0, 0, 0, 70))  # ground shadow
# legs
bone(d, (162, 862), (86, 926)); bone(d, (86, 926), (148, 956))
bone(d, (210, 862), (288, 924)); bone(d, (288, 924), (226, 956))
# pelvis + spine
d.ellipse([138, 836, 232, 874], fill=(245, 242, 235), outline=(10, 8, 10), width=5)
bone(d, (185, 838), (185, 748), w=13)
# ribs
for yy in (764, 788, 812):
    d.arc([128, yy - 18, 242, yy + 18], start=15, end=165, fill=(10, 8, 10), width=9)
    d.arc([128, yy - 18, 242, yy + 18], start=15, end=165, fill=(245, 242, 235), width=5)
# arms to the controller
bone(d, (168, 762), (104, 820)); bone(d, (104, 820), (166, 868))
bone(d, (202, 762), (268, 818)); bone(d, (268, 818), (206, 868))
for jx, jy in [(168, 762), (104, 820), (202, 762), (268, 818)]:
    d.ellipse([jx - 10, jy - 10, jx + 10, jy + 10], fill=(245, 242, 235), outline=(10, 8, 10), width=4)
# skull + jaw
d.rounded_rectangle([142, 688, 228, 744], radius=14, fill=(245, 242, 235), outline=(10, 8, 10), width=5)
d.ellipse([122, 592, 248, 722], fill=(245, 242, 235), outline=(10, 8, 10), width=6)
d.ellipse([147, 640, 179, 678], fill=(12, 10, 12))
d.ellipse([191, 640, 223, 678], fill=(12, 10, 12))
d.polygon([(185, 676), (173, 700), (197, 700)], fill=(12, 10, 12))
for tx in (160, 174, 188, 202, 214):
    d.line([(tx, 708), (tx, 736)], fill=(10, 8, 10), width=3)
# controller in its hands
d.rounded_rectangle([138, 852, 234, 906], radius=17, fill=(26, 30, 42), outline=(0, 0, 0), width=4)
d.line([(158, 872), (158, 890)], fill=(200, 205, 215), width=5)
d.line([(149, 881), (167, 881)], fill=(200, 205, 215), width=5)
d.ellipse([196, 866, 210, 880], fill=(255, 94, 98))
d.ellipse([212, 880, 226, 894], fill=(255, 209, 102))

# ---------------------------------------------------------------- ghost (real press-kit mark)
ghost = extract_ghost()
GH = 460
gw = int(ghost.width * GH / ghost.height)
ghost = ghost.resize((gw, GH), Image.LANCZOS)
gx0, gy0 = 1186 - gw, 1002 - GH
shadow = Image.new("RGBA", (gw, 60), (0, 0, 0, 0))
ImageDraw.Draw(shadow).ellipse([20, 8, gw - 20, 52], fill=(0, 0, 0, 90))
img.paste(shadow.filter(ImageFilter.GaussianBlur(8)), (gx0, 972), shadow.filter(ImageFilter.GaussianBlur(8)))
img.alpha_composite(ghost, (gx0, gy0))
d = ImageDraw.Draw(img, "RGBA")
# sunglasses worked onto the ghost
sx0, sy0 = gx0 + int(0.235 * gw), gy0 + int(0.235 * GH)
sx1, sy1 = gx0 + int(0.685 * gw), gy0 + int(0.415 * GH)
d.rounded_rectangle([sx0, sy0, sx1, sy1], radius=34, fill=(8, 8, 14), outline=(0, 0, 0), width=4)
d.line([(sx0 + 26, sy0 + 26), (sx0 + 96, sy0 + 26)], fill=(255, 255, 255, 130), width=9)
# controller held low-left of the ghost
cx0, cy0 = gx0 + int(0.12 * gw), gy0 + int(0.80 * GH)
cx1, cy1 = cx0 + 128, cy0 + 70
d.rounded_rectangle([cx0, cy0, cx1, cy1], radius=20, fill=(26, 30, 42), outline=(0, 0, 0), width=4)
d.line([(cx0 + 28, cy0 + 24), (cx0 + 28, cy0 + 46)], fill=(200, 205, 215), width=6)
d.line([(cx0 + 17, cy0 + 35), (cx0 + 39, cy0 + 35)], fill=(200, 205, 215), width=6)
d.ellipse([cx0 + 82, cy0 + 16, cx0 + 98, cy0 + 32], fill=(255, 94, 98))
d.ellipse([cx0 + 100, cy0 + 36, cx0 + 116, cy0 + 52], fill=(255, 209, 102))

# ---------------------------------------------------------------- captions
centered(d, 604, 40, "WAITED 13 YEARS", font(ANTON, 108), (255, 255, 255), stroke=7)
centered(d, 604, 156, "FOR GTA VI", font(ANTON, 132), (255, 255, 255), stroke=8)
d.rounded_rectangle([36, 1002, 1164, 1190], radius=24, fill=(5, 5, 10, 238))
centered(d, 600, 1018, "THE WAIT KILLED HIM.", font(ANTON, 58), (255, 255, 255))
centered(d, 600, 1096, "HE'S STILL PLAYING DAY ONE.", font(ANTON, 58), (255, 209, 102))

img = img.convert("RGB")
out = os.path.join(HERE, "meme.png")
img.save(out)
img.resize((480, 480), Image.LANCZOS).save(os.path.join(HERE, "preview-480.png"))
print("saved", out, img.size, os.path.getsize(out), "bytes; ghost pasted at", (gx0, gy0), "size", (gw, GH))
