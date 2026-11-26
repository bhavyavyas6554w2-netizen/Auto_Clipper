"""
Facecam layout engine.

Modes:
  auto, fullscreen, split_top, split_bottom, half_top, half_bottom,
  circle, square, rounded

The source facecam is cropped from the original video (AI box or 9-grid
preset), then placed on the 1080x1920 canvas. `size` controls the split
height / overlay width, `ratio` controls the crop aspect, and
`overlay_position` controls where circle/square/rounded overlays sit.
"""

import json
import subprocess

FACECAM_MODES = {
    "auto": {"label": "Auto (AI)", "desc": "AI detects the facecam; split top if found, otherwise fullscreen."},
    "fullscreen": {"label": "Fullscreen", "desc": "No facecam box, gameplay fills the whole Short."},
    "split_top": {"label": "Split Top", "desc": "Facecam on top, gameplay below (the original style)."},
    "split_bottom": {"label": "Split Bottom", "desc": "Gameplay on top, facecam below (the opposite style)."},
    "half_top": {"label": "Half Top", "desc": "Facecam takes the top half, gameplay the bottom half."},
    "half_bottom": {"label": "Half Bottom", "desc": "Gameplay takes the top half, facecam the bottom half."},
    "circle": {"label": "Circle", "desc": "Circular facecam overlay on fullscreen gameplay."},
    "square": {"label": "Square", "desc": "Square facecam overlay on fullscreen gameplay."},
    "rounded": {"label": "Smooth Square", "desc": "Rounded-corner facecam overlay on fullscreen gameplay."},
}

SOURCE_POSITIONS = {
    "auto": None,
    "top_left": (0.0, 0.0),
    "top_center": (0.5, 0.0),
    "top_right": (1.0, 0.0),
    "mid_left": (0.0, 0.5),
    "center": (0.5, 0.5),
    "mid_right": (1.0, 0.5),
    "bottom_left": (0.0, 1.0),
    "bottom_center": (0.5, 1.0),
    "bottom_right": (1.0, 1.0),
}

OVERLAY_POSITIONS = {k: v for k, v in SOURCE_POSITIONS.items() if k != "auto"}

RATIOS = {
    "auto": None,
    "16:9": 16.0 / 9.0,
    "4:3": 4.0 / 3.0,
    "1:1": 1.0,
    "3:4": 3.0 / 4.0,
    "9:16": 9.0 / 16.0,
    "21:9": 21.0 / 9.0,
}


def _even(value):
    return max(2, int(round(float(value) / 2.0)) * 2)


def _clamp(value, low, high):
    return max(low, min(high, value))


def get_video_info(path):
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=width,height", "-of", "json", path,
            ],
            capture_output=True, text=True, timeout=30,
        )
        data = json.loads(result.stdout or "{}")
        stream = (data.get("streams") or [{}])[0]
        width = int(stream.get("width") or 1920)
        height = int(stream.get("height") or 1080)
        if width > 0 and height > 0:
            return width, height
    except Exception:
        pass
    return 1920, 1080


def _default_ratio(cam_cfg):
    ratio_name = cam_cfg.get("ratio", "auto")
    if ratio_name in RATIOS and RATIOS[ratio_name]:
        return RATIOS[ratio_name]
    if cam_cfg.get("mode") in ("circle", "square", "rounded"):
        return 1.0
    return 16.0 / 9.0


def _preset_box(info, position, crop_size, ratio):
    width, height = info
    anchor = SOURCE_POSITIONS.get(position) or (0.5, 0.5)
    ax, ay = anchor

    crop_w = max(32.0, float(crop_size) * width)
    crop_h = crop_w / max(0.1, ratio)

    if crop_h > height * 0.72:
        crop_h = height * 0.72
        crop_w = crop_h * ratio
    if crop_w > width * 0.72:
        crop_w = width * 0.72
        crop_h = crop_w / max(0.1, ratio)

    x = ax * (width - crop_w)
    y = ay * (height - crop_h)
    return {
        "x": _clamp(x / width, 0.0, 1.0),
        "y": _clamp(y / height, 0.0, 1.0),
        "w": _clamp(crop_w / width, 0.01, 1.0),
        "h": _clamp(crop_h / height, 0.01, 1.0),
    }


