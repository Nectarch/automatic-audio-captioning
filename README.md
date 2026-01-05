# Automatic Audio Captioning

A small pipeline to generate narrated captioned videos:
1) Generate voice audio with Microsoft Edge TTS (text → mp3 → wav)
2) Transcribe + word-align with WhisperX
3) Render captions over a background and export an mp4 with MoviePy

## Requirements
- Python 3.10+
- FFmpeg installed and available on PATH

## Setup (Windows)
```bat
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```
Recommended: use a virtual environment to avoid installing packages into your global Python environment.
Reference: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/

## Config
Edit config.json to control:
- TTS voice / rate / volume
- render size / background / caption styling
- WhisperX model / device settings

## Usage
### 1) Generate voice audio
```bat
python src\tts.py --config config.json
```
Or quick test:

```bat
python src\tts.py --text "hello world"
```
Outputs are written to outputs/.

### 2) Render a video
```bat
python src\render.py --config config.json
```
## Notes
The outputs/ directory contains generated audio/video and is usually not committed to git.
