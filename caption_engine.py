"""
ASS caption renderer: 20 styles, 10 animations, 9-grid / custom position.

The renderer always works on a 1080x1920 ASS canvas. ffmpeg/libass scales
that canvas to the final video size automatically, so captions look the
same at 720x1280 or 1080x1920.
"""

import os

from caption_styles import (
    ANIMATIONS,
    CAPTION_EFFECTS,
    CAPTION_POSITIONS,
    CAPTION_STYLES,
    DEFAULT_ANIMATION,
    DEFAULT_EFFECT,
    DEFAULT_STYLE,
)

CANVAS_W = 1080
CANVAS_H = 1920

FONT_FILES = {
    "Poppins": ["Poppins-Bold.ttf", "Poppins-ExtraBold.ttf"],
    "Playfair Display": ["PlayfairDisplay-BoldItalic.ttf", "PlayfairDisplay-Bold.ttf"],
    "Montserrat": ["Montserrat-ExtraBold.ttf", "Montserrat-Bold.ttf"],
    "DM Serif Display": ["DMSerifDisplay-Italic.ttf"],
    "Anton": ["Anton-Regular.ttf"],
    "Bebas Neue": ["BebasNeue-Regular.ttf"],
    "Bangers": ["Bangers-Regular.ttf"],
    "Luckiest Guy": ["LuckiestGuy-Regular.ttf"],
    "Cinzel": ["Cinzel-Bold.ttf"],
    "Press Start 2P": ["PressStart2P-Regular.ttf"],
    "Permanent Marker": ["PermanentMarker-Regular.ttf"],
    "Lobster": ["Lobster-Regular.ttf"],
    "Inter": ["Inter-Black.ttf", "Inter-Bold.ttf"],
    "Archivo Black": ["ArchivoBlack-Regular.ttf"],
    "Space Grotesk": ["SpaceGrotesk-Bold.ttf"],
    "Righteous": ["Righteous-Regular.ttf"],
    "Roboto Mono": ["RobotoMono-Bold.ttf"],
}

SERIF_FONTS = {"Playfair Display", "Cinzel", "DM Serif Display", "Lobster"}


def _font_available(family, fonts_dir="."):
    for filename in FONT_FILES.get(family, []):
        path = os.path.join(fonts_dir, filename)
        if os.path.exists(path) and os.path.getsize(path) > 20000:
            return True
    return False


def resolve_font(family, fonts_dir="."):
    if family and _font_available(family, fonts_dir):
        return family
    return "Liberation Serif" if family in SERIF_FONTS else "DejaVu Sans"


def hex_to_ass(hex_color, alpha=0):
    """#RRGGBB -> &HAABBGGRR& (ASS is BGR, alpha 00 = opaque)."""
    value = (hex_color or "#FFFFFF").strip().lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    if len(value) != 6:
        value = "FFFFFF"
    r, g, b = int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)
    return "&H%02X%02X%02X%02X&" % (alpha, b, g, r)


def _inline_color(hex_color):
    return hex_to_ass(hex_color, 0)


