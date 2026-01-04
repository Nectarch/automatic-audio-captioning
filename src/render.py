import os
import json
import argparse

from render.transcribe import transcribe_words
from render.background import create_background
from render.captions import compute_auto_canvas_size, build_caption_clips
from render.compose import compose_and_export


def load_config(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_latest_file(folder: str, ext: str):
    if not folder or not os.path.isdir(folder):
        return None
    files = [f for f in os.listdir(folder) if f.lower().endswith(ext.lower())]
    if not files:
        return None
    files.sort(key=lambda f: os.path.getmtime(os.path.join(folder, f)), reverse=True)
    return os.path.join(folder, files[0])


def parse_rgb(hex_color: str):
    s = (hex_color or "").strip()
    if s.startswith("#"):
        s = s[1:]
    if len(s) != 6:
        raise ValueError("bg_color must be like #RRGGBB")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="config.json")
    args = parser.parse_args()

    cfg = load_config(args.config)
    asr_cfg = cfg.get("asr", {}) if isinstance(cfg.get("asr", {}), dict) else {}
    r_cfg = cfg.get("render", {}) if isinstance(cfg.get("render", {}), dict) else {}

    out_dir = r_cfg.get("out_dir", "outputs")
    font_path = r_cfg.get("font_path", "assets/fonts/MikadoBold.otf")

    audio_source = r_cfg.get("audio_source", "latest")
    audio_dir = r_cfg.get("audio_dir", out_dir)
    audio_path = r_cfg.get("audio_path", os.path.join(out_dir, "my_voice.wav"))

    if audio_source == "latest":
        resolved_audio = get_latest_file(audio_dir, ".wav")
    else:
        resolved_audio = audio_path if os.path.exists(audio_path) else None

    if not resolved_audio:
        raise FileNotFoundError("No audio found. Set render.audio_source/audio_dir/audio_path correctly.")

    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Font not found: {font_path}")

    model_name = asr_cfg.get("model_name", "small")
    vad_method = asr_cfg.get("vad_method", "silero")
    language = asr_cfg.get("language", "en")
    device_pref = asr_cfg.get("device", None)

    bg_hex = r_cfg.get("bg_color", "#737373")
    bg_color = parse_rgb(bg_hex)

    fps = int(r_cfg.get("fps", 24))
    padding = int(r_cfg.get("auto_padding", 80))

    debug = bool(r_cfg.get("debug_mode", False))
    fast_mode = bool(r_cfg.get("fast_mode", False))
    fast_duration = float(r_cfg.get("fast_duration", 30))

    text_shadow = bool(r_cfg.get("text_shadow", True))
    highlight_enabled = bool(r_cfg.get("highlight_enabled", False))
    downscale_enabled = bool(r_cfg.get("downscale_enabled", False))
    downscale_factor = float(r_cfg.get("downscale_factor", 1.0))

    group_words = int(r_cfg.get("group_words", 7))
    font_size = int(r_cfg.get("font_size", 80))
    stroke_width = int(r_cfg.get("stroke_width", 12))
    max_width = int(r_cfg.get("max_width", 1000))
    line_spacing = int(r_cfg.get("line_spacing", 3))

    device, words = transcribe_words(
        audio_path=resolved_audio,
        model_name=model_name,
        vad_method=vad_method,
        language=language,
        device_pref=device_pref,
    )
    print(device)

    if not words:
        raise RuntimeError("ASR returned no aligned words.")

    canvas_size = compute_auto_canvas_size(
        words=words,
        group_words=group_words,
        font_path=font_path,
        font_size=font_size,
        stroke_width=stroke_width,
        max_width=max_width,
        line_spacing=line_spacing,
        text_shadow=text_shadow,
        highlight_enabled=highlight_enabled,
        downscale_enabled=downscale_enabled,
        downscale_factor=downscale_factor,
        padding=padding,
    )

    from moviepy.editor import AudioFileClip
    voice = AudioFileClip(resolved_audio)
    bg = create_background(duration=voice.duration, size=canvas_size, color=bg_color)

    captions = build_caption_clips(
        words=words,
        canvas_size=canvas_size,
        group_words=group_words,
        font_path=font_path,
        font_size=font_size,
        stroke_width=stroke_width,
        max_width=max_width,
        line_spacing=line_spacing,
        text_shadow=text_shadow,
        highlight_enabled=highlight_enabled,
        downscale_enabled=downscale_enabled,
        downscale_factor=downscale_factor,
    )

    compose_and_export(
        bg=bg,
        captions=captions,
        audio_path=resolved_audio,
        out_dir=out_dir,
        fps=fps,
        fast_mode=fast_mode,
        fast_duration=fast_duration,
        debug=debug,
    )


if __name__ == "__main__":
    main()
