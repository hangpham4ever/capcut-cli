"""Opening 'quote' scene: the subject's own voice line(s), joined into one continuous sentence, over the
running source video with a slow push-in, while two-tier text types out (white italic lead + gold KEYWORD)
with a soft keyboard tick.

usage: python3 -I quote_intro.py project.json OUT_DIR
Reads cfg["intro"]:
  src        video file with the real voice
  t0         source time shown at output 0
  dur        output length (story continues the same footage after this)
  voice      [[a,b], ...] source ranges of the subject's speech, in order; anything between them (e.g. the
             camera operator talking) is left out and the pieces are crossfaded into one sentence
  beats      [["lead…", "KEYWORD"], ...] one beat per voice range
  fade_out   true -> fade to black at the end (stand-alone preview); false when the story follows
Writes OUT_DIR/intro.mp4 and OUT_DIR/intro_audio.wav (voice + typing, no music).
"""
import sys, os, subprocess, numpy as np, cv2, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

OUTD = os.path.abspath(sys.argv[2]); cfg = load_config(sys.argv[1]); os.makedirs(OUTD, exist_ok=True)
ensure_fonts()
I = cfg["intro"]; W, H = cfg.get("size", [1080, 1440]); FPS = cfg.get("fps", 30); SR = 48000
SRC, T0, DUR = I["src"], float(I["t0"]), float(I["dur"])
VOICE = I["voice"]; BEATS = I["beats"]; FADE = I.get("fade_out", False)
XF = 0.12; CPS_W, CPS_G = 16.0, 13.0
VOICE_AT = VOICE[0][0] - T0

# ---------- voice: join, denoise once (constant noise floor), level ----------
raw_p = os.path.join(OUTD, "_raw48.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-af", "highpass=f=100", "-ar", str(SR), "-ac", "1", raw_p], check=True)
raw, _ = sf.read(raw_p)
pieces = [raw[int(a * SR):int(b * SR)].copy() for a, b in VOICE]
x = int(XF * SR); tt = np.linspace(0, np.pi / 2, x)
joined = pieces[0]; seg_out = [0.0]
for p in pieces[1:]:
    seg_out.append(len(joined) / SR - XF)
    joined = np.concatenate([joined[:-x], joined[-x:] * np.cos(tt) + p[:x] * np.sin(tt), p[x:]])
f1, f2 = int(0.08 * SR), int(0.3 * SR); joined[:f1] *= np.linspace(0, 1, f1); joined[-f2:] *= np.linspace(1, 0, f2)
jp = os.path.join(OUTD, "_join.wav"); vp = os.path.join(OUTD, "_voice.wav"); sf.write(jp, joined, SR)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", jp, "-af",
                "afftdn=nr=24:nf=-45:tn=1,highpass=f=130,lowpass=f=7000,equalizer=f=2500:t=q:w=1.2:g=3,"
                "equalizer=f=250:t=q:w=1:g=-2,acompressor=threshold=-28dB:ratio=3:attack=5:release=150:makeup=8,"
                "afftdn=nr=10:nf=-50", "-ar", str(SR), vp], check=True)
voice, _ = sf.read(vp)
k = np.ones(int(0.12 * SR)) / int(0.12 * SR)
env = np.sqrt(np.convolve(voice ** 2, k, "same")) + 1e-6
g = np.clip(np.percentile(env, 85) / env, 1.0, 2.0); g = np.convolve(g, np.ones(int(0.1 * SR)) / int(0.1 * SR), "same")
voice = voice * g

# ---------- beat timing (output time) ----------
beats = []
for i, (lead, key) in enumerate(BEATS):
    tw = VOICE_AT + seg_out[i] + 0.05
    tg = tw + min(len(lead) / CPS_W, 0.5)
    beats.append((lead, key, tw, tg))
TE = DUR - 1.7

# ---------- audio: voice + soft keyboard ticks ----------
N = int(DUR * SR); mix = np.zeros(N); o = int(VOICE_AT * SR); mix[o:o + len(voice)] += voice[:N - o]
rng = np.random.default_rng(3)
def tick():
    L = int(0.018 * SR); t = np.arange(L) / SR
    nz = rng.standard_normal(L); nz = nz - np.convolve(nz, np.ones(8) / 8, "same")
    return (np.sin(2 * np.pi * rng.uniform(2600, 3600) * t) * np.exp(-t * 420) * 0.5 + nz * np.exp(-t * 600) * 0.25
            + np.sin(2 * np.pi * rng.uniform(900, 1300) * t) * np.exp(-t * 300) * 0.25)
