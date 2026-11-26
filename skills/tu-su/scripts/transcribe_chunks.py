"""Phrase-level transcript of a voice recording (Vietnamese by default).

Whisper hallucinates ("Hãy subscribe cho kênh…") on long quiet / windy / music-backed audio. Splitting on silences
and transcribing each phrase on its own, with a vocabulary prompt, is far more reliable and also exposes retakes.

usage: python3 -I transcribe_chunks.py AUDIO OUT.json [--prompt "từ khoá, tên riêng…"] [--db -42] [--min-sil 0.3]
OUT.json: [{"s": start, "e": end, "t": text}, ...]   (times in AUDIO's timeline)
"""
import argparse, json, subprocess, tempfile, os
import numpy as np, soundfile as sf

ap = argparse.ArgumentParser()
ap.add_argument("audio"); ap.add_argument("out")
ap.add_argument("--prompt", default="")
ap.add_argument("--lang", default="vi")
ap.add_argument("--db", type=float, default=-42)
ap.add_argument("--min-sil", type=float, default=0.3)
ap.add_argument("--model", default="large-v3")
a = ap.parse_args()

tmp = tempfile.mkdtemp()
wav = os.path.join(tmp, "a16.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.audio, "-ar", "16000", "-ac", "1", wav], check=True)
log = subprocess.run(["ffmpeg", "-i", wav, "-af", f"silencedetect=n={a.db}dB:d={a.min_sil}", "-f", "null", "-"],
                     capture_output=True, text=True).stderr
starts = [float(l.split("silence_start: ")[1].split()[0]) for l in log.splitlines() if "silence_start" in l]
ends = [float(l.split("silence_end: ")[1].split()[0]) for l in log.splitlines() if "silence_end" in l]
x, sr = sf.read(wav, dtype="float32"); dur = len(x) / sr
speech, t = [], 0.0
for s, e in zip(starts, ends + [dur] * (len(starts) - len(ends))):
    if s > t: speech.append((t, s))
    t = e
if t < dur: speech.append((t, dur))
speech = [(s, e) for s, e in speech if e - s > 0.25]

from faster_whisper import WhisperModel
m = WhisperModel(a.model, device="cpu", compute_type="int8")
out = []
for s, e in speech:
    seg = x[int(max(0, s - 0.1) * sr):int(min(dur, e + 0.1) * sr)]
    segs, _ = m.transcribe(seg, language=a.lang, beam_size=5, temperature=0, condition_on_previous_text=False,
                           initial_prompt=a.prompt or None, vad_filter=False)
    txt = " ".join(z.text.strip() for z in segs)
    out.append({"s": round(s, 3), "e": round(e, 3), "t": txt})
    print(f"{len(out)-1:3d} [{s:7.2f}-{e:7.2f}] {txt}", flush=True)
json.dump(out, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
