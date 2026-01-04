import os
from datetime import datetime
from moviepy.editor import AudioFileClip, CompositeVideoClip


def compose_and_export(bg, captions, audio_path, out_dir, fps, fast_mode, fast_duration, debug):
    os.makedirs(out_dir, exist_ok=True)

    voice = AudioFileClip(audio_path)
    final_duration = fast_duration if fast_mode else voice.duration

    final = (
        CompositeVideoClip([bg] + captions)
        .set_audio(voice)
        .subclip(0, final_duration)
    )

    final = final.crop(
        x1=0,
        y1=0,
        x2=final.size[0] - (final.size[0] % 2),
        y2=final.size[1] - (final.size[1] % 2)
    )

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.abspath(os.path.join(out_dir, f"render_{ts}.mp4"))
    print(out_path)

    if debug:
        final.save_frame("debug_frame.png", t=1.0)

    final.write_videofile(
        out_path,
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp-audio-render.m4a",
        remove_temp=True,
        preset="ultrafast",
        threads=2,
        ffmpeg_params=["-pix_fmt", "yuv420p"],
        verbose=False,
        logger=None
    )

    return out_path