for lead, key, tw, tg in beats:
    for kk, (txt, t0, cps) in enumerate(((lead, tw, CPS_W), (key, tg, CPS_G))):
        for j, ch in enumerate(txt):
            c = tick() * rng.uniform(0.6, 1.0) * (0.55 if ch == " " else 1.0)
            oo = int((t0 + j / cps + rng.uniform(-0.01, 0.01)) * SR)
            if 0 <= oo < N - len(c): mix[oo:oo + len(c)] += c * 0.035
if FADE: ft = int(1.5 * SR); mix[-ft:] *= np.linspace(1, 0, ft)
mix = np.clip(mix / max(1e-9, np.abs(mix).max()) * 0.9, -1, 1)
AUD = os.path.join(OUTD, "intro_audio.wav"); sf.write(AUD, mix.astype(np.float32), SR)

# ---------- video ----------
VW, VH = int(W * 1.1), int(H * 1.1)
frames = load_video(SRC, VW, VH, FPS, T0, DUR + 0.2); n = len(frames)
yy, xx = np.mgrid[0:H, 0:W]
vig = 1 - 0.38 * (((xx - W / 2) / (W / 1.25)) ** 2 + ((yy - H / 2) / (H / 1.25)) ** 2)
SHADE = (np.clip(vig, 0.5, 1) * (1 - 0.55 * np.clip((yy / H - 0.50) / 0.35, 0, 1)))[..., None].astype(np.float32)
WARM = np.array([1.06, 1.0, 0.88], np.float32)
FW = font("Playfair-SemiBoldItalic.ttf", 64)
def gfont(txt):
    s = 150
    while font("Oswald-Bold.ttf", s).getlength(txt) > W - 170: s -= 4
    return font("Oswald-Bold.ttf", s)
GF = [gfont(b[1]) for b in beats]
cache = {}
def get(key, txt, fnt, gold, ref):
    if key not in cache: cache[key] = render_text(txt, fnt, gold, ref)
    return cache[key]
heights = [(render_text(b[0], FW, False).shape[0], render_text(b[1], GF[i], True).shape[0]) for i, b in enumerate(beats)]
blocks = [hw + hg - 70 for hw, hg in heights]
tot = sum(blocks) - 60 * (len(blocks) - 1)
tops = []; y = int(H * 0.92) - tot
for b in blocks: tops.append(y); y += b - 60

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                        "-i", "-", "-i", AUD, "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac",
                        "-b:a", "192k", "-shortest", "-movflags", "+faststart", os.path.join(OUTD, "intro.mp4")], stdin=subprocess.PIPE)
for fi in range(int(DUR * FPS)):
    t = fi / FPS; z = 1.0 + 0.08 * t / DUR
    x0, y0 = (VW - W / z) / 2, (VH - H / z) / 2
    fr = cv2.warpAffine(frames[min(fi, n - 1)], np.float32([[z, 0, -x0 * z], [0, z, -y0 * z]]), (W, H))
    fr = np.clip(fr.astype(np.float32) * WARM * SHADE, 0, 255).astype(np.uint8)
    for bi, (lead, key, tw, tg) in enumerate(beats):
        if t < tw or t > TE + 0.5: continue
        a = 1.0 if t <= TE else max(0.0, 1 - (t - TE) / 0.5); lift = 0 if t <= TE else int(-40 * (t - TE) / 0.5)
        kw = max(0, min(len(lead), int((t - tw) * CPS_W) + 1))
        kg = max(0, min(len(key), int((t - tg) * CPS_G) + 1)) if t >= tg else 0
        wimg = get(("w", bi, kw), lead[:kw], FW, False, lead)
        paste(fr, wimg, W / 2, tops[bi] + lift + wimg.shape[0] / 2, a)
        if kg:
            gimg = get(("g", bi, kg), key[:kg], GF[bi], True, key)
            paste(fr, gimg, W / 2, tops[bi] + lift + wimg.shape[0] - 70 + gimg.shape[0] / 2, a)
    if FADE and t > DUR - 0.9: fr = (fr * max(0.0, (DUR - t) / 0.9)).astype(np.uint8)
    enc.stdin.write(fr.tobytes())
enc.stdin.close(); enc.wait(); print("intro done", enc.returncode)
