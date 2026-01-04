import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip


def build_word_groups(word_segments, max_words):
    punct_stop = [".", "!", "?", ","]

    def should_stop(token):
        t = token.strip()
        return (t[-1:] in punct_stop) or t.endswith('"') or t.endswith("'")

    groups = []
    i = 0
    while i < len(word_segments):
        group = []
        while i < len(word_segments) and len(group) < max_words:
            group.append(word_segments[i])
            if should_stop(word_segments[i]["word"]):
                i += 1
                break
            i += 1
        groups.append(group)
    return groups


def _caption_image(
    words,
    highlight_index,
    font_path,
    font_size,
    stroke_width,
    max_width,
    line_spacing,
    text_shadow,
    highlight_enabled,
    downscale_enabled,
    downscale_factor,
    stroke_fill="black",
    text_fill="white",
    highlight_fill="yellow",
    shadow_offset=(3, 3),
):
    scale = downscale_factor if downscale_enabled else 1.0
    if downscale_enabled:
        font_size = int(font_size * scale)
        stroke_width = max(1, int(stroke_width * scale))
        max_width = int(max_width * scale)
        line_spacing = int(line_spacing * scale)
        shadow_offset = (int(shadow_offset[0] * scale), int(shadow_offset[1] * scale))

    margin = int(font_size * 0.6)
    font = ImageFont.truetype(font_path, font_size)
    spacing = int(28 * scale) if downscale_enabled else 28

    lines = []
    current = []
    draw_test = ImageDraw.Draw(Image.new("RGB", (10, 10)))

    for w in words:
        test_line = " ".join(current + [w])
        bbox = draw_test.textbbox((0, 0), test_line, font=font)
        if (bbox[2] - bbox[0]) <= max_width:
            current.append(w)
        else:
            if current:
                lines.append(current)
            current = [w]
    if current:
        lines.append(current)

    ascent, descent = font.getmetrics()
    line_h = int(ascent + descent + line_spacing)
    block_h = int(len(lines) * line_h)
    total_h = int(block_h + margin * 2)
    img_w = int(max_width + margin * 2 + 100)

    img = Image.new("RGBA", (img_w, total_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    word_i = 0
    y = int((total_h - block_h) // 2)

    for line in lines:
        word_widths = [int(font.getbbox(t)[2] - font.getbbox(t)[0]) for t in line]
        line_width = int(sum(word_widths) + spacing * (len(line) - 1))
        x = int((img_w - line_width) // 2)

        for t in line:
            fill = highlight_fill if (highlight_enabled and word_i == highlight_index) else text_fill

            if text_shadow:
                for i in range(stroke_width):
                    ox = shadow_offset[0] + i
                    oy = shadow_offset[1] + i
                    draw.text((x + ox, y + oy), t, font=font, fill=stroke_fill)
            else:
                for dx in range(-stroke_width, stroke_width + 1):
                    for dy in range(-stroke_width, stroke_width + 1):
                        if dx * dx + dy * dy <= stroke_width * stroke_width:
                            draw.text((x + dx, y + dy), t, font=font, fill=stroke_fill)

            draw.text((x, y), t, font=font, fill=fill)
            x += int(font.getbbox(t)[2] - font.getbbox(t)[0]) + spacing
            word_i += 1

        y += line_h

    if downscale_enabled:
        final_w = int(img_w / scale)
        final_h = int(total_h / scale)
        img = img.resize((final_w, final_h), Image.LANCZOS)

    return img


def compute_auto_canvas_size(
    words,
    group_words,
    font_path,
    font_size,
    stroke_width,
    max_width,
    line_spacing,
    text_shadow,
    highlight_enabled,
    downscale_enabled,
    downscale_factor,
    padding,
):
    groups = build_word_groups(words, max_words=group_words)
    max_w = 1
    max_h = 1

    for group in groups:
        word_texts = [w["word"].strip() for w in group]
        img = _caption_image(
            words=word_texts,
            highlight_index=0,
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
        max_w = max(max_w, img.size[0])
        max_h = max(max_h, img.size[1])

    w = max_w + padding * 2
    h = max_h + padding * 2

    if w % 2 == 1:
        w += 1
    if h % 2 == 1:
        h += 1

    return (w, h)


def build_caption_clips(
    words,
    canvas_size,
    group_words,
    font_path,
    font_size,
    stroke_width,
    max_width,
    line_spacing,
    text_shadow,
    highlight_enabled,
    downscale_enabled,
    downscale_factor,
):
    groups = build_word_groups(words, max_words=group_words)
    caption_clips = []

    for gi, group in enumerate(groups):
        word_texts = [w["word"].strip() for w in group]
        group_start = group[0]["start"]
        group_end = groups[gi + 1][0]["start"] if gi < len(groups) - 1 else group[-1]["end"] + 0.1

        if not highlight_enabled:
            img = _caption_image(
                words=word_texts,
                highlight_index=0,
                font_path=font_path,
                font_size=font_size,
                stroke_width=stroke_width,
                max_width=max_width,
                line_spacing=line_spacing,
                text_shadow=text_shadow,
                highlight_enabled=False,
                downscale_enabled=downscale_enabled,
                downscale_factor=downscale_factor,
            )
            caption_clips.append(
                ImageClip(np.array(img))
                .set_start(group_start)
                .set_duration(max(0.01, group_end - group_start))
                .set_position(("center", "center"))
            )
        else:
            for hi in range(len(word_texts)):
                img = _caption_image(
                    words=word_texts,
                    highlight_index=hi,
                    font_path=font_path,
                    font_size=font_size,
                    stroke_width=stroke_width,
                    max_width=max_width,
                    line_spacing=line_spacing,
                    text_shadow=text_shadow,
                    highlight_enabled=True,
                    downscale_enabled=downscale_enabled,
                    downscale_factor=downscale_factor,
                )
                word_start = group[hi]["start"]
                word_end = group[hi + 1]["start"] if hi < len(group) - 1 else group_end
                caption_clips.append(
                    ImageClip(np.array(img))
                    .set_start(word_start)
                    .set_duration(max(0.01, word_end - word_start))
                    .set_position(("center", "center"))
                )

    return caption_clips
