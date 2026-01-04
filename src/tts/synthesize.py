import edge_tts


async def synthesize_to_mp3(text: str, mp3_path: str, voice: str, rate: str, volume: str) -> None:
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume)
    await communicate.save(mp3_path)