"""
Caption style + animation presets for Auto Clipper.

This file is the single source of truth for the 20 caption looks and
10 caption animations. The website data file (docs/data.js) is generated
from this module by tools/build_web_data.py.

Colors are plain #RRGGBB strings. The ASS renderer converts them.
"""

DEFAULT_STYLE = "editorial_glow"
DEFAULT_ANIMATION = "pop_highlight"
DEFAULT_EFFECT = "none"


def _style(label, **overrides):
    """Build a full style dict from sensible defaults + overrides."""
    base = {
        "label": label,
        "font": "Poppins",
        "accent_font": "Poppins",
        "size": 74,
        "accent_size": 82,
        "bold": True,
        "italic": False,
        "accent_bold": True,
        "accent_italic": False,
        "uppercase": False,
        "primary": "#FFFFFF",
        "accent": "#FF3B6B",
        "outline": "#000000",
        "outline_width": 3,
        "shadow": 3,
        "glow": False,
        "glow_color": None,
        "glow_strength": 14,
        "glow_blur": 8,
        "background": False,
        "background_color": "#000000",
        "background_opacity": 0.62,
        "box_padding": 18,
        "spacing": 0.5,
        "rotate": 0,
        "accent_scale": 1.10,
        "max_words": 3,
        "max_chars": 18,
        "rainbow": False,
        "accent_colors": [],
        "chromatic_shift": 0,
    }
    base.update(overrides)
    return base


