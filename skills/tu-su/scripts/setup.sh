#!/usr/bin/env bash
# One-time setup for the tự sự pipeline: Python deps + Vietnamese-capable fonts (cached in ~/.cache/tu-su/fonts).
set -euo pipefail
command -v ffmpeg >/dev/null || { echo "ffmpeg is required"; exit 1; }
python3 -m pip install -q --break-system-packages numpy opencv-python-headless pillow pillow-heif soundfile faster-whisper 2>/dev/null \
  || python3 -m pip install -q numpy opencv-python-headless pillow pillow-heif soundfile faster-whisper
python3 -I -c "import sys; sys.path.insert(0, '$(dirname "$0")'); import common; print('fonts:', common.ensure_fonts())"
