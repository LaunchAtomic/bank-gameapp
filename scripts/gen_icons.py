import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

BG_TOP = hex_rgb('#1d3444')
BG_MID = hex_rgb('#11212b')
BG_BOT = hex_rgb('#0a151c')
ACCENT_HI = hex_rgb('#ffbe57')
ACCENT_LO = hex_rgb('#e2952f')
INK = hex_rgb('#0e1a22')
GOLD_TEXT_TOP = hex_rgb('#ffffff')
GOLD_TEXT_BOT = hex_rgb('#ffd79a')
TEXT_DIM = hex_rgb('#9fb7c2')

def vertical_gradient(w, h, stops):
    # stops: list of (pos 0..1, rgb)
    ys = np.linspace(0, 1, h)
    img = np.zeros((h, w, 3), dtype=np.uint8)
    for y_idx, t in enumerate(ys):
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1 or i == len(stops) - 2:
                local_t = 0 if p1 == p0 else (t - p0) / (p1 - p0)
                local_t = min(max(local_t, 0), 1)
                c = tuple(int(c0[k] + (c1[k] - c0[k]) * local_t) for k in range(3))
                img[y_idx, :, :] = c
                break
    return Image.fromarray(img, 'RGB')

def diagonal_gradient(size, c0, c1):
    w = h = size
    xs, ys = np.meshgrid(np.linspace(0, 1, w), np.linspace(0, 1, h))
    t = (xs + ys) / 2.0
    img = np.zeros((h, w, 3), dtype=np.uint8)
    for k in range(3):
        img[:, :, k] = (c0[k] + (c1[k] - c0[k]) * t).astype(np.uint8)
    return Image.fromarray(img, 'RGB')

def make_icon(size, out_path, corner_radius_frac=0.0):
    bg = vertical_gradient(size, size, [(0, BG_TOP), (0.55, BG_MID), (1, BG_BOT)])
    canvas = bg.convert('RGBA')

    coin_d = int(size * 0.66)
    coin = diagonal_gradient(coin_d, ACCENT_HI, ACCENT_LO).convert('RGBA')
    mask = Image.new('L', (coin_d, coin_d), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, coin_d, coin_d), fill=255)
    coin.putalpha(mask)

    cx, cy = size // 2, size // 2
    canvas.alpha_composite(coin, (cx - coin_d // 2, cy - coin_d // 2))

    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(BOLD, int(coin_d * 0.52))
    txt = "$"
    bbox = draw.textbbox((0, 0), txt, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw / 2 - bbox[0], cy - th / 2 - bbox[1]), txt, font=font, fill=INK + (255,))

    if corner_radius_frac > 0:
        r = int(size * corner_radius_frac)
        rmask = Image.new('L', (size, size), 0)
        ImageDraw.Draw(rmask).rounded_rectangle((0, 0, size, size), radius=r, fill=255)
        out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        out.paste(canvas, (0, 0), rmask)
        canvas = out

    canvas.convert('RGB' if corner_radius_frac == 0 else 'RGBA').save(out_path)
    print('wrote', out_path, size)

def make_og_image(out_path):
    w, h = 1200, 630
    bg = vertical_gradient(w, h, [(0, BG_TOP), (0.5, BG_MID), (1, BG_BOT)])
    canvas = bg.convert('RGBA')
    draw = ImageDraw.Draw(canvas)

    coin_d = 190
    coin = diagonal_gradient(coin_d, ACCENT_HI, ACCENT_LO).convert('RGBA')
    mask = Image.new('L', (coin_d, coin_d), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, coin_d, coin_d), fill=255)
    coin.putalpha(mask)
    coin_x, coin_y = 130, 150
    canvas.alpha_composite(coin, (coin_x, coin_y))
    cf = ImageFont.truetype(BOLD, int(coin_d * 0.52))
    cbbox = draw.textbbox((0, 0), "$", font=cf)
    ctw, cth = cbbox[2] - cbbox[0], cbbox[3] - cbbox[1]
    ccx, ccy = coin_x + coin_d / 2, coin_y + coin_d / 2
    draw.text((ccx - ctw / 2 - cbbox[0], ccy - cth / 2 - cbbox[1]), "$", font=cf, fill=INK + (255,))

    word_font = ImageFont.truetype(BOLD, 150)
    word = "BANK"
    wbbox = draw.textbbox((0, 0), word, font=word_font)
    ww, wh = wbbox[2] - wbbox[0], wbbox[3] - wbbox[1]
    wx, wy = coin_x + coin_d + 40, coin_y + coin_d / 2 - wh / 2 - wbbox[1]

    text_grad = vertical_gradient(int(ww) + 20, int(wh) + 20, [(0, GOLD_TEXT_TOP), (1, GOLD_TEXT_BOT)]).convert('RGBA')
    tmask = Image.new('L', (int(ww) + 20, int(wh) + 20), 0)
    tdraw = ImageDraw.Draw(tmask)
    tdraw.text((10 - wbbox[0], 10 - wbbox[1]), word, font=word_font, fill=255)
    text_grad.putalpha(tmask)
    canvas.alpha_composite(text_grad, (int(wx) - 10, int(wy) - 10))

    tag_font = ImageFont.truetype(BOLD, 40)
    tagline = "Push your luck. Bank before you bust."
    draw.text((coin_x, coin_y + coin_d + 55), tagline, font=tag_font, fill=TEXT_DIM + (255,))

    canvas.convert('RGB').save(out_path)
    print('wrote', out_path, w, h)

import os
os.makedirs('icons', exist_ok=True)
make_icon(180, 'icons/apple-touch-icon.png')
make_icon(192, 'icons/icon-192.png')
make_icon(512, 'icons/icon-512.png')
make_icon(32, 'icons/favicon-32.png')
make_og_image('icons/og-image.png')