CAPTION_STYLES = {
    # 1 ------------------------------------------------------------------
    "editorial_glow": _style(
        "Editorial Glow",
        font="Poppins",
        accent_font="Playfair Display",
        size=74,
        accent_size=84,
        accent_italic=True,
        accent="#FF3B6B",
        outline_width=3,
        shadow=3,
        glow=True,
        glow_strength=14,
        spacing=0.5,
    ),
    # 2 ------------------------------------------------------------------
    "beast_mode": _style(
        "Beast Mode",
        font="Montserrat",
        accent_font="Montserrat",
        size=78,
        accent_size=88,
        uppercase=True,
        accent="#FFD400",
        outline_width=7,
        shadow=0,
        accent_scale=1.16,
        max_words=2,
        max_chars=14,
    ),
    # 3 ------------------------------------------------------------------
    "tiktok_classic": _style(
        "TikTok Classic",
        font="Poppins",
        accent_font="Poppins",
        size=76,
        accent_size=84,
        uppercase=True,
        accent="#FF2D55",
        outline_width=6,
        shadow=0,
        max_words=3,
        max_chars=16,
    ),
    # 4 ------------------------------------------------------------------
    "neon_cyan": _style(
        "Neon Cyan",
        font="Poppins",
        accent_font="Poppins",
        size=76,
        accent_size=86,
        uppercase=True,
        accent="#00E5FF",
        outline="#001018",
        outline_width=4,
        shadow=0,
        glow=True,
        glow_strength=18,
        accent_scale=1.12,
    ),
    # 5 ------------------------------------------------------------------
    "fire_cracker": _style(
        "Fire Cracker",
        font="Anton",
        accent_font="Anton",
        size=84,
        accent_size=94,
        uppercase=True,
        accent="#FF6B00",
        outline="#1A0500",
        outline_width=5,
        shadow=2,
        glow=True,
        glow_strength=16,
        accent_scale=1.12,
    ),
    # 6 ------------------------------------------------------------------
    "comic_bangers": _style(
        "Comic Bangers",
        font="Bangers",
        accent_font="Bangers",
        size=86,
        accent_size=96,
        uppercase=True,
        accent="#FFE600",
        outline_width=6,
        shadow=4,
        rotate=-2,
        accent_scale=1.15,
    ),
    # 7 ------------------------------------------------------------------
    "bubble_luckiest": _style(
        "Bubble Pop",
        font="Luckiest Guy",
        accent_font="Luckiest Guy",
        size=78,
        accent_size=88,
        uppercase=True,
        accent="#FF4FA3",
        outline_width=6,
        shadow=4,
        accent_scale=1.12,
    ),
    # 8 ------------------------------------------------------------------
    "luxury_serif": _style(
        "Luxury Serif",
        font="Cinzel",
        accent_font="Cinzel",
        size=68,
        accent_size=76,
        uppercase=True,
        accent="#E8C46A",
        outline="#1A1200",
        outline_width=3,
        shadow=2,
        spacing=1.0,
        accent_scale=1.08,
    ),
    # 9 ------------------------------------------------------------------
    "retro_pixel": _style(
        "Retro Pixel",
        font="Press Start 2P",
        accent_font="Press Start 2P",
        size=44,
        accent_size=48,
        uppercase=True,
        primary="#7CFF6B",
        accent="#FFE600",
        outline_width=4,
        shadow=0,
        background=True,
        background_color="#000000",
        background_opacity=0.65,
        box_padding=18,
        accent_scale=1.08,
        max_words=2,
        max_chars=12,
    ),
    # 10 -----------------------------------------------------------------
    "marker_hand": _style(
        "Marker Hand",
        font="Permanent Marker",
        accent_font="Permanent Marker",
        size=78,
        accent_size=86,
        uppercase=False,
        accent="#FFD54A",
        outline_width=4,
        shadow=2,
        rotate=-1,
        accent_scale=1.10,
    ),
    # 11 -----------------------------------------------------------------
    "script_lobster": _style(
        "Script Lobster",
        font="Lobster",
        accent_font="Lobster",
        size=82,
        accent_size=92,
        uppercase=False,
        accent="#FF6B6B",
        outline="#200000",
        outline_width=3,
        shadow=3,
        accent_scale=1.12,
    ),
    # 12 -----------------------------------------------------------------
    "clean_minimal": _style(
        "Clean Minimal",
        font="Inter",
        accent_font="Inter",
        size=66,
        accent_size=70,
        uppercase=False,
        accent="#9BE7FF",
        outline_width=0,
        shadow=6,
        spacing=0.2,
        accent_scale=1.06,
    ),
    # 13 -----------------------------------------------------------------
    "boxed_podcast": _style(
        "Boxed Podcast",
        font="Montserrat",
        accent_font="Montserrat",
        size=62,
        accent_size=68,
        uppercase=True,
        accent="#FFD166",
        outline_width=0,
        shadow=0,
        background=True,
        background_color="#000000",
        background_opacity=0.62,
        box_padding=20,
        accent_scale=1.06,
    ),
    # 14 -----------------------------------------------------------------
    "rainbow_party": _style(
        "Rainbow Party",
        font="Poppins",
        accent_font="Poppins",
        size=76,
        accent_size=86,
        uppercase=True,
        accent="#FF3B6B",
        outline_width=5,
        shadow=0,
        rainbow=True,
        accent_colors=[
            "#FF3B6B", "#FFD400", "#00E5FF",
            "#7CFF6B", "#B388FF", "#FF8A3D",
        ],
        accent_scale=1.12,
    ),
    # 15 -----------------------------------------------------------------
    "electric_blue": _style(
        "Electric Blue",
        font="Archivo Black",
        accent_font="Archivo Black",
        size=74,
        accent_size=82,
        uppercase=True,
        accent="#3D8BFF",
        outline="#000B2A",
        outline_width=5,
        shadow=0,
        glow=True,
        glow_strength=18,
        accent_scale=1.12,
    ),
    # 16 -----------------------------------------------------------------
    "vhs_glitch": _style(
        "VHS Glitch",
        font="Space Grotesk",
        accent_font="Space Grotesk",
        size=74,
        accent_size=80,
        uppercase=True,
        accent="#FF00E5",
        outline_width=2,
        shadow=0,
        spacing=1.0,
        chromatic_shift=3,
        accent_scale=1.08,
    ),
    # 17 -----------------------------------------------------------------
    "sports_impact": _style(
        "Sports Impact",
        font="Anton",
        accent_font="Anton",
        size=88,
        accent_size=98,
        uppercase=True,
        accent="#FF3B3B",
        outline_width=6,
        shadow=3,
        accent_scale=1.14,
    ),
    # 18 -----------------------------------------------------------------
    "pastel_cute": _style(
        "Pastel Cute",
        font="Righteous",
        accent_font="Righteous",
        size=72,
        accent_size=80,
        uppercase=False,
        primary="#FFF7FB",
        accent="#FF9EC4",
        outline="#5A2A4A",
        outline_width=3,
        shadow=3,
        glow=True,
        glow_strength=10,
        accent_scale=1.10,
    ),
    # 19 -----------------------------------------------------------------
    "gold_glow": _style(
        "Gold Glow",
        font="Poppins",
        accent_font="Cinzel",
        size=74,
        accent_size=82,
        uppercase=True,
        accent="#FFD700",
        outline="#2A1A00",
        outline_width=3,
        shadow=0,
        glow=True,
        glow_strength=20,
        accent_scale=1.12,
    ),
    # 20 -----------------------------------------------------------------
    "mono_terminal": _style(
        "Mono Terminal",
        font="Roboto Mono",
        accent_font="Roboto Mono",
        size=54,
        accent_size=58,
        uppercase=True,
        primary="#D8FFE0",
        accent="#00FF66",
        outline_width=2,
        shadow=0,
        background=True,
        background_color="#000000",
        background_opacity=0.75,
        box_padding=12,
        accent_scale=1.05,
        max_words=3,
        max_chars=16,
    ),
}


