---
name: tu-su
description: Tự sự — dựng video tự sự / tri ân cảm xúc (giọng thật của nhân vật mở đầu + giọng đọc lồng tiếng + ảnh/clip) theo phong cách chữ vàng hai tầng, chuyển cảnh phong phú (nét cọ, vòng tròn, lồng hình, vệt sáng), bụi vàng, nhạc nền nhẹ. Use when the user asks for a "video tự sự", tribute / storytelling / memoir video, wants a heartfelt narration script written from their notes, wants a quote from a clip typed on screen with a typing sound, or says "tự sự", "tri ân", "lồng tiếng", "kể chuyện" — Vietnamese or English.
---

# Tự sự — narrative tribute videos

Turns a real quote from a clip, a recorded narration and a folder of photos/clips into a finished vertical video
(default 3:4, 1080×1440). Everything is driven by one `project.json`; scripts are deterministic.

Reference result: `examples/su-phu-gia-roi.json` ("Sư phụ già rồi", 2:10).

## Workflow (do these in order — each step is a checkpoint with the user)

1. **Collect media.** Clips + photos (HEIC ok). Google Drive folder links shared "anyone with link" download with
   `curl -L "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t"`; list IDs with the
   Drive search tool (`parentId = '<folder>'`). Make contact sheets (ffmpeg `tile`) and *look* at every asset.
2. **Find the quote.** `transcribe_chunks.py CLIP_AUDIO quote.json --prompt "<expected words>"`. Outdoor audio is
   windy: pre-filter (`highpass=150,afftdn,dynaudnorm`). If the camera operator also speaks, tell voices apart by
   pitch (male ≈100–130 Hz, female ≈220–290 Hz) and keep only the subject's ranges. Send the user a short cut to
   confirm the exact words before building.
3. **Write the script (bài đọc).** Rewrite the user's raw notes into a reading script: coherent, concise, everyday
   but lightly poetic; keep their meaning and their own phrases; mark pauses `( / )` short, `( // )` long; split
   into 4–6 paragraphs and name the visuals for each. List every word you corrected (speech-to-text errors) so the
   user can veto. The opening quote is NOT in the reading script — it is the subject's real voice.
4. **Build the quote intro** (`quote_intro.py`). Rules the user insisted on:
   - the quote's voice pieces are **joined into one continuous sentence** (no on/off noise gaps); denoised once
     so the noise floor is constant; never clip the tail of a word (check RMS until it really decays);
   - text = white italic lead + big gold KEYWORD, typed letter by letter with a **soft, light** keyboard tick
     (not a harsh click); the footage keeps running with a slow push-in.
   Render with `"fade_out": true` first and send it for approval.
5. **Clean the narration** (`clean_vo.py`): transcribe with `transcribe_chunks.py`, find stumbles/retakes (a phrase
   repeated, a cut-off start like "Mà mấy ai…"), then `--drop A-B`, `--cut-after T:END`, `--skip-before T`.
   Keep the reader's intentional pauses (the script keeps up to 0.85 s breaths). Re-run `transcribe_chunks.py`
   on the cleaned wav → `vo_chunks.json`; this phrase list is the caption timeline.
6. **Plan shots & captions in `project.json`.** One shot per thought, matched to what is being said (literal
   matches land hardest: "bánh mì" → photos of making bánh mì, "ngồi bệt trên bãi cỏ" → people on grass,
   "về Trời" → "Stairway to Heaven" sign). Captions: one `[white lead, GOLD KEY]` per chunk, matching the words
   actually spoken; `*` prefix = big quote card (use for 3–4 key lines only).
   **Transitions must be varied and meaningful — never plain cuts only:** `brush` (gold-edged ink stroke, for new
   ideas), `iris` (gold-rimmed circle, for close-ups of the face), `dx` (double exposure), `whip` (zoom blur, for
   quick lists), `leak` (light leak, for heaven/sun moments), `dip` (to black, between paragraphs). Add a `ghost`
   double exposure (face over landscape) on the most emotional line.
7. **Preview stills** — `render_story.py project.json prev/ 12 40 88 …` — and check: faces not cut off, no burned-in
   date stamps / watermarks / other people's logos in frame (crop with `z`/`c`), captions not over text already in
   an image, the right person on screen.
8. **Render** — `render_story.py project.json out.mp4` (≈1 min per 10 s on 4 cores; needs ~6 GB RAM, never run two
   renders at once). Deliver with SendUserFile `display: "attach"` so the user gets a **download** card; keep it
   ≤ ~50 MB (`ffmpeg -crf 26 -maxrate 2.5M`) for phones. Offer a Facebook caption with an ALL-CAPS title + hashtags.

## Commands

```bash
bash scripts/setup.sh                                   # deps + fonts (Oswald, Playfair Display — Vietnamese)
python3 -I scripts/transcribe_chunks.py voice.m4a work/raw_chunks.json --prompt "Sư phụ, chúng sanh, …"
python3 -I scripts/clean_vo.py voice.m4a work/vo_clean.wav --skip-before 19 --drop 73.8-75.2 --cut-after 132.6:133.55
python3 -I scripts/transcribe_chunks.py work/vo_clean.wav work/vo_chunks.json --prompt "…"
python3 -I scripts/quote_intro.py project.json work/intro
python3 -I scripts/render_story.py project.json prev/ 3 12 34 61     # stills
python3 -I scripts/render_story.py project.json out/video.mp4        # full render
```

Paths in `project.json` are relative to the file. Shot fields: `vo:[a,b]` (narration time, `"end"` = after the last
word) or `t:[a,b]` (absolute); `img` or `vid` (+`ss` start); `z:[z0,z1]` zoom; `c:[[cx,cy],[cx,cy]]` focus (0–1);
`tr:[kind, seconds]`; optional `ghost:[img, 0.3–0.5]`. Top-level: `vo.start` (when narration begins, ≈ intro voice
end + 1.5 s), `intro_len` (cut from intro to first shot — continue the same clip at `t0+intro_len` for a seamless
hand-off), `logo`, `music` (file; default is a soft synthesized pad ducked under the voice), `music_level`.

## Style constants (what the user approved)

- Two-tier captions: Playfair Display italic warm-white lead + Oswald Bold gold-gradient KEYWORD with dark stroke,
  warm glow, light sweep ("shine") and a gold ornament line with a diamond that draws out underneath.
- Big quote cards: dark ink-brush band paints in behind, gold text scales in.
- Warm grade, vignette, darker lower third for legibility, gentle film grain, floating gold dust throughout.
- Quote intro: real voice + typed text; narration starts after a short silence while the footage continues.

## Pitfalls

- Whisper on long noisy/music audio outputs "Hãy subscribe cho kênh…" — always use `transcribe_chunks.py`.
- Words with zero-length timestamps in a re-transcription are hallucinated repeats, not real retakes.
- `pillow-heif` is needed for iPhone HEIC; apply EXIF orientation (handled by `load_image`).
- Big source images are downscaled on load; videos are loaded per shot and freed — keep previews to a few stills.
