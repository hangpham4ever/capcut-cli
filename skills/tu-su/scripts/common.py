"""Shared helpers for the tự sự (narrative tribute) pipeline: fonts, gold text, compositing, framing."""
import json, os, subprocess, urllib.request, re
import numpy as np, cv2
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter

FONT_DIR = os.path.expanduser(os.environ.get("TUSU_FONTS", "~/.cache/tu-su/fonts"))
FONTS = {  # file name -> Google Fonts css family spec (latin + vietnamese subsets in one TTF)
    "Oswald-Bold.ttf": "Oswald:700",
    "Playfair-Medium.ttf": "Playfair+Display:500",
    "Playfair-SemiBoldItalic.ttf": "Playfair+Display:600i",
}

def ensure_fonts():
    os.makedirs(FONT_DIR, exist_ok=True)
    for name, fam in FONTS.items():
        dst = os.path.join(FONT_DIR, name)
        if os.path.exists(dst) and os.path.getsize(dst) > 10000:
            continue
        req = urllib.request.Request(f"https://fonts.googleapis.com/css?family={fam}&subset=latin,vietnamese",
                                     headers={"User-Agent": "Mozilla/4.0"})  # old UA -> plain TTF urls
        css = urllib.request.urlopen(req).read().decode()
        url = re.search(r"url\((https://[^)]+)\)", css).group(1)
        urllib.request.urlretrieve(url, dst)
    return FONT_DIR

def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)

def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def load_config(path):
    """Load project.json and chdir next to it, so relative media paths in the config just work."""
    cfg = load_json(path)
    os.chdir(os.path.dirname(os.path.abspath(path)))
    return cfg

def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)

def media_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout
    return float(out)

# ---------------- text ----------------
def gold_grad(h):
    stops = [(0, (255, 250, 220)), (.45, (255, 215, 90)), (.75, (240, 175, 45)), (1, (190, 125, 20))]
    ys = np.linspace(0, 1, h)
    return np.stack([np.interp(ys, [q[0] for q in stops], [q[1][i] for q in stops]) for i in range(3)], -1)

