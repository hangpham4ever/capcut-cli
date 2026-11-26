"""Render the full tự sự video from project.json: quote intro -> narration-driven shots with rich transitions,
gold-dust overlay, film grain, two-tier captions with ornaments, ambient pad (or your music) ducked under the voice.

usage: python3 -I render_story.py project.json OUT.mp4            # full render
       python3 -I render_story.py project.json PREVIEW_DIR 12 40 88  # stills at those seconds (check framing!)

project.json keys used here (see examples/su-phu-gia-roi.json):
  size, fps
  intro_dir            folder written by quote_intro.py (intro.mp4 + intro_audio.wav); omit for no intro
  intro_len            seconds of intro used before the first story shot (cut point)
  vo                   {"wav": clean narration, "chunks": transcribe_chunks.py json of that wav, "start": global s}
  shots                list, in order:
     {"vo":[a,b] | "t":[a,b] | "vo":[a,"end"],  "img": path | "vid": path, "ss": src start for vid,
      "z":[z0,z1], "c":[[cx0,cy0],[cx1,cy1]], "tr":[kind, seconds], "ghost":[img_path, strength]}
     transition kinds: fade, dip, leak, brush, iris, whip, dx (double exposure), cut
  captions             one [white_lead, GOLD_KEY] per narration chunk ("" to omit a line; "*GOLD" = big quote card)
  logo                 end-card image (shown on black after the last shot)
  music                optional audio file; default = soft synthesized pad
"""
import sys, os, subprocess, numpy as np, cv2, soundfile as sf
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

OUT = os.path.abspath(sys.argv[2]); PREVIEW = sys.argv[3:]; cfg = load_config(sys.argv[1])
ensure_fonts()
W, H = cfg.get("size", [1080, 1440]); FPS = cfg.get("fps", 30); SR = 48000
VO = cfg["vo"]; VO0 = float(VO["start"])
chunks = load_json(VO["chunks"])
ch = [(c["s"], c["e"]) for c in chunks][: len(cfg["captions"])]
G = lambda vt: VO0 + vt
END_VO = ch[-1][1]; TAIL = cfg.get("tail", 4.2); TOTAL = G(END_VO) + TAIL
INTRO_DIR = cfg.get("intro_dir"); INTRO_LEN = cfg.get("intro_len", 0.0) if INTRO_DIR else 0.0

# ---------- shot table ----------
SHOTS = []
if INTRO_DIR:
    SHOTS.append(dict(st=0.0, en=INTRO_LEN, kind="intro", tr=None))
for s in cfg["shots"]:
    if "t" in s: a, b = s["t"]
    else:
        a, b = s["vo"]; a = G(a); b = G(END_VO) + 1.2 if b == "end" else G(b)
    d = dict(st=a, en=b, z=s.get("z", [1.0, 1.08]), c=s.get("c", [[.5, .5], [.5, .5]]), tr=s.get("tr", ["fade", .6]),
             ghost=s.get("ghost"))
    if "vid" in s: d.update(kind="vid", src=(s["vid"], float(s.get("ss", 0))))
    else: d.update(kind="img", src=s["img"])
    SHOTS.append(d)
if cfg.get("logo"):
    SHOTS.append(dict(st=SHOTS[-1]["en"], en=TOTAL, kind="logo", src=cfg["logo"], z=[1.0, 1.05],
                      c=[[.5, .5], [.5, .5]], tr=["dip", 1.2], ghost=None))
SHOTS[-1]["en"] = max(SHOTS[-1]["en"], TOTAL)

yy, xx, SHADE, WARM = grade_maps(W, H)
cache = {}; intro_frames = None

