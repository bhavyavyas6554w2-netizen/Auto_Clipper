"""
Config loader for Auto Clipper.

Reads config.json (created by the web Config Studio), deep-merges it over
safe defaults, then applies optional environment overrides from the
GitHub Actions workflow.
"""

import copy
import json
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

DEFAULT_CONFIG = {
    "captions": {
        "enabled": True,
        "style": DEFAULT_STYLE,
        "animation": DEFAULT_ANIMATION,
        "effect": DEFAULT_EFFECT,
        "effect_intensity": 1.0,
        "position": "bottom_center",
        "custom_x": 0.50,
        "custom_y": 0.76,
        "offset_x": 0,
        "offset_y": 0,
        # null = inherit the selected style's value
        "font_size": None,
        "max_words": None,
        "max_chars": None,
        "uppercase": None,
        "primary_color": None,
        "accent_color": None,
        "outline_color": None,
        "outline_width": None,
        "glow": None,
        "background": None,
        "background_color": None,
        "background_opacity": None,
    },
    "facecam": {
        "mode": "auto",              # auto|fullscreen|split_top|split_bottom|half_top|half_bottom|circle|square|rounded
        "source_position": "auto",   # auto|top_left|...|bottom_right
        "overlay_position": "top_right",
        "crop_size": 0.30,           # how much of the source video the facecam crop takes
        "size": 0.30,                # output size: split height fraction / overlay width fraction
        "ratio": "auto",             # auto|16:9|4:3|1:1|3:4|9:16|21:9
        "corner_radius": 28,
        "border": True,
        "border_color": "#FFFFFF",
        "border_width": 4,
        "background_color": "#000000",
        "auto_detect": True,
    },
    "video": {
        "width": 1080,
        "height": 1920,
        "fps": 30,
        "crf": 23,
        "preset": "fast",
    },
}

FACECAM_MODES = (
    "auto", "fullscreen", "split_top", "split_bottom",
    "half_top", "half_bottom", "circle", "square", "rounded",
)

SOURCE_POSITIONS = (
    "auto", "top_left", "top_center", "top_right",
    "mid_left", "center", "mid_right",
    "bottom_left", "bottom_center", "bottom_right",
)

OVERLAY_POSITIONS = (
    "top_left", "top_center", "top_right",
    "mid_left", "center", "mid_right",
    "bottom_left", "bottom_center", "bottom_right",
)

RATIOS = ("auto", "16:9", "4:3", "1:1", "3:4", "9:16", "21:9")


def _deep_merge(base, override):
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
    return base


def _as_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def _as_float(value, fallback):
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _env_override(cfg):
    """Workflow inputs override config.json only when explicitly provided."""
    cap = cfg["captions"]
    cam = cfg["facecam"]
    vid = cfg["video"]

    def pick(env_name, current):
        raw = os.environ.get(env_name, "").strip()
        if not raw or raw.lower() == "config":
            return current
        return raw

    cap["style"] = pick("CAPTION_STYLE", cap["style"])
    cap["animation"] = pick("CAPTION_ANIMATION", cap["animation"])
    cap["effect"] = pick("CAPTION_EFFECT", cap["effect"])
    cap["position"] = pick("CAPTION_POSITION", cap["position"])

    raw = os.environ.get("CAPTION_ENABLED", "").strip()
    if raw and raw.lower() != "config":
        cap["enabled"] = _as_bool(raw)

    raw = os.environ.get("CAPTION_EFFECT_INTENSITY", "").strip()
    if raw and raw.lower() != "config":
        cap["effect_intensity"] = _as_float(raw, cap["effect_intensity"])

    cam["mode"] = pick("FACECAM_MODE", cam["mode"])
    cam["source_position"] = pick("FACECAM_POS", cam["source_position"])
    cam["ratio"] = pick("FACECAM_RATIO", cam["ratio"])

    raw = os.environ.get("FACECAM_SIZE", "").strip()
    if raw and raw.lower() != "config":
        cam["size"] = _as_float(raw, cam["size"])

    raw = os.environ.get("FACECAM_AUTO_DETECT", "").strip()
    if raw and raw.lower() != "config":
        cam["auto_detect"] = _as_bool(raw)

    raw = os.environ.get("VIDEO_WIDTH", "").strip()
    if raw:
        vid["width"] = int(_as_float(raw, vid["width"]))
    raw = os.environ.get("VIDEO_HEIGHT", "").strip()
    if raw:
        vid["height"] = int(_as_float(raw, vid["height"]))
    raw = os.environ.get("VIDEO_FPS", "").strip()
    if raw:
        vid["fps"] = int(_as_float(raw, vid["fps"]))


def _validate(cfg):
    cap = cfg["captions"]
    cam = cfg["facecam"]
    vid = cfg["video"]

    if cap.get("style") not in CAPTION_STYLES:
        cap["style"] = DEFAULT_STYLE
    if cap.get("animation") not in ANIMATIONS:
        cap["animation"] = DEFAULT_ANIMATION
    if cap.get("effect") not in CAPTION_EFFECTS:
        cap["effect"] = DEFAULT_EFFECT
    if cap.get("position") not in CAPTION_POSITIONS:
        cap["position"] = "bottom_center"

    cap["custom_x"] = min(1.0, max(0.0, _as_float(cap.get("custom_x"), 0.5)))
    cap["custom_y"] = min(1.0, max(0.0, _as_float(cap.get("custom_y"), 0.76)))
    cap["offset_x"] = int(_as_float(cap.get("offset_x"), 0))
    cap["offset_y"] = int(_as_float(cap.get("offset_y"), 0))
    cap["effect_intensity"] = min(3.0, max(0.1, _as_float(cap.get("effect_intensity"), 1.0)))

    if cam.get("mode") not in FACECAM_MODES:
        cam["mode"] = "auto"
    if cam.get("source_position") not in SOURCE_POSITIONS:
        cam["source_position"] = "auto"
    if cam.get("overlay_position") not in OVERLAY_POSITIONS:
        cam["overlay_position"] = "top_right"
    if cam.get("ratio") not in RATIOS:
        cam["ratio"] = "auto"

    cam["size"] = min(0.60, max(0.10, _as_float(cam.get("size"), 0.30)))
    cam["crop_size"] = min(0.60, max(0.10, _as_float(cam.get("crop_size"), 0.30)))
    cam["corner_radius"] = min(300, max(0, int(_as_float(cam.get("corner_radius"), 28))))
    cam["border_width"] = min(30, max(0, int(_as_float(cam.get("border_width"), 4))))

    vid["width"] = min(2160, max(360, int(_as_float(vid.get("width"), 1080))))
    vid["height"] = min(3840, max(640, int(_as_float(vid.get("height"), 1920))))
    vid["fps"] = min(60, max(15, int(_as_float(vid.get("fps"), 30))))
    vid["crf"] = min(35, max(14, int(_as_float(vid.get("crf"), 23))))
    if vid.get("preset") not in ("ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow"):
        vid["preset"] = "fast"

    return cfg


def load_config(path="config.json"):
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                user_cfg = json.load(f)
            if isinstance(user_cfg, dict):
                _deep_merge(cfg, user_cfg)
        except Exception as exc:
            print(f"Config warning: could not read {path}: {exc}")
    _env_override(cfg)
    return _validate(cfg)