ANIMATIONS = {
    "pop_highlight": {
        "label": "Pop Highlight",
        "desc": "Active word pops bigger with the accent font.",
    },
    "bounce": {
        "label": "Bounce",
        "desc": "Active word bounces with a quick overshoot.",
    },
    "slide_up": {
        "label": "Slide Up",
        "desc": "Every new line slides up and fades in.",
    },
    "fade_in": {
        "label": "Fade In",
        "desc": "Every new line fades in smoothly.",
    },
    "typewriter": {
        "label": "Typewriter",
        "desc": "Words appear one by one as they are spoken.",
    },
    "zoom_pulse": {
        "label": "Zoom Pulse",
        "desc": "Active word pulses with a slow zoom.",
    },
    "shake": {
        "label": "Shake",
        "desc": "Active word shakes with a quick tilt.",
    },
    "wave": {
        "label": "Wave",
        "desc": "Active word bobs up and down.",
    },
    "karaoke_fill": {
        "label": "Karaoke Fill",
        "desc": "Spoken words fill with the accent color.",
    },
    "static": {
        "label": "Static",
        "desc": "No motion, only a clean color highlight.",
    },
    # 10 NEW ANIMATIONS
    "elastic": {
        "label": "Elastic",
        "desc": "Active word stretches and snaps back like a rubber band.",
    },
    "spiral": {
        "label": "Spiral",
        "desc": "Active word rotates in a spiral motion while scaling.",
    },
    "flip": {
        "label": "Flip",
        "desc": "Active word flips 3D-style to reveal accent color.",
    },
    "glitch": {
        "label": "Glitch",
        "desc": "Active word glitches with RGB channel separation.",
    },
    "pulse": {
        "label": "Pulse",
        "desc": "Active word breathes with a smooth scaling pulse.",
    },
    "wave_vertical": {
        "label": "Vertical Wave",
        "desc": "Words flow up and down in a vertical sine wave.",
    },
    "typewriter_reveal": {
        "label": "Typewriter Reveal",
        "desc": "Each character types out with cursor effect.",
    },
    "highlight_sweep": {
        "label": "Highlight Sweep",
        "desc": "Accent color sweeps across the word like a spotlight.",
    },
    "shake_3d": {
        "label": "3D Shake",
        "desc": "Active word shakes in 3D with perspective tilt.",
    },
    "rainbow_shift": {
        "label": "Rainbow Shift",
        "desc": "Active word cycles through rainbow colors.",
    },
}


CAPTION_EFFECTS = {
    "none": {
        "label": "None",
        "desc": "No additional effect.",
    },
    "neon_glow": {
        "label": "Neon Glow",
        "desc": "Vibrant neon glow around text with customizable color.",
        "glow": True,
        "glow_strength": 20,
        "glow_blur": 12,
    },
    "fire_glow": {
        "label": "Fire Glow",
        "desc": "Warm fire-like glow with flicker animation.",
        "glow": True,
        "glow_color": "#FF4500",
        "glow_strength": 24,
        "glow_blur": 16,
    },
    "ice_glow": {
        "label": "Ice Glow",
        "desc": "Cool blue-white glow with frosted edges.",
        "glow": True,
        "glow_color": "#00FFFF",
        "glow_strength": 18,
        "glow_blur": 14,
    },
    "rgb_shift": {
        "label": "RGB Shift",
        "desc": "Chromatic aberration with red/cyan channel separation.",
        "chromatic_shift": 4,
    },
    "scanlines": {
        "label": "Scanlines",
        "desc": "Retro CRT scanline overlay on text.",
        "scanlines": True,
        "scanline_opacity": 0.3,
    },
    "vignette": {
        "label": "Vignette",
        "desc": "Darkened edges with bright center focus.",
        "vignette": True,
        "vignette_strength": 0.4,
    },
    "stroke_outline": {
        "label": "Stroke Outline",
        "desc": "Thick multi-layer outline for high contrast.",
        "outline_width": 8,
        "outline_layers": 3,
    },
    "drop_shadow": {
        "label": "Drop Shadow",
        "desc": "Deep shadow with offset for 3D depth.",
        "shadow": 8,
        "shadow_offset": 4,
    },
    "chromatic_aberration": {
        "label": "Chromatic Aberration",
        "desc": "Strong RGB split with animated shift.",
        "chromatic_shift": 6,
        "chromatic_animate": True,
    },
    "halftone": {
        "label": "Halftone",
        "desc": "Comic-book halftone dot pattern overlay.",
        "halftone": True,
        "halftone_size": 4,
    },
}


CAPTION_POSITIONS = {
    "top_left": {"label": "Top Left", "x": 0.18, "y": 0.18},
    "top_center": {"label": "Top Center", "x": 0.50, "y": 0.18},
    "top_right": {"label": "Top Right", "x": 0.82, "y": 0.18},
    "mid_left": {"label": "Mid Left", "x": 0.18, "y": 0.50},
    "mid_center": {"label": "Center", "x": 0.50, "y": 0.50},
    "mid_right": {"label": "Mid Right", "x": 0.82, "y": 0.50},
    "bottom_left": {"label": "Bottom Left", "x": 0.18, "y": 0.76},
    "bottom_center": {"label": "Bottom Center", "x": 0.50, "y": 0.76},
    "bottom_right": {"label": "Bottom Right", "x": 0.82, "y": 0.76},
    "custom": {"label": "Custom", "x": 0.50, "y": 0.76},
}
