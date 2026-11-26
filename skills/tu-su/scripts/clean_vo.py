"""Cut stumbles / retakes out of a narration and polish it.

Keeps every phrase except the ones you drop, pads each phrase a little, keeps a longer breath (up to 0.85 s)
where the reader paused on purpose (> 1 s), then denoise + gentle compression + loudness -16 LUFS.

usage: python3 -I clean_vo.py IN_AUDIO OUT.wav [--drop A-B ...] [--cut-after T:END ...] [--skip-before T]
  --drop A-B       drop any phrase whose midpoint is between A and B seconds (a stumble)
  --cut-after T:E  the phrase that contains time T ends at E instead (cut a doubled tail mid-phrase)
  --skip-before T  ignore everything before T (noise before the reader starts)
Then run transcribe_chunks.py on OUT.wav: its phrase list is what render_story.py uses for caption timing.
"""
import argparse, subprocess, tempfile, os
import soundfile as sf

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--drop", action="append", default=[])
ap.add_argument("--cut-after", action="append", default=[])
ap.add_argument("--skip-before", type=float, default=0.0)
ap.add_argument("--db", type=float, default=-42)
a = ap.parse_args()

tmp = tempfile.mkdtemp(); wav = os.path.join(tmp, "a16.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.src, "-ar", "16000", "-ac", "1", wav], check=True)
dur = sf.info(wav).duration
log = subprocess.run(["ffmpeg", "-i", wav, "-af", f"silencedetect=n={a.db}dB:d=0.3", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
st = [float(l.split("silence_start: ")[1].split()[0]) for l in log.splitlines() if "silence_start" in l]
en = [float(l.split("silence_end: ")[1].split()[0]) for l in log.splitlines() if "silence_end" in l]
sp, t = [], 0.0
for s, e in zip(st, en + [dur] * (len(st) - len(en))):
    if s > t: sp.append([t, s])
    t = e
if t < dur: sp.append([t, dur])
sp = [r for r in sp if r[1] - r[0] > 0.2 and r[0] >= a.skip_before]
drops = [tuple(map(float, d.split("-"))) for d in a.drop]
sp = [r for r in sp if not any(x <= (r[0] + r[1]) / 2 <= y for x, y in drops)]
for c in a.cut_after:
    T, E = map(float, c.split(":"))
    for r in sp:
        if r[0] < T < r[1]: r[1] = E

PRE, POST = 0.10, 0.30
keep = []
for i, (s, e) in enumerate(sp):
    nxt = sp[i + 1][0] if i + 1 < len(sp) else dur
    gap = nxt - e
    post = min(0.85, gap - PRE - 0.02) if gap > 1.0 else POST
    s = max(0, s - PRE); e = min(dur, e + max(post, 0.05))
    if keep and s <= keep[-1][1]: keep[-1][1] = e
    else: keep.append([s, e])
print(f"{len(keep)} pieces, {sum(e - s for s, e in keep):.2f}s")
parts, labels = [], []
for i, (s, e) in enumerate(keep):
    parts.append(f"[0:a]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={e-s-0.06:.3f}:d=0.06[p{i}]")
    labels.append(f"[p{i}]")
fc = ";".join(parts) + ";" + "".join(labels) + (f"concat=n={len(keep)}:v=0:a=1,highpass=f=80,afftdn=nr=12:nf=-50,"
     "acompressor=threshold=-22dB:ratio=2.5:attack=8:release=200:makeup=3,loudnorm=I=-16:TP=-1.5:LRA=9[out]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.src, "-filter_complex", fc, "-map", "[out]",
                "-ar", "48000", "-ac", "1", a.out], check=True)
