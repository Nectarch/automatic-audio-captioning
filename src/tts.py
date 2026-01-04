import os
import sys
import json
import argparse
import subprocess
from datetime import datetime

from tts.synthesize import synthesize_to_mp3
from tts.convert import mp3_to_wav


def load_config(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def ensure_ffmpeg_available():
    subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="config.json")
    parser.add_argument("--text", type=str, default=None)
    parser.add_argument("--input", type=str, default=None)
    args = parser.parse_args()

    ensure_ffmpeg_available()

    cfg = load_config(args.config)
    tts_cfg = cfg.get("tts", {}) if isinstance(cfg.get("tts", {}), dict) else {}

    out_dir = tts_cfg.get("out_dir", "outputs")
    input_path = tts_cfg.get("input_path", os.path.join("inputs", "sample.txt"))
    voice = tts_cfg.get("voice", "en-US-JennyNeural")
    rate = tts_cfg.get("rate", "+0%")
    volume = tts_cfg.get("volume", "+0%")
    normalize = bool(tts_cfg.get("normalize", True))

    os.makedirs(out_dir, exist_ok=True)

    if args.text and args.text.strip():
        text = args.text.strip()
    else:
        in_path = args.input or input_path
        if not os.path.exists(in_path):
            raise FileNotFoundError(f"Input file not found: {in_path}")
        text = read_text_file(in_path)

    if not text:
        print("Empty text.")
        sys.exit(1)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    tmp_mp3 = os.path.join(out_dir, f"tts_tmp_{ts}.mp3")
    out_wav = os.path.join(out_dir, f"voice_{ts}.wav")

    try:
        import asyncio
        asyncio.run(synthesize_to_mp3(text, tmp_mp3, voice, rate, volume))
    except Exception as e:
        raise RuntimeError(f"Edge TTS failed: {e}")

    try:
        mp3_to_wav(tmp_mp3, out_wav, normalize=normalize)
    finally:
        try:
            os.remove(tmp_mp3)
        except Exception:
            pass

    print(os.path.abspath(out_wav))


if __name__ == "__main__":
    main()
