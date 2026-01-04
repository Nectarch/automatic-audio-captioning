import subprocess


def run_ffmpeg(args_list):
    try:
        subprocess.run(args_list, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        raise RuntimeError("ffmpeg not found in PATH.")
    except subprocess.CalledProcessError:
        raise RuntimeError("ffmpeg failed.")


def mp3_to_wav(mp3_path: str, wav_path: str, normalize: bool) -> None:
    if normalize:
        cmd = [
            "ffmpeg", "-y",
            "-i", mp3_path,
            "-af", "loudnorm=I=-16:LRA=11:TP=-1.5",
            "-ar", "44100",
            wav_path
        ]
    else:
        cmd = ["ffmpeg", "-y", "-i", mp3_path, "-ar", "44100", wav_path]
    run_ffmpeg(cmd)