def render_text(txt, fnt, gold, ref=None):
    """RGBA image of one text line. gold=True -> gradient gold with dark stroke + warm glow;
    otherwise warm-white with soft shadow. `ref` fixes canvas size/left edge (for typewriter reveals)."""
    ref = ref or txt
    stroke = max(3, fnt.size // 26) if gold else 2
    bb = fnt.getbbox(ref, stroke_width=stroke); pad = 40
    w, h = bb[2] - bb[0] + pad * 2, bb[3] - bb[1] + pad * 2
    ox, oy = pad - bb[0], pad - bb[1]
    mf = Image.new("L", (w, h)); ImageDraw.Draw(mf).text((ox, oy), txt, font=fnt, fill=255)
    ms = Image.new("L", (w, h)); ImageDraw.Draw(ms).text((ox, oy), txt, font=fnt, fill=255, stroke_width=stroke, stroke_fill=255)
    out = np.zeros((h, w, 4), np.float32)
    if gold:
        out[..., :3] = np.array([255, 190, 60], np.float32)
        out[..., 3] = np.array(ms.filter(ImageFilter.GaussianBlur(16)), np.float32) * 0.5
    sa = np.roll(np.array(ms.filter(ImageFilter.GaussianBlur(7)), np.float32), 5, 0) / 255 * 0.8
    out[..., :3] *= (1 - sa[..., None]); out[..., 3] = np.maximum(out[..., 3], sa * 255)
    st = np.array(ms, np.float32)[..., None] / 255
    out[..., :3] = out[..., :3] * (1 - st) + np.array([40, 22, 0] if gold else [0, 0, 0], np.float32) * st
    out[..., 3] = np.maximum(out[..., 3], st[..., 0] * 255)
    fa = np.array(mf, np.float32)[..., None] / 255
    if gold:
        gy0, gy1 = oy + fnt.getbbox(ref)[1], oy + fnt.getbbox(ref)[3]
        fill = np.zeros((h, w, 3), np.float32); g = gold_grad(max(1, gy1 - gy0))
        fill[:gy0] = g[0]; fill[gy0:gy1] = g[:, None, :]; fill[gy1:] = g[-1]
    else:
        fill = np.array([255, 250, 238], np.float32)
    out[..., :3] = out[..., :3] * (1 - fa) + fill * fa
    out[..., 3] = np.maximum(out[..., 3], fa[..., 0] * 255)
    return np.clip(out, 0, 255).astype(np.uint8)

def gold_lines(txt, size, maxw=980):
    """Fit a gold keyword in maxw; shrink a little, else split in two (prefer after ',' or '·')."""
    f = lambda s: font("Oswald-Bold.ttf", s)
    s = size
    while s > size * 0.66 and f(s).getlength(txt) > maxw - 80: s -= 4
    if f(s).getlength(txt) <= maxw - 80:
        return [render_text(txt, f(s), True)]
    best = None
    for sep in (",", "·"):
        if sep in txt:
            k = txt.index(sep)
            best = (0, txt[:k + (1 if sep == "," else 0)].strip(), txt[k + 1:].strip()); break
    if best is None:
        ws = txt.split()
        for i in range(1, len(ws)):
            a, b = " ".join(ws[:i]), " ".join(ws[i:]); m = max(f(size).getlength(a), f(size).getlength(b))
            if best is None or m < best[0]: best = (m, a, b)
    out = []
    for part in best[1:]:
        s = size
        while f(s).getlength(part) > maxw - 80: s -= 4
        out.append(render_text(part, f(s), True))
    return out

def stack(imgs, gap):
    w = max(i.shape[1] for i in imgs); h = sum(i.shape[0] for i in imgs) + gap * (len(imgs) - 1)
    o = np.zeros((h, w, 4), np.uint8); y = 0
    for i in imgs:
        x = (w - i.shape[1]) // 2; sub = o[y:y + i.shape[0], x:x + i.shape[1]]
        a = i[..., 3:4].astype(np.float32) / 255
        sub[..., :3] = (sub[..., :3] * (1 - a) + i[..., :3] * a).astype(np.uint8)
        sub[..., 3] = np.maximum(sub[..., 3], i[..., 3])
        y += i.shape[0] + gap
    return o

def paste(dst, rgba, cx, cy, alpha=1.0):
    """Alpha-composite rgba centred at (cx, cy)."""
    H, W = dst.shape[:2]; h, w = rgba.shape[:2]; x, y = int(cx - w / 2), int(cy - h / 2)
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if x1 <= x0 or y1 <= y0 or alpha <= 0: return
    sub = rgba[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float32); a = sub[..., 3:4] / 255 * alpha
    d = dst[y0:y1, x0:x1].astype(np.float32)
    dst[y0:y1, x0:x1] = (d * (1 - a) + sub[..., :3] * a).astype(np.uint8)

# ---------------- framing ----------------
def kb(src, W, H, z, cx, cy):
    """Cover-crop `src` to W x H at zoom z, centred on normalized (cx, cy). Ken Burns building block."""
    h, w = src.shape[:2]
    s = max(W / w, H / h) * z
    vw, vh = W / s, H / s
    x0 = min(max(cx * w - vw / 2, 0), w - vw); y0 = min(max(cy * h - vh / 2, 0), h - vh)
    M = np.float32([[s, 0, -x0 * s], [0, s, -y0 * s]])
    return cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_AREA if s < 0.7 else cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REFLECT)

def load_image(path, W, H, headroom=2.1):
    try:
        import pillow_heif; pillow_heif.register_heif_opener()
    except ImportError:
        pass
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    w, h = im.size; s = max(W / w, H / h) * headroom
    if s < 1: im = im.resize((int(w * s), int(h * s)), Image.LANCZOS)
    return np.array(im)

def load_video(path, W, H, fps, start, dur):
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-t", f"{dur:.3f}", "-i", path, "-vf",
                        f"fps={fps},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True)
    n = len(p.stdout) // (W * H * 3)
    return np.frombuffer(p.stdout, np.uint8)[: n * W * H * 3].reshape(n, H, W, 3)

def grade_maps(W, H):
    yy, xx = np.mgrid[0:H, 0:W]
    vig = np.clip(1 - 0.34 * (((xx - W / 2) / (W / 1.25)) ** 2 + ((yy - H / 2) / (H / 1.25)) ** 2), 0.55, 1)
    bot = 1 - 0.42 * np.clip((yy / H - 0.58) / 0.32, 0, 1)
    return yy, xx, (vig * bot)[..., None].astype(np.float32), np.array([1.05, 1.0, 0.9], np.float32)