def load_logo(path):
    lg = Image.open(path).convert("RGB"); lg.thumbnail((int(W * .7), int(H * .62)), Image.LANCZOS)
    cv = Image.new("RGB", (W, H)); cv.paste(lg, ((W - lg.width) // 2, (H - lg.height) // 2 - 80))
    return np.array(cv)

def shot_frame(i, t):
    global intro_frames
    S = SHOTS[i]
    if S["kind"] == "intro":
        if intro_frames is None:
            r = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(INTRO_DIR, "intro.mp4"), "-f", "rawvideo",
                                "-pix_fmt", "rgb24", "-"], capture_output=True, check=True)
            n = len(r.stdout) // (W * H * 3); intro_frames = np.frombuffer(r.stdout, np.uint8)[: n * W * H * 3].reshape(n, H, W, 3)
        return intro_frames[min(int(t * FPS), len(intro_frames) - 1)].copy(), True
    p = ease((t - S["st"]) / max(S["en"] - S["st"], 1e-3))
    z = S["z"][0] + (S["z"][1] - S["z"][0]) * p
    cx = S["c"][0][0] + (S["c"][1][0] - S["c"][0][0]) * p; cy = S["c"][0][1] + (S["c"][1][1] - S["c"][0][1]) * p
    if S["kind"] == "vid":
        path, s0 = S["src"]
        if (path, s0) not in cache:
            dur = S["en"] - S["st"] + 1.5
            rate = min(1.0, (media_duration(path) - s0) / dur)          # slow-mo if the clip is short
            cache[(path, s0)] = (load_video(path, W, H, FPS, s0, dur * rate + 0.3), rate)
        fr, rate = cache[(path, s0)]
        k = min(max(int((t - S["st"]) * rate * FPS), 0), len(fr) - 1)
        return kb(fr[k], W, H, z, cx, cy), False
    if S["kind"] == "logo":
        if S["src"] not in cache: cache[S["src"]] = load_logo(S["src"])
        return kb(cache[S["src"]], W, H, z, cx, cy), True
    if S["src"] not in cache: cache[S["src"]] = load_image(S["src"], W, H)
    return kb(cache[S["src"]], W, H, z, cx, cy), False

def graded(i, t):
    fr, done = shot_frame(i, t)
    return fr if done else np.clip(fr.astype(np.float32) * WARM * SHADE, 0, 255).astype(np.uint8)

