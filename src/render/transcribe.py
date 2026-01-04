import torch
import whisperx


def get_device(device_pref: str | None):
    if device_pref in ("cpu", "cuda"):
        if device_pref == "cuda" and not torch.cuda.is_available():
            return "cpu"
        return device_pref
    return "cuda" if torch.cuda.is_available() else "cpu"


def transcribe_words(audio_path: str, model_name: str, vad_method: str, language: str, device_pref: str | None):
    device = get_device(device_pref)
    compute_type = "float32" if device == "cuda" else "int8"

    model = whisperx.load_model(
        model_name,
        device=device,
        compute_type=compute_type,
        vad_method=vad_method,
    )

    result = model.transcribe(audio_path, language=language)
    segments = result.get("segments", [])

    align_model, metadata = whisperx.load_align_model(language_code=language, device=device)
    aligned = whisperx.align(segments, align_model, metadata, audio_path, device=device)

    words = []
    for seg in aligned.get("segments", []):
        if "words" in seg:
            words.extend(seg["words"])

    return device, [w for w in words if w.get("start") is not None and w.get("end") is not None and w.get("word")]