def _fit_box_to_ratio(box, info, ratio):
    width, height = info
    x = box["x"] * width
    y = box["y"] * height
    w = box["w"] * width
    h = box["h"] * height
    if w <= 0 or h <= 0:
        return box

    cx, cy = x + w / 2.0, y + h / 2.0
    current = w / h
    if current > ratio:
        w = h * ratio
    else:
        h = w / ratio

    if w > width:
        w = width
        h = w / ratio
    if h > height:
        h = height
        w = h * ratio

    x = _clamp(cx - w / 2.0, 0.0, width - w)
    y = _clamp(cy - h / 2.0, 0.0, height - h)
    return {
        "x": x / width,
        "y": y / height,
        "w": w / width,
        "h": h / height,
    }


def compute_crop(info, cam_cfg, auto_box=None):
    """Return a pixel crop dict {x,y,w,h,ratio} or None (no facecam)."""
    width, height = info
    source_position = cam_cfg.get("source_position", "auto")
    ratio = _default_ratio(cam_cfg)

    if source_position == "auto":
        if isinstance(auto_box, dict):
            box = auto_box
            if cam_cfg.get("ratio", "auto") == "auto":
                box_ratio = (box["w"] * width) / max(1.0, box["h"] * height)
                ratio = box_ratio
        elif auto_box == "FULLSCREEN":
            return None
        else:
            box = _preset_box(info, "mid_left", cam_cfg.get("crop_size", 0.30), ratio)
    else:
        box = _preset_box(
            info, source_position, cam_cfg.get("crop_size", 0.30), ratio
        )

    if cam_cfg.get("ratio", "auto") != "auto":
        box = _fit_box_to_ratio(box, info, ratio)

    x = int(round(box["x"] * width))
    y = int(round(box["y"] * height))
    w = _even(box["w"] * width)
    h = _even(box["h"] * height)

    x = int(_clamp(x, 0, max(0, width - w)))
    y = int(_clamp(y, 0, max(0, height - h)))
    return {"x": x, "y": y, "w": w, "h": h, "ratio": ratio}


def _rounded_alpha(width, height, radius):
    radius = max(0.0, min(radius, min(width, height) / 2.0))
    if radius <= 0.5:
        return None
    half_w, half_h = width / 2.0, height / 2.0
    inner_w, inner_h = max(0.0, half_w - radius), max(0.0, half_h - radius)
    return (
        f"255*clip(({radius:.2f}-hypot("
        f"max(0,abs(X-{half_w:.2f})-{inner_w:.2f}),"
        f"max(0,abs(Y-{half_h:.2f})-{inner_h:.2f})))/1.5,0,1)"
    )


def _ass_suffix(ass_path):
    if not ass_path:
        return ""
    safe = ass_path.replace("\\", "/").replace(":", r"\:")
    return f",ass={safe}:fontsdir=."


