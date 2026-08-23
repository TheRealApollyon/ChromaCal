"""Generates icon.png in this directory: a rainbow calendar+bulb mark.

Requires: pip install numpy pillow

Everything is drawn as exact vector geometry at high resolution and
downsampled with LANCZOS for anti-aliasing, so the alpha channel is
correct by construction rather than guessed at via background removal
-- see the security-review-era CLAUDE.md notes on why HACS/pre-pub
brand assets went through this route instead of an AI image export.

The bulb's gradient (hue-sweep fill, offset highlight, dark rim) is the
same recipe as the panel's own _renderOrb() in
frontend/src/chromacal-panel.ts, just parameterized by shape instead of
hardcoded to a circle, and with its shading maps blurred for a softer
"layered glass" look. Kept here as reference for future icon/mark work
so that reuse doesn't require re-deriving the gradient math from
scratch.

Two things were tried and deliberately dropped after pixel-level
testing at 48/32/24px, not kept behind a flag:
  - A folded-corner rainbow ribbon in the bottom-right corner --
    several adjacent thin diagonal stripes degraded into an
    indistinguishable colored smudge at small sizes.
  - A muted/dusty grid-square palette -- technically fine, but a
    product-identity misstep (ChromaCal's actual visual identity is
    built on vivid, saturated color).
A single-piece black outline around the bulb and a wider/rounder
bulb base, by contrast, both survived small-size testing fine --
continuous single shapes hold up under downsampling far better than
adjacent fine linework does.
"""

import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

NAVY = (30, 42, 66, 255)
WHITE = (250, 250, 252, 255)


def hsv_to_rgb(h, s, v):
    i = np.floor(h * 6.0)
    f = h * 6.0 - i
    p = v * (1.0 - s)
    q = v * (1.0 - f * s)
    t = v * (1.0 - (1.0 - f) * s)
    i = i.astype(int) % 6
    r = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5], [v, q, p, p, t, v])
    g = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5], [t, v, v, q, p, p])
    b = np.select([i == 0, i == 1, i == 2, i == 3, i == 4, i == 5], [p, p, t, v, v, q])
    return r, g, b


def gradient_field_soft(W, H, cx, cy, R, hue_offset=90):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    X = (xx - cx) / R
    Y = (yy - cy) / R
    r = np.sqrt(X ** 2 + Y ** 2)

    angle = (np.degrees(np.arctan2(Y, X)) + 360) % 360
    hue = ((angle + hue_offset) % 360) / 360.0
    sat = np.full_like(hue, 0.80)
    val = np.full_like(hue, 0.93)
    rr, gg, bb = hsv_to_rgb(hue, sat, val)
    base = np.stack([rr, gg, bb], axis=-1)

    hx, hy = -0.20, -0.35
    dh = np.sqrt((X - hx) ** 2 + (Y - hy) ** 2)
    highlight_a = np.clip(1 - dh / 0.75, 0, 1) * 0.42
    rim_a = np.clip((r - 0.45) / 0.65, 0, 1) * 0.45

    # Blur the shading maps themselves (not just the final image) for a
    # genuinely soft ambient falloff -- no hard specular edge anywhere.
    blur_px = max(1, int(R * 0.12))
    h_img = Image.fromarray((highlight_a * 255).astype(np.uint8), mode="L").filter(
        ImageFilter.GaussianBlur(radius=blur_px))
    r_img = Image.fromarray((rim_a * 255).astype(np.uint8), mode="L").filter(
        ImageFilter.GaussianBlur(radius=blur_px))
    highlight_a = np.array(h_img).astype(np.float64) / 255.0
    rim_a = np.array(r_img).astype(np.float64) / 255.0

    col = base.copy()
    white_ = np.ones_like(base)
    black_ = np.zeros_like(base)
    col = col * (1 - highlight_a[..., None]) + white_ * highlight_a[..., None]
    col = col * (1 - rim_a[..., None]) + black_ * rim_a[..., None]
    return np.clip(col, 0, 1)


