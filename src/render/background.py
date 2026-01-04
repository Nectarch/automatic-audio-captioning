from moviepy.editor import ColorClip


def create_background(duration, size, color=(16, 16, 16)):
    w, h = size
    return ColorClip(size=(w, h), color=color).set_duration(duration)