def build_facecam_filter(info, cam_cfg, auto_box=None, ass_path=None, out_w=1080, out_h=1920):
    """Build the ffmpeg filter_complex string. Returns (graph, details)."""
    mode = cam_cfg.get("mode", "auto")
    if mode == "auto":
        mode = "fullscreen" if auto_box == "FULLSCREEN" else "split_top"

    if mode == "fullscreen":
        graph = (
            f"[0:v]scale={out_w}:{out_h}:force_original_aspect_ratio=increase,"
            f"crop={out_w}:{out_h},setsar=1{_ass_suffix(ass_path)},format=yuv420p[v]"
        )
        return graph, {"mode": "fullscreen", "crop": None}

    crop = compute_crop(info, cam_cfg, auto_box)
    if crop is None:
        graph = (
            f"[0:v]scale={out_w}:{out_h}:force_original_aspect_ratio=increase,"
            f"crop={out_w}:{out_h},setsar=1{_ass_suffix(ass_path)},format=yuv420p[v]"
        )
        return graph, {"mode": "fullscreen", "crop": None}

    crop_str = f"crop={crop['w']}:{crop['h']}:{crop['x']}:{crop['y']}"
    size = _clamp(float(cam_cfg.get("size", 0.30)), 0.10, 0.60)
    border = bool(cam_cfg.get("border", True)) and int(cam_cfg.get("border_width", 4)) > 0
    border_w = int(cam_cfg.get("border_width", 4)) if border else 0
    border_color = "0x" + str(cam_cfg.get("border_color", "#FFFFFF")).lstrip("#")

    if mode in ("split_top", "split_bottom", "half_top", "half_bottom"):
        face_h = _even(out_h * size)
        face_h = int(_clamp(face_h, 120, out_h - 120))
        game_h = out_h - face_h

        face_chain = (
            f"[0:v]{crop_str},scale={out_w}:{face_h}:force_original_aspect_ratio=increase,"
            f"crop={out_w}:{face_h},setsar=1"
        )
        if border:
            box_y = face_h - border_w if mode in ("split_top", "half_top") else 0
            face_chain += (
                f",drawbox=x=0:y={box_y}:w={out_w}:h={border_w}:"
                f"color={border_color}:t=fill"
            )
        face_chain += "[face]"

        game_chain = (
            f"[0:v]scale={out_w}:{game_h}:force_original_aspect_ratio=increase,"
            f"crop={out_w}:{game_h},setsar=1[game]"
        )

        if mode in ("split_top", "half_top"):
            graph = f"{face_chain};{game_chain};[face][game]vstack=inputs=2"
        else:
            graph = f"{game_chain};{face_chain};[game][face]vstack=inputs=2"
        graph += _ass_suffix(ass_path) + ",format=yuv420p[v]"
        return graph, {
            "mode": mode, "crop": crop, "face_h": face_h, "game_h": game_h,
        }

    # Overlay modes: circle / square / rounded
    box_w = _even(out_w * size)
    if mode == "circle":
        box_h = box_w
        radius = box_w / 2.0
    elif mode == "square":
        box_h = box_w
        radius = 0.0
    else:
        ratio = crop["ratio"] if cam_cfg.get("ratio", "auto") == "auto" else _default_ratio(cam_cfg)
        box_h = _even(box_w / max(0.2, ratio))
        radius = float(cam_cfg.get("corner_radius", 28))

    radius = _clamp(radius, 0.0, min(box_w, box_h) / 2.0)

    face_chain = (
        f"[0:v]{crop_str},scale={box_w}:{box_h}:force_original_aspect_ratio=increase,"
        f"crop={box_w}:{box_h},setsar=1,format=rgba"
    )
    alpha_expr = _rounded_alpha(box_w, box_h, radius)
    if alpha_expr:
        face_chain += (
            f",geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='{alpha_expr}'"
        )

    bg_chain = (
        f"[0:v]scale={out_w}:{out_h}:force_original_aspect_ratio=increase,"
        f"crop={out_w}:{out_h},setsar=1[bg]"
    )

    margin = max(16, int(out_w * 0.03))
    position = cam_cfg.get("overlay_position", "top_right")
    row, col = position.split("_", 1) if "_" in position else ("center", "center")
    if position == "center":
        col, row = "center", "center"
    x = {"left": margin, "center": (out_w - box_w) // 2, "right": out_w - box_w - margin}.get(col, (out_w - box_w) // 2)
    y = {"top": margin, "mid": (out_h - box_h) // 2, "bottom": out_h - box_h - margin}.get(row, margin)

    ring = ""
    if border:
        if mode == "square":
            face_chain += (
                f",pad=w={box_w + 2 * border_w}:h={box_h + 2 * border_w}:"
                f"x={border_w}:y={border_w}:color={border_color}"
            )
            x -= border_w
            y -= border_w
        else:
            ring_w, ring_h = box_w + 2 * border_w, box_h + 2 * border_w
            ring_radius = radius + border_w
            ring_alpha = _rounded_alpha(ring_w, ring_h, ring_radius)
            ring = (
                f"color=c={border_color}:s={ring_w}x{ring_h}:d=1,format=rgba,"
                f"geq=r='255':g='255':b='255':a='{ring_alpha}'[ring];"
            )

    face_chain += "[face]"
    if ring:
        graph = (
            f"{ring}{bg_chain};{face_chain};[bg][ring]overlay={x - border_w}:{y - border_w}[bg2];"
            f"[bg2][face]overlay={x}:{y}"
        )
    else:
        graph = f"{bg_chain};{face_chain};[bg][face]overlay={x}:{y}"
    graph += _ass_suffix(ass_path) + ",format=yuv420p[v]"
    return graph, {
        "mode": mode, "crop": crop, "box_w": box_w, "box_h": box_h,
        "radius": radius, "x": x, "y": y,
    }