# ================= graphics =================
RNG = np.random.default_rng(11)
_nz = cv2.resize(RNG.random((24, 18)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
_nz2 = cv2.resize(cv2.GaussianBlur(RNG.random((H // 4, W // 4)).astype(np.float32), (0, 0), 1.2), (W, H))
BRUSH_FIELD = (xx / W) * 0.75 + (yy / H) * 0.25 + (_nz - .5) * 0.35 + (_nz2 - .5) * 0.12
RR = np.sqrt((xx - W / 2) ** 2 + (yy - H * 0.45) ** 2).astype(np.float32); RMAX = float(RR.max())
GOLD = np.array([255, 205, 110], np.float32)
LEAK = None

def brush_mask(a):
    thr = -0.25 + a * 1.55
    return (np.clip((thr - BRUSH_FIELD) / 0.035, 0, 1)[..., None].astype(np.float32),
            np.clip(1 - np.abs(thr - BRUSH_FIELD) / 0.03, 0, 1)[..., None].astype(np.float32))

def iris_mask(a):
    r = ease(a) * RMAX * 1.05
    return np.clip((r - RR) / 30, 0, 1)[..., None], np.clip(1 - np.abs(r - RR) / 14, 0, 1)[..., None]

def light_leak(fr, a):
    global LEAK
    if LEAK is None:
        g1 = np.exp(-(((xx - W * 0.85) / (W * 0.45)) ** 2 + ((yy - H * 0.2) / (H * 0.5)) ** 2))
        g2 = np.exp(-(((xx - W * 0.1) / (W * 0.35)) ** 2 + ((yy - H * 0.85) / (H * 0.4)) ** 2))
        LEAK = np.stack([g1 * 255 + g2 * 230, g1 * 170 + g2 * 120, g1 * 70 + g2 * 60], -1).astype(np.float32)
    return np.clip(255 - (255 - fr.astype(np.float32)) * (1 - LEAK * a / 255), 0, 255).astype(np.uint8)

def zoom_blur(fr, amt):
    if amt < 0.02: return fr
    acc = fr.astype(np.float32).copy()
    for k in range(1, 6):
        M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, 1 + amt * 0.06 * k)
        acc += cv2.warpAffine(fr, M, (W, H), borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    return (acc / 6).astype(np.uint8)

def screen(a, b, k):
    return np.clip(255 - (255 - a.astype(np.float32)) * (255 - b.astype(np.float32) * k) / 255, 0, 255).astype(np.uint8)

NP = 46
P_X = RNG.uniform(0, W, NP); P_Y0 = RNG.uniform(0, H, NP); P_V = RNG.uniform(12, 38, NP)
P_R = RNG.uniform(3, 11, NP); P_PH = RNG.uniform(0, 6.28, NP); P_A = RNG.uniform(0.25, 0.7, NP)
SPR = {}
def sprite(r):
    r = int(r)
    if r not in SPR:
        s_ = r * 4 + 1; g_ = np.mgrid[0:s_, 0:s_] - s_ // 2; d = np.sqrt(g_[0] ** 2 + g_[1] ** 2)
        SPR[r] = (np.exp(-(d / r) ** 2) * 0.9 + np.exp(-(d / (r * .35)) ** 2) * 0.6).astype(np.float32)
    return SPR[r]

def dust(fr, t, strength):
    f = fr.astype(np.float32)
    for k in range(NP):
        y = (P_Y0[k] - P_V[k] * t) % (H + 60) - 30; x = P_X[k] + 18 * np.sin(t * 0.5 + P_PH[k])
        a = P_A[k] * (0.6 + 0.4 * np.sin(t * 1.7 + P_PH[k])) * strength
        sp = sprite(P_R[k]); h_ = sp.shape[0] // 2; x0, y0 = int(x) - h_, int(y) - h_
        if x0 < 0 or y0 < 0 or x0 + sp.shape[1] > W or y0 + sp.shape[0] > H: continue
        f[y0:y0 + sp.shape[0], x0:x0 + sp.shape[1]] += sp[..., None] * GOLD * a * 0.55
    return np.clip(f, 0, 255).astype(np.uint8)

GRAIN = [(RNG.standard_normal((H // 2, W // 2)) * 5).astype(np.float32) for _ in range(6)]
def grain(fr, n):
    return np.clip(fr.astype(np.float32) + cv2.resize(GRAIN[n % 6], (W, H), interpolation=cv2.INTER_NEAREST)[..., None], 0, 255).astype(np.uint8)

def ornament(fr, cx, cy, half, a):
    if a <= 0.01: return
    L = int(half * ease(a)); col = tuple(int(c) for c in GOLD); ov = fr.copy()
    cv2.line(ov, (cx - L, cy), (cx - 16, cy), col, 2, cv2.LINE_AA); cv2.line(ov, (cx + 16, cy), (cx + L, cy), col, 2, cv2.LINE_AA)
    cv2.fillConvexPoly(ov, np.array([[cx, cy - 9], [cx + 9, cy], [cx, cy + 9], [cx - 9, cy]], np.int32), col, cv2.LINE_AA)
    for sx in (-1, 1): cv2.circle(ov, (cx + sx * L, cy), 3, col, -1, cv2.LINE_AA)
    cv2.addWeighted(ov, min(1, a) * 0.9, fr, 1 - min(1, a) * 0.9, 0, dst=fr)

def shine(img, p):
    if p <= 0 or p >= 1: return img
    h_, w_ = img.shape[:2]
    band = (np.arange(w_)[None, :] + np.arange(h_)[:, None] * 0.6) / (w_ + h_ * 0.6)
    k = np.exp(-((band - (p * 1.4 - 0.2)) / 0.06) ** 2)[..., None]
    out = img.astype(np.float32); out[..., :3] = np.clip(out[..., :3] + k * 120, 0, 255)
    return out.astype(np.uint8)

# ================= captions =================
CAP_Y = int(H * 0.82)
caps = []
for i, ((a, b), (wt, gt)) in enumerate(zip(ch, cfg["captions"])):
    st = G(a) - 0.05
    nxt = G(ch[i + 1][0]) if i + 1 < len(ch) else G(b) + 1.6
    en = nxt - 0.08 if nxt - G(b) < 1.1 else G(b) + 0.6
    big = gt.startswith("*"); gt = gt.lstrip("*")
    if big:
        wl = render_text(wt, font("Playfair-SemiBoldItalic.ttf", 64), False) if wt else None
        gl = stack(gold_lines(gt, 170, W - 80), -55)
    else:
        wl = render_text(wt, font("Playfair-SemiBoldItalic.ttf", 56 if gt else 62), False) if wt else None
        gl = stack(gold_lines(gt, 104, W - 100), -45) if gt else None
    caps.append(dict(st=st, en=en, wl=wl, gl=gl, big=big))

def draw_caps(fr, t):
    for c in caps:
        if not (c["st"] <= t < c["en"]): continue
        fin = min(1, (t - c["st"]) / 0.35); fout = 1 if t < c["en"] - 0.28 else max(0, (c["en"] - t) / 0.28)
        a = ease(fin) * fout; rise = int(18 * (1 - ease(fin)))
        if c["big"]:
            gl = c["gl"]; cy = H // 2 + 40
            pb = ease(min(1, (t - c["st"]) / 0.55)) * fout; hb = gl.shape[0] // 2 + 70; edge = (_nz - .5) * 60
            m = (np.clip((hb + edge - np.abs(yy - (cy + 20))) / 25, 0, 1) * np.clip((pb * W * 1.25 - xx + edge * 2) / 40, 0, 1))[..., None]
            fr[:] = (fr.astype(np.float32) * (1 - 0.62 * m) + np.array([30, 18, 5], np.float32) * 0.62 * m).astype(np.uint8)
            if c["wl"] is not None: paste(fr, c["wl"], W // 2, cy - gl.shape[0] // 2 - 20 + rise, a)
            ga = ease(min(1, max(0, (t - c["st"] - 0.25) / 0.5))) * fout
            sc = 1.12 - 0.12 * ease(min(1, max(0, (t - c["st"] - 0.25) / 0.6)))
            g2 = cv2.resize(gl, None, fx=sc, fy=sc) if abs(sc - 1) > 1e-3 else gl
            paste(fr, shine(g2, (t - c["st"] - 0.6) / 0.9), W // 2, cy + 40, ga)
            ornament(fr, W // 2, cy + 40 + gl.shape[0] // 2 - 10, min(420, gl.shape[1] // 2), ease(min(1, max(0, (t - c["st"] - 0.5) / 0.7))) * fout)
        else:
            wl, gl = c["wl"], c["gl"]
            hw = wl.shape[0] - 40 if wl is not None else 0; hg = gl.shape[0] - 40 if gl is not None else 0
            top = CAP_Y - (hw + hg) // 2
            if wl is not None: paste(fr, wl, W // 2, top + hw // 2 + rise, a)
            if gl is not None:
                ga = ease(min(1, max(0, (t - c["st"] - 0.15) / 0.4))) * fout
                gy = top + hw + hg // 2 - (6 if wl is not None else 0) + int(22 * (1 - ga))
                paste(fr, shine(gl, (t - c["st"] - 0.45) / 0.8), W // 2, gy, ga)
                ornament(fr, W // 2, gy + gl.shape[0] // 2 - 16, min(360, gl.shape[1] // 2 - 20), ease(min(1, max(0, (t - c["st"] - 0.4) / 0.6))) * fout)
            elif wl is not None:
                ornament(fr, W // 2, top + hw - 4, 140, ease(min(1, max(0, (t - c["st"] - 0.3) / 0.6))) * fout)

def shot_at(t):
    return next((k for k, s in enumerate(SHOTS) if s["st"] <= t < s["en"]), len(SHOTS) - 1)

def compose(t, n=0):
    i = shot_at(t); S = SHOTS[i]; fr = graded(i, t); tr = S["tr"]
    if i > 0 and tr and tr[0] != "cut" and t - S["st"] < tr[1]:
        kind, d = tr; a = (t - S["st"]) / d; prev = graded(i - 1, t)
        if kind == "dip":
            fr = (prev.astype(np.float32) * (1 - a * 2)).astype(np.uint8) if a < 0.5 else (fr.astype(np.float32) * ((a - .5) * 2)).astype(np.uint8)
        elif kind == "brush":
            m, e = brush_mask(ease(a)); fr = np.clip(prev * (1 - m) + fr * m + e * GOLD * 0.9, 0, 255).astype(np.uint8)
        elif kind == "iris":
            m, r = iris_mask(a); fr = np.clip(prev * (1 - m) + fr * m + r * GOLD * 0.8, 0, 255).astype(np.uint8)
        elif kind == "whip":
            b = np.sin(np.pi * a)
            fr = light_leak(cv2.addWeighted(zoom_blur(prev, b * 2.2), 1 - ease(a), zoom_blur(fr, b * 2.2), ease(a), 0), b * 0.5)
        elif kind == "dx":
            fr = screen(fr, prev, 0.55 * (1 - ease(a)))
        else:
            fr = cv2.addWeighted(prev, 1 - ease(a), fr, ease(a), 0)
            if kind == "leak": fr = light_leak(fr, np.sin(np.pi * a) * 0.85)
    if S.get("ghost"):
        gp, gk = S["ghost"]
        if gp not in cache: cache[gp] = load_image(gp, W, H)
        pp = ease((t - S["st"]) / (S["en"] - S["st"]))
        fr = screen(fr, kb(cache[gp], W, H, 1.3 + 0.1 * pp, .6, .3), gk)
    if t > INTRO_LEN - 1.5: fr = dust(fr, t, 1.3 if S["kind"] == "logo" else 0.8)
    draw_caps(fr, t)
    fr = grain(fr, n)
    if t > TOTAL - 1.0: fr = (fr.astype(np.float32) * max(0, (TOTAL - t) / 1.0)).astype(np.uint8)
    return fr

def free_for(t):
    i = shot_at(t)
    need = set()
    for s in SHOTS[max(0, i - 1):i + 1]:
        if s["kind"] in ("vid",): need.add(s["src"])
        elif s["kind"] in ("img", "logo"): need.add(s["src"])
        if s.get("ghost"): need.add(s["ghost"][0])
    for k in list(cache):
        if k not in need: del cache[k]

# ================= audio =================
def build_audio(path):
    N = int(TOTAL * SR); mix = np.zeros(N); tt = np.arange(N) / SR
    if INTRO_DIR:
        ia, _ = sf.read(os.path.join(INTRO_DIR, "intro_audio.wav"))
        ia = ia[: int(min(len(ia) / SR, VO0 + 0.4) * SR)]; f = int(0.8 * SR); ia[-f:] *= np.linspace(1, 0, f)
        mix[:len(ia)] += ia
    vo, _ = sf.read(VO["wav"])
    if vo.ndim > 1: vo = vo.mean(1)
    vo = vo[: int((END_VO + 0.4) * SR)]; o = int(VO0 * SR); mix[o:o + len(vo)] += vo * 0.95
    if cfg.get("music"):
        mp = path + ".music.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-i", cfg["music"], "-t", f"{TOTAL:.2f}",
                        "-ar", str(SR), "-ac", "1", mp], check=True)
        pad, _ = sf.read(mp); pad = np.pad(pad, (0, max(0, N - len(pad))))[:N]; pad /= np.abs(pad).max() + 1e-9
    else:
        chords = [[220.0, 261.63, 329.63, 493.88], [174.61, 220.0, 261.63, 329.63], [130.81, 196.0, 261.63, 329.63], [196.0, 246.94, 293.66, 392.0]]
        pad = np.zeros(N); L = 8.0
        for k in range(int(TOTAL / L) + 2):
            s0 = int(k * L * SR)
            if s0 >= N: break
            s1 = min(N, int((k * L + L + 3.0) * SR)); st_ = np.arange(s1 - s0) / SR
            env = np.minimum(1, st_ / 2.5) * np.clip((L + 3.0 - st_) / 3.0, 0, 1); notes = chords[k % 4]
            for fq in notes:
                for det in (-0.0015, 0.0015):
                    pad[s0:s1] += (np.sin(2 * np.pi * fq * (1 + det) * st_) + 0.25 * np.sin(2 * np.pi * fq * 2 * st_)) * env
            pad[s0:s1] += 0.6 * np.sin(2 * np.pi * notes[0] / 2 * st_) * env
        pad /= np.abs(pad).max() + 1e-9; k = int(0.03 * SR); pad = np.convolve(pad, np.ones(k) / k, "same")
    venv = np.zeros(N); venv[o:o + len(vo)] = np.abs(vo)
    venv = np.convolve(venv, np.ones(int(0.4 * SR)) / int(0.4 * SR), "same")
    duck = 1 - 0.45 * np.clip(venv / (venv.max() * 0.25 + 1e-9), 0, 1)
    fade = np.clip((tt - max(0, VO0 - 2.1)) / 3.0, 0, 1) * np.clip((TOTAL - tt) / 3.0, 0, 1)
    mix += pad * cfg.get("music_level", 0.075) * duck * fade
    sf.write(path, np.clip(mix / max(1.0, np.abs(mix).max() / 0.95), -1, 1).astype(np.float32), SR)

if PREVIEW:
    os.makedirs(OUT, exist_ok=True)
    for t in sorted(map(float, PREVIEW)):
        free_for(t); Image.fromarray(compose(t)).resize((W // 3, H // 3)).save(os.path.join(OUT, f"st_{t:07.2f}.jpg"))
    sys.exit(0)

AUD = OUT + ".audio.wav"; build_audio(AUD)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-i", AUD, "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-maxrate", "8M", "-bufsize", "16M",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
N = int(TOTAL * FPS); last = -1
for n in range(N):
    t = n / FPS; i = shot_at(t)
    if i != last: free_for(t); last = i
    enc.stdin.write(compose(t, n).tobytes())
    if n % 300 == 0: print(f"{n}/{N}", flush=True)
enc.stdin.close(); enc.wait(); os.remove(AUD); print("done", enc.returncode, f"{TOTAL:.1f}s")