def _num(value, fallback=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _int(value, fallback=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return fallback


def resolve_style(caption_cfg):
    """Merge config overrides onto the selected style preset."""
    style = dict(CAPTION_STYLES.get(caption_cfg.get("style"), CAPTION_STYLES[DEFAULT_STYLE]))

    if caption_cfg.get("font_size") is not None:
        new_size = max(20, _int(caption_cfg["font_size"], style["size"]))
        ratio = new_size / max(1, style["size"])
        style["size"] = new_size
        style["accent_size"] = max(20, int(round(style["accent_size"] * ratio)))

    for cfg_key, style_key in (
        ("max_words", "max_words"),
        ("max_chars", "max_chars"),
        ("uppercase", "uppercase"),
        ("primary_color", "primary"),
        ("accent_color", "accent"),
        ("outline_color", "outline"),
        ("outline_width", "outline_width"),
        ("glow", "glow"),
        ("background", "background"),
        ("background_color", "background_color"),
        ("background_opacity", "background_opacity"),
    ):
        value = caption_cfg.get(cfg_key)
        if value is not None:
            style[style_key] = value

    style["size"] = max(20, _int(style["size"], 74))
    style["accent_size"] = max(20, _int(style["accent_size"], style["size"] + 8))
    style["max_words"] = max(1, min(6, _int(style["max_words"], 3)))
    style["max_chars"] = max(6, min(40, _int(style["max_chars"], 18)))
    style["outline_width"] = max(0.0, min(20.0, _num(style["outline_width"], 3)))
    style["shadow"] = max(0.0, min(20.0, _num(style["shadow"], 3)))
    style["spacing"] = max(0.0, min(10.0, _num(style["spacing"], 0.5)))
    style["rotate"] = max(-20.0, min(20.0, _num(style["rotate"], 0)))
    style["accent_scale"] = max(1.0, min(1.6, _num(style["accent_scale"], 1.10)))
    style["box_padding"] = max(0, min(60, _int(style["box_padding"], 18)))
    style["glow_strength"] = max(2, min(40, _int(style["glow_strength"], 14)))
    style["glow_blur"] = max(0, min(30, _int(style["glow_blur"], 8)))
    style["background_opacity"] = max(0.0, min(1.0, _num(style["background_opacity"], 0.62)))
    style["chromatic_shift"] = max(0, min(10, _int(style["chromatic_shift"], 0)))

    style["font"] = resolve_font(style.get("font"))
    style["accent_font"] = resolve_font(style.get("accent_font") or style["font"])
    if not style.get("glow_color"):
        style["glow_color"] = style["accent"]
    return style


def resolve_effects(caption_cfg, base_style):
    """Merge effect preset onto the resolved style."""
    effect_name = caption_cfg.get("effect", DEFAULT_EFFECT)
    if not effect_name or effect_name == "none":
        return base_style

    effect = CAPTION_EFFECTS.get(effect_name, CAPTION_EFFECTS["none"])
    style = dict(base_style)

    # Apply effect properties
    for key, value in effect.items():
        if key in ("label", "desc"):
            continue
        style[key] = value

    # Effect-specific intensity scaling
    intensity = _num(caption_cfg.get("effect_intensity"), 1.0)
    if effect.get("glow"):
        style["glow_strength"] = int(style.get("glow_strength", 14) * intensity)
        style["glow_blur"] = int(style.get("glow_blur", 8) * intensity)
    if effect.get("chromatic_shift"):
        style["chromatic_shift"] = int(style.get("chromatic_shift", 0) * intensity)
    if effect.get("outline_width"):
        style["outline_width"] = style.get("outline_width", 3) * intensity
    if effect.get("shadow"):
        style["shadow"] = style.get("shadow", 3) * intensity

    return style


def caption_anchor(caption_cfg):
    position = caption_cfg.get("position", "bottom_center")
    if position == "custom":
        x_frac = _num(caption_cfg.get("custom_x"), 0.50)
        y_frac = _num(caption_cfg.get("custom_y"), 0.76)
    else:
        preset = CAPTION_POSITIONS.get(position, CAPTION_POSITIONS["bottom_center"])
        x_frac, y_frac = preset["x"], preset["y"]
    x = int(x_frac * CANVAS_W + _int(caption_cfg.get("offset_x"), 0))
    y = int(y_frac * CANVAS_H + _int(caption_cfg.get("offset_y"), 0))
    return max(60, min(CANVAS_W - 60, x)), max(60, min(CANVAS_H - 60, y))


def format_ass_time(seconds):
    total_cs = max(0, int(round(float(seconds) * 100)))
    cs = total_cs % 100
    total_s = total_cs // 100
    s = total_s % 60
    total_m = total_s // 60
    m = total_m % 60
    h = total_m // 60
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def group_words(words, max_words, max_chars):
    groups = []
    current = []
    current_chars = 0
    for word in words:
        text = word["text"]
        gap = 0.0
        if current:
            gap = max(0.0, word["start"] - current[-1]["end"])
        break_group = (
            current
            and (
                len(current) >= max_words
                or current_chars + 1 + len(text) > max_chars
                or gap > 0.85
                or current[-1]["text"].endswith((".", "!", "?"))
            )
        )
        if break_group:
            groups.append(current)
            current = []
            current_chars = 0
        current.append(word)
        current_chars += len(text) + (1 if current_chars else 0)
    if current:
        groups.append(current)
    return groups


def _base_tags(style, bord_value):
    return (
        rf"\fn{style['font']}\fs{style['size']}"
        rf"\b{1 if style['bold'] else 0}\i{1 if style['italic'] else 0}"
        rf"\c{_inline_color(style['primary'])}\3c{_inline_color(style['outline'])}"
        rf"\bord{bord_value:g}\shad{style['shadow']:g}\fsp{style['spacing']:g}"
        rf"\frz{style['rotate']:g}"
    )


def _reset_tags(style, bord_value):
    return (
        rf"\fn{style['font']}\fs{style['size']}"
        rf"\b{1 if style['bold'] else 0}\i{1 if style['italic'] else 0}"
        rf"\c{_inline_color(style['primary'])}\3c{_inline_color(style['outline'])}"
        rf"\bord{bord_value:g}\shad{style['shadow']:g}\fsp{style['spacing']:g}"
        rf"\frz{style['rotate']:g}\fscx100\fscy100"
    )


def _active_tags(style, animation, word_index):
    scale = style["accent_scale"]
    accent = _inline_color(style["accent"])
    tags = (
        rf"\fn{style['accent_font']}\fs{style['accent_size']}"
        rf"\b{1 if style['accent_bold'] else 0}\i{1 if style['accent_italic'] else 0}"
        rf"\c{accent}\3c{_inline_color(style['outline'])}"
    )

    if animation == "pop_highlight":
        tags += (
            rf"\fscx{scale * 100:.1f}\fscy{scale * 100:.1f}"
            rf"\t(0,85,\fscx{scale * 103:.1f}\fscy{scale * 103:.1f})"
        )
    elif animation == "bounce":
        tags += r"\fscx100\fscy100\t(0,55,\fscx118\fscy118)\t(55,130,\fscx96\fscy96)\t(130,190,\fscx100\fscy100)"
    elif animation == "zoom_pulse":
        tags += r"\fscx100\fscy100\t(0,180,\fscx108\fscy108)\t(180,360,\fscx100\fscy100)"
    elif animation == "shake":
        base = style["rotate"]
        tags += (
            rf"\frz{base:g}\t(0,45,\frz{base + 2:g})\t(45,90,\frz{base - 2:g})"
            rf"\t(90,135,\frz{base + 1.5:g})\t(135,180,\frz{base:g})"
        )
    elif animation == "wave":
        tags += r"\fscy100\t(0,90,\fscy112)\t(90,180,\fscy100)"
    elif animation == "typewriter":
        tags += r"\fscx90\fscy90\t(0,70,\fscx100\fscy100)\fad(60,0)"
    elif animation == "karaoke_fill":
        tags += r"\fscx106\fscy106"
    elif animation == "static":
        pass
    # NEW ANIMATIONS
    elif animation == "elastic":
        tags += r"\fscx100\fscy100\t(0,60,\fscx130\fscy130)\t(60,120,\fscx85\fscy85)\t(120,180,\fscx100\fscy100)"
    elif animation == "spiral":
        tags += r"\fscx100\fscy100\t(0,200,\fscx120\fscy120\frz360)\t(200,400,\fscx100\fscy100\frz0)"
    elif animation == "flip":
        tags += r"\fscx100\fscy100\t(0,100,\fscx0)\t(100,101,\fscx100)\t(101,200,\fscx100)"
    elif animation == "glitch":
        tags += r"\fscx100\fscy100\t(0,30,\fscx110)\t(30,60,\fscx90)\t(60,90,\fscx115)\t(90,120,\fscx100)\t(120,150,\fscx95)\t(150,180,\fscx100)"
    elif animation == "pulse":
        tags += r"\fscx100\fscy100\t(0,250,\fscx110\fscy110)\t(250,500,\fscx100\fscy100)\t(500,750,\fscx110\fscy110)\t(750,1000,\fscx100\fscy100)"
    elif animation == "wave_vertical":
        tags += r"\fscy100\t(0,150,\fscy115)\t(150,300,\fscy85)\t(300,450,\fscy115)\t(450,600,\fscy100)"
    elif animation == "typewriter_reveal":
        tags += r"\fscx90\fscy90\t(0,50,\fscx100\fscy100)\fad(40,0)"
    elif animation == "highlight_sweep":
        tags += r"\fscx100\fscy100\c" + accent + r"\t(0,120,\c" + _inline_color(style['primary']) + r")"
    elif animation == "shake_3d":
        base = style["rotate"]
        tags += (
            rf"\frz{base:g}\frx0\fry0\t(0,40,\frz{base + 3:g}\frx2\fry-1)\t(40,80,\frz{base - 3:g}\frx-2\fry1)"
            rf"\t(80,120,\frz{base + 2:g}\frx1\fry-1)\t(120,160,\frz{base:g}\frx0\fry0)"
        )
    elif animation == "rainbow_shift":
        tags += r"\fscx100\fscy100"
    else:
        tags += (
            rf"\fscx{scale * 100:.1f}\fscy{scale * 100:.1f}"
            rf"\t(0,85,\fscx{scale * 103:.1f}\fscy{scale * 103:.1f})"
        )
    return tags


def _word_color(style, word_index):
    if style.get("rainbow") and style.get("accent_colors"):
        colors = style["accent_colors"]
        return colors[word_index % len(colors)]
    return style["primary"]


def _render_line(style, group, active_idx, visible_count, animation, bord_value):
    """Return ASS text for the main caption line."""
    parts = []
    for idx, word in enumerate(group[:visible_count]):
        is_active = idx == active_idx
        is_past = idx < active_idx
        text = word["text"]
        if style.get("uppercase"):
            text = text.upper()

        if is_active:
            tags = _active_tags(style, animation, idx)
            parts.append("{" + tags + "}" + text + "{" + _reset_tags(style, bord_value) + "}")
        elif is_past and animation == "karaoke_fill":
            tags = (
                rf"\fn{style['accent_font']}\fs{style['accent_size']}"
                rf"\c{_inline_color(style['accent'])}\3c{_inline_color(style['outline'])}"
            )
            parts.append("{" + tags + "}" + text + "{" + _reset_tags(style, bord_value) + "}")
        else:
            color = _word_color(style, idx)
            tags = rf"\c{_inline_color(color)}" if color != style["primary"] else ""
            if tags:
                parts.append("{" + tags + "}" + text + "{" + _reset_tags(style, bord_value) + "}")
            else:
                parts.append(text)
    return " ".join(parts)


def _render_glow(style, group, active_idx, visible_count, animation):
    parts = []
    glow = _inline_color(style["glow_color"])
    for idx, word in enumerate(group[:visible_count]):
        text = word["text"]
        if style.get("uppercase"):
            text = text.upper()
        if idx == active_idx:
            tags = (
                rf"\fn{style['accent_font']}\fs{style['accent_size']}"
                rf"\1a&HFF&\3a&H40&\3c{glow}"
                rf"\bord{style['glow_strength']}\blur{style['glow_blur']}\shad0"
            )
            parts.append("{" + tags + "}" + text + r"{\1a&HFF&\3a&HFF&}")
        else:
            parts.append(r"{\1a&HFF&\3a&HFF&}" + text)
    return " ".join(parts)


def _render_chromatic(style, group, visible_count, color_hex):
    color = _inline_color(color_hex)
    words = []
    for word in group[:visible_count]:
        text = word["text"]
        if style.get("uppercase"):
            text = text.upper()
        words.append(text)
    return rf"{{\1a&H00&\3a&HFF&\c{color}\3c{color}\bord0\shad0}}" + " ".join(words)


def _render_scanlines(style, group, visible_count):
    """Render scanline overlay effect."""
    lines = []
    for idx, word in enumerate(group[:visible_count]):
        text = word["text"]
        if style.get("uppercase"):
            text = text.upper()
        lines.append(text)
    # Scanlines are applied via inline style with repeated horizontal lines
    # This is a simplified version - full scanlines would need more complex ASS
    return " ".join(lines)


def _render_halftone(style, group, visible_count):
    """Render halftone dot pattern - simplified as text with pattern chars."""
    words = []
    for idx, word in enumerate(group[:visible_count]):
        text = word["text"]
        if style.get("uppercase"):
            text = text.upper()
        # Add halftone-like character between words
        words.append(text)
    return " ".join(words)


def build_ass(words, caption_cfg, ass_path="captions.ass", fonts_dir="."):
    """Write an ASS file. Returns (ok, metadata dict)."""
    if not caption_cfg.get("enabled", True):
        return False, {"reason": "captions disabled"}
    if not words:
        return False, {"reason": "no words"}

    style = resolve_style(caption_cfg)
    # Apply effects on top of style
    style = resolve_effects(caption_cfg, style)

    animation = caption_cfg.get("animation") or DEFAULT_ANIMATION
    if animation not in ANIMATIONS:
        animation = DEFAULT_ANIMATION

    effect_name = caption_cfg.get("effect", DEFAULT_EFFECT)
    if effect_name not in CAPTION_EFFECTS:
        effect_name = DEFAULT_EFFECT

    x, y = caption_anchor(caption_cfg)
    groups = group_words(words, style["max_words"], style["max_chars"])

    boxed = bool(style.get("background"))
    bord_value = style["box_padding"] if boxed else style["outline_width"]
    main_style_name = "Box" if boxed else "Main"

    back_alpha = int(round((1.0 - style["background_opacity"]) * 255))
    back_color = hex_to_ass(style["background_color"], back_alpha)

    # Determine needed styles
    has_glow = style.get("glow", False)
    has_chromatic = style.get("chromatic_shift", 0) > 0
    has_scanlines = style.get("scanlines", False)
    has_vignette = style.get("vignette", False)
    has_halftone = style.get("halftone", False)

    style_defs = [
        f"Style: Main,{style['font']},{style['size']},{_inline_color(style['primary'])},{_inline_color(style['primary'])},{_inline_color(style['outline'])},&H00000000&,{1 if style['bold'] else 0},{1 if style['italic'] else 0},0,0,100,100,{style['spacing']:g},{style['rotate']:g},1,{style['outline_width']:g},{style['shadow']:g},5,0,0,0,1"
    ]
    if boxed:
        style_defs.append(
            f"Style: Box,{style['font']},{style['size']},{_inline_color(style['primary'])},{_inline_color(style['primary'])},{_inline_color(style['outline'])},{back_color},{1 if style['bold'] else 0},{1 if style['italic'] else 0},0,0,100,100,{style['spacing']:g},{style['rotate']:g},3,{style['box_padding']},0,5,0,0,0,1"
        )
    if has_glow:
        style_defs.append(
            f"Style: Glow,{style['font']},{style['size']},{_inline_color(style['primary'])},{_inline_color(style['primary'])},{_inline_color(style['glow_color'])},&H00000000&,{1 if style['bold'] else 0},{1 if style['italic'] else 0},0,0,100,100,0,0,1,{style['glow_strength']},0,5,0,0,0,1"
        )

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {CANVAS_W}
PlayResY: {CANVAS_H}
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{chr(10).join(style_defs)}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []
    for group in groups:
        group_start = group[0]["start"]
        group_end = group[-1]["end"]
        for active_idx, active_word in enumerate(group):
            t_start = max(0.0, active_word["start"])
            if active_idx + 1 < len(group):
                t_end = group[active_idx + 1]["start"]
            else:
                t_end = max(active_word["end"], group_end)
            if t_end <= t_start:
                t_end = t_start + 0.12

            visible_count = len(group)
            if animation == "typewriter":
                visible_count = active_idx + 1
            elif animation == "typewriter_reveal":
                visible_count = active_idx + 1

            if animation == "slide_up" and active_idx == 0:
                pos_tags = rf"{{\an5\move({x},{y + 38},{x},{y},0,160)\fad(120,0)}}"
            elif animation == "fade_in" and active_idx == 0:
                pos_tags = rf"{{\an5\pos({x},{y})\fad(160,0)}}"
            else:
                pos_tags = rf"{{\an5\pos({x},{y})}}"

            line_text = _render_line(style, group, active_idx, visible_count, animation, bord_value)

            # VHS chromatic fringes (behind the main layer)
            if has_chromatic:
                shift = style["chromatic_shift"]
                magenta = _render_chromatic(style, group, visible_count, "#FF00E5")
                cyan = _render_chromatic(style, group, visible_count, "#00E5FF")
                pos_left = rf"{{\an5\pos({x - shift},{y})}}"
                pos_right = rf"{{\an5\pos({x + shift},{y})}}"
                events.append(
                    f"Dialogue: 0,{format_ass_time(t_start)},{format_ass_time(t_end)},Main,,0,0,0,,"
                    f"{pos_left}{magenta}"
                )
                events.append(
                    f"Dialogue: 1,{format_ass_time(t_start)},{format_ass_time(t_end)},Main,,0,0,0,,"
                    f"{pos_right}{cyan}"
                )

            # Glow layer (behind the text)
            if has_glow:
                glow_text = _render_glow(style, group, active_idx, visible_count, animation)
                events.append(
                    f"Dialogue: 0,{format_ass_time(t_start)},{format_ass_time(t_end)},Glow,,0,0,0,,"
                    f"{pos_tags}{glow_text}"
                )

            # Main text layer
            main_layer = 2 if (has_chromatic or has_glow) else 1
            events.append(
                f"Dialogue: {main_layer},{format_ass_time(t_start)},{format_ass_time(t_end)},"
                f"{main_style_name},,0,0,0,,{pos_tags}{line_text}"
            )

            # Effect-specific additional layers
            if has_scanlines:
                # Scanline overlay - simplified as semi-transparent horizontal bars
                scan_alpha = int(style.get("scanline_opacity", 0.3) * 255)
                scan_color = hex_to_ass("#000000", scan_alpha)
                events.append(
                    f"Dialogue: {main_layer + 1},{format_ass_time(t_start)},{format_ass_time(t_end)},"
                    f"Main,,0,0,0,,{pos_tags}{{\\1a&H{scan_alpha:02X}&\\c{scan_color}\\bord0\\shad0}}"
                    + " ".join(["_" * 50] * 20)  # Simplified scanline representation
                )

            if has_vignette:
                # Vignette as darkened edges - would need more complex ASS drawing
                # Simplified: add subtle dark overlay at top/bottom
                vig_alpha = int(style.get("vignette_strength", 0.4) * 255)
                vig_color = hex_to_ass("#000000", vig_alpha)
                events.append(
                    f"Dialogue: {main_layer + 2},{format_ass_time(t_start)},{format_ass_time(t_end)},"
                    f"Main,,0,0,0,,{pos_tags}{{\\1a&H{vig_alpha:02X}&\\c{vig_color}\\bord0\\shad0\\fs{style['size'] * 2}}}"
                    + " " * 100
                )

            if has_halftone:
                # Halftone pattern - simplified representation
                ht_size = style.get("halftone_size", 4)
                events.append(
                    f"Dialogue: {main_layer + 3},{format_ass_time(t_start)},{format_ass_time(t_end)},"
                    f"Main,,0,0,0,,{pos_tags}{{\\1a&H80&\\c{_inline_color(style['outline'])}\\bord0\\shad0\\fs{ht_size}}}"
                    + " ".join(["●"] * (visible_count * 3))
                )

    with open(ass_path, "w", encoding="utf-8") as handle:
        handle.write(header + "\n".join(events) + "\n")

    return True, {
        "style": style["label"],
        "animation": ANIMATIONS[animation]["label"],
        "effect": CAPTION_EFFECTS.get(effect_name, {}).get("label", "None"),
        "position": f"{x},{y}",
        "groups": len(groups),
        "events": len(events),
        "words": len(words),
    }