def build_bulb_mask(W, H, cx, cy, R, expand=0):
    # Round dome + tapered neck + wide rounded base, as one continuous
    # silhouette (no filament, no separate base-ring lines -- that kind
    # of fine linework is exactly what didn't survive downsampling).
    # `expand` rebuilds the identical shape slightly larger, used to
    # generate a crisp black outline layer without a raster dilation.
    R2 = R + expand
    mask = Image.new("L", (W, H), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.ellipse([cx - R2, cy - R2, cx + R2, cy + R2], fill=255)
    neck_top_y = cy + R * 0.55
    neck_top_hw = R * 0.62 + expand
    neck_bottom_y = neck_top_y + 260 + expand
    neck_bottom_hw = R * 0.52 + expand
    mdraw.polygon([
        (cx - neck_top_hw, neck_top_y), (cx + neck_top_hw, neck_top_y),
        (cx + neck_bottom_hw, neck_bottom_y), (cx - neck_bottom_hw, neck_bottom_y),
    ], fill=255)
    mdraw.rounded_rectangle(
        [cx - neck_bottom_hw, neck_bottom_y - 55 - expand, cx + neck_bottom_hw, neck_bottom_y + 55 + expand],
        radius=48 + expand, fill=255,
    )
    mask = mask.filter(ImageFilter.GaussianBlur(radius=2)).point(lambda a: 255 if a > 128 else 0)
    return mask


def make_bulb(hue_offset=90, outline_stroke=22):
    W, H = 700, 920
    cx, cy, R = 350, 320, 270

    fill_mask = build_bulb_mask(W, H, cx, cy, R, expand=0)
    outline_mask = build_bulb_mask(W, H, cx, cy, R, expand=outline_stroke)

    col = gradient_field_soft(W, H, cx, cy, R, hue_offset)
    alpha = np.array(fill_mask).astype(np.float64) / 255.0
    rgba = np.concatenate([col, alpha[..., None]], axis=-1)
    shape_img = Image.fromarray((rgba * 255).astype(np.uint8), mode="RGBA")

    glow = shape_img.filter(ImageFilter.GaussianBlur(radius=W * 0.06))
    glow_alpha = glow.getchannel("A").point(lambda a: int(a * 0.7))
    glow.putalpha(glow_alpha)

    outline_rgba = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    outline_solid = Image.new("RGBA", (W, H), (10, 10, 14, 255))
    outline_solid.putalpha(outline_mask)
    outline_rgba.alpha_composite(outline_solid)

    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.alpha_composite(glow)
    out.alpha_composite(outline_rgba)
    out.alpha_composite(shape_img)
    return out


def generate():
    S = 1500
    BODY = (200, 300, 1260, 1280)
    RADIUS = 90
    OUTLINE_W = 20
    tab_w = 90

    # Card silhouette (tabs + body only) used as the drop-shadow source,
    # kept separate from the bulb so the shadow doesn't double up with
    # the bulb's own ambient glow.
    card_silhouette = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(card_silhouette)
    for cx_ in (BODY[0] + 260, BODY[2] - 260):
        tab_box = [cx_ - tab_w / 2, BODY[1] - 150, cx_ + tab_w / 2, BODY[1] + 70]
        sdraw.rounded_rectangle(tab_box, radius=tab_w / 2, fill=(0, 0, 0, 255))
    sdraw.rounded_rectangle(BODY, radius=RADIUS, fill=(0, 0, 0, 255))

    shadow = card_silhouette.filter(ImageFilter.GaussianBlur(radius=34))
    shadow_alpha = shadow.getchannel("A").point(lambda a: int(a * 0.38))
    shadow.putalpha(shadow_alpha)

    canvas = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    canvas.alpha_composite(shadow, (0, 26))
    draw = ImageDraw.Draw(canvas)

    for cx_ in (BODY[0] + 260, BODY[2] - 260):
        tab_box = [cx_ - tab_w / 2, BODY[1] - 150, cx_ + tab_w / 2, BODY[1] + 70]
        draw.rounded_rectangle(tab_box, radius=tab_w / 2, fill=(120, 128, 140, 255), outline=NAVY, width=OUTLINE_W)

    draw.rounded_rectangle(BODY, radius=RADIUS, fill=WHITE, outline=NAVY, width=OUTLINE_W)

    inset = OUTLINE_W // 2 + 6
    header_box = [BODY[0] + inset, BODY[1] + inset, BODY[2] - inset, BODY[1] + 230]
    mask = Image.new("L", (S, S), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rounded_rectangle(header_box, radius=RADIUS - inset, fill=255, corners=(True, True, False, False))

    gx = np.linspace(200, 140, S)
    grad_hue = np.tile(gx, (S, 1)) / 360.0
    grad_sat = np.full((S, S), 0.55)
    grad_val = np.full((S, S), 0.80)
    gr, gg, gb = hsv_to_rgb(grad_hue, grad_sat, grad_val)
    grad_rgb = (np.stack([gr, gg, gb], axis=-1) * 255).astype(np.uint8)
    grad_img = Image.fromarray(grad_rgb, mode="RGB").convert("RGBA")
    grad_img.putalpha(mask)
    canvas.alpha_composite(grad_img)
    draw.rounded_rectangle(header_box, radius=RADIUS - inset, outline=NAVY, width=10, corners=(True, True, False, False))

    # Vivid, fully-saturated swatches -- ChromaCal's actual visual
    # identity is built on saturated color, not a muted palette.
    swatch_hues = [0, 55, 120, 190, 250, 305]
    sat, val = 0.72, 0.88
    cols, rows = 3, 2
    grid_top = header_box[3] + 60
    grid_bottom = BODY[3] - 60
    grid_left = BODY[0] + 90
    grid_right = BODY[2] - 90
    gap = 30
    cell_w = (grid_right - grid_left - gap * (cols - 1)) / cols
    cell_h = (grid_bottom - grid_top - gap * (rows - 1)) / rows

    i = 0
    for row in range(rows):
        for col in range(cols):
            r, g, b = hsv_to_rgb(np.array([swatch_hues[i] / 360.0]), np.array([sat]), np.array([val]))
            color = (int(r[0] * 255), int(g[0] * 255), int(b[0] * 255), 255)
            x0 = grid_left + col * (cell_w + gap)
            y0 = grid_top + row * (cell_h + gap)
            draw.rounded_rectangle([x0, y0, x0 + cell_w, y0 + cell_h], radius=cell_w * 0.18, fill=color)
            i += 1

    bulb_asset = make_bulb()
    scale = 560 / bulb_asset.width
    new_w, new_h = int(bulb_asset.width * scale), int(bulb_asset.height * scale)
    bulb_scaled = bulb_asset.resize((new_w, new_h), Image.LANCZOS)
    bx = (BODY[0] + BODY[2]) / 2 - new_w / 2
    by = header_box[3] - new_h * 0.30
    canvas.alpha_composite(bulb_scaled, (int(bx), int(by)))

    bbox = canvas.getbbox()
    cropped = canvas.crop(bbox)
    w, h = cropped.size
    side = max(w, h)
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    square.paste(cropped, ((side - w) // 2, (side - h) // 2), cropped)

    return square.resize((256, 256), Image.LANCZOS)


if __name__ == "__main__":
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")
    generate().save(out_path)
    print(f"wrote {out_path}")
