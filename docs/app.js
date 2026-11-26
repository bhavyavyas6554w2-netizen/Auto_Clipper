/* Auto Clipper Studio - static config builder */
(function () {
  "use strict";

  const D = window.CLIPPER_DATA;
  if (!D) {
    document.body.innerHTML = "<p style='padding:40px;color:white'>data.js missing. Run <code>python tools/build_web_data.py</code>.</p>";
    return;
  }

  const $ = (id) => document.getElementById(id);

  const FONT_MAP = {
    "Poppins": "'Poppins', sans-serif",
    "Playfair Display": "'Playfair Display', serif",
    "Montserrat": "'Montserrat', sans-serif",
    "DM Serif Display": "'Playfair Display', serif",
    "Anton": "'Anton', sans-serif",
    "Bebas Neue": "'Bebas Neue', sans-serif",
    "Bangers": "'Bangers', cursive",
    "Luckiest Guy": "'Luckiest Guy', cursive",
    "Cinzel": "'Cinzel', serif",
    "Press Start 2P": "'Press Start 2P', monospace",
    "Permanent Marker": "'Permanent Marker', cursive",
    "Lobster": "'Lobster', cursive",
    "Inter": "'Inter', sans-serif",
    "Archivo Black": "'Archivo Black', sans-serif",
    "Space Grotesk": "'Space Grotesk', sans-serif",
    "Righteous": "'Righteous', sans-serif",
    "Roboto Mono": "'Roboto Mono', monospace",
  };

  const ANIM_ICONS = {
    pop_highlight: "✨",
    bounce: "🏀",
    slide_up: "⬆️",
    fade_in: "🌫️",
    typewriter: "⌨️",
    zoom_pulse: "🔍",
    shake: "📳",
    wave: "🌊",
    karaoke_fill: "🎤",
    static: "▫️",
    elastic: "🔁",
    spiral: "🌀",
    flip: "🔄",
    glitch: "📺",
    pulse: "💓",
    wave_vertical: "〰️",
    typewriter_reveal: "⌨️",
    highlight_sweep: "💡",
    shake_3d: "📦",
    rainbow_shift: "🌈",
  };

  const EFFECT_ICONS = {
    none: "✖️",
    neon_glow: "💜",
    fire_glow: "🔥",
    ice_glow: "❄️",
    rgb_shift: "📺",
    scanlines: "📟",
    vignette: "🔘",
    stroke_outline: "⬜",
    drop_shadow: "🌑",
    chromatic_aberration: "🌈",
    halftone: "📰",
  };

  const PHRASE = ["THIS", "IS", "HOW", "YOUR", "CAPTIONS", "LOOK"];
  const POSITION_KEYS = [
    "top_left", "top_center", "top_right",
    "mid_left", "mid_center", "mid_right",
    "bottom_left", "bottom_center", "bottom_right",
  ];
  const POSITION_POINTS = {
    top_left: [0.18, 0.18], top_center: [0.50, 0.18], top_right: [0.82, 0.18],
    mid_left: [0.18, 0.50], mid_center: [0.50, 0.50], mid_right: [0.82, 0.50],
    bottom_left: [0.18, 0.78], bottom_center: [0.50, 0.78], bottom_right: [0.82, 0.78],
  };
  const ANCHORS = {
    top_left: [0, 0], top_center: [0.5, 0], top_right: [1, 0],
    mid_left: [0, 0.5], center: [0.5, 0.5], mid_right: [1, 0.5],
    bottom_left: [0, 1], bottom_center: [0.5, 1], bottom_right: [1, 1],
  };

  const state = {
    captions: JSON.parse(JSON.stringify(D.defaults.captions)),
    facecam: JSON.parse(JSON.stringify(D.defaults.facecam)),
    video: JSON.parse(JSON.stringify(D.defaults.video)),
    captionGroup: 0,
    captionWord: 0,
  };

  let imageUrls = { gameplay: "", facecam: "" };
  let captionTimer = null;

  /* ------------------------------------------------------------------ */
  /* Helpers                                                            */
  /* ------------------------------------------------------------------ */

  function cssFont(name) {
    return FONT_MAP[name] || "'Inter', sans-serif";
  }

  function hexToRgba(hex, alpha) {
    const value = (hex || "#000000").replace("#", "");
    const full = value.length === 3 ? value.split("").map((c) => c + c).join("") : value;
    const r = parseInt(full.slice(0, 2), 16) || 0;
    const g = parseInt(full.slice(2, 4), 16) || 0;
    const b = parseInt(full.slice(4, 6), 16) || 0;
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }

  function resolvedStyle() {
    const base = D.styles[state.captions.style] || D.styles[D.defaultStyle];
    const c = state.captions;
    const s = Object.assign({}, base);

    if (c.font_size != null) {
      const ratio = Number(c.font_size) / Math.max(1, base.size);
      s.size = Number(c.font_size);
      s.accent_size = Math.round(base.accent_size * ratio);
    }
    if (c.max_words != null) s.max_words = Number(c.max_words);
    if (c.max_chars != null) s.max_chars = Number(c.max_chars);
    if (c.uppercase != null) s.uppercase = Boolean(c.uppercase);
    if (c.primary_color != null) s.primary = c.primary_color;
    if (c.accent_color != null) s.accent = c.accent_color;
    if (c.outline_color != null) s.outline = c.outline_color;
    if (c.outline_width != null) s.outline_width = Number(c.outline_width);
    if (c.glow != null) s.glow = Boolean(c.glow);
    if (c.background != null) s.background = Boolean(c.background);
    if (c.background_color != null) s.background_color = c.background_color;
    if (c.background_opacity != null) s.background_opacity = Number(c.background_opacity);

    if (!s.glow_color) s.glow_color = s.accent;
    return s;
  }

  function captionPoint() {
    const c = state.captions;
    let x = 0.5;
    let y = 0.78;
    if (c.position === "custom") {
      x = Number(c.custom_x);
      y = Number(c.custom_y);
    } else if (POSITION_POINTS[c.position]) {
      [x, y] = POSITION_POINTS[c.position];
    }
    return [
      Math.max(0.05, Math.min(0.95, x + Number(c.offset_x || 0) / 1080)),
      Math.max(0.05, Math.min(0.95, y + Number(c.offset_y || 0) / 1920)),
    ];
  }

  function effectiveLayout() {
    if (state.facecam.mode !== "auto") return state.facecam.mode;
    return "split_top";
  }

  function isOverlay(mode) {
    return mode === "circle" || mode === "square" || mode === "rounded";
  }

  function ratioValue() {
    const raw = state.facecam.ratio;
    if (raw === "auto") return null;
    const parts = raw.split(":").map(Number);
    return parts[0] / parts[1];
  }

  /* ------------------------------------------------------------------ */
  /* Card rendering                                                     */
  /* ------------------------------------------------------------------ */

  function applySampleStyle(el, style) {
    el.style.fontFamily = cssFont(style.font);
    el.style.color = style.primary;
    el.style.fontSize = "18px";
    el.style.fontWeight = style.bold ? "800" : "500";
    el.style.fontStyle = style.italic ? "italic" : "normal";
    el.style.textTransform = style.uppercase ? "uppercase" : "none";
    el.style.letterSpacing = `${style.spacing * 0.3}px`;
    el.style.transform = `rotate(${style.rotate}deg)`;
    el.style.webkitTextStroke = `${Math.min(2, style.outline_width * 0.3)}px ${style.outline}`;
    el.style.textShadow = style.glow
      ? `0 0 ${Math.min(12, style.glow_strength)}px ${style.glow_color || style.accent}, ${style.shadow * 0.3}px ${style.shadow * 0.3}px 0 ${style.outline}`
      : `${style.shadow * 0.3}px ${style.shadow * 0.3}px 0 ${style.outline}`;
    if (style.background) {
      el.style.background = hexToRgba(style.background_color, style.background_opacity);
      el.style.borderRadius = "5px";
    }
    if (style.rainbow && style.accent_colors && style.accent_colors.length) {
      el.style.color = style.accent_colors[0];
    }
  }

  function renderStyleCards() {
    const grid = $("styleGrid");
    grid.innerHTML = "";
    Object.entries(D.styles).forEach(([id, style]) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "style-card" + (state.captions.style === id ? " active" : "");
      btn.dataset.id = id;

      const sample = document.createElement("span");
      sample.className = "style-sample";
      sample.textContent = "WOW";
      applySampleStyle(sample, style);

      const name = document.createElement("span");
      name.className = "style-name";
      name.textContent = style.label;

      btn.append(sample, name);
      btn.addEventListener("click", () => selectStyle(id));
      grid.append(btn);
    });
  }

  function renderAnimationCards() {
    const grid = $("animationGrid");
    grid.innerHTML = "";
    Object.entries(D.animations).forEach(([id, anim]) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "anim-card" + (state.captions.animation === id ? " active" : "");
      btn.dataset.id = id;
      btn.title = anim.desc;

      const icon = document.createElement("span");
      icon.className = "anim-icon";
      icon.textContent = ANIM_ICONS[id] || "🎞️";

      const name = document.createElement("span");
      name.className = "anim-name";
      name.textContent = anim.label;

      btn.append(icon, name);
      btn.addEventListener("click", () => {
        state.captions.animation = id;
        renderAnimationCards();
        refresh();
      });
      grid.append(btn);
    });
  }

  function renderEffectCards() {
    const grid = $("effectGrid");
    grid.innerHTML = "";
    Object.entries(D.effects).forEach(([id, effect]) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "effect-card" + (state.captions.effect === id ? " active" : "");
      btn.dataset.id = id;
      btn.title = effect.desc;

      const icon = document.createElement("span");
      icon.className = "effect-icon";
      icon.textContent = EFFECT_ICONS[id] || "✨";

      const name = document.createElement("span");
      name.className = "effect-name";
      name.textContent = effect.label;

      btn.append(icon, name);
      btn.addEventListener("click", () => {
        state.captions.effect = id;
        renderEffectCards();
        refresh();
      });
      grid.append(btn);
    });
  }

  function layoutIcon(mode) {
    const icon = document.createElement("span");
    icon.className = "layout-icon";
    const face = document.createElement("i");
    const game = document.createElement("i");
    face.className = "face";
    game.className = "game";
    const set = (el, top, height, extra) => {
      el.style.left = "0";
      el.style.width = "100%";
      el.style.top = top;
      el.style.height = height;
      if (extra) Object.assign(el.style, extra);
    };

    if (mode === "fullscreen") {
      set(game, "0", "100%");
    } else if (mode === "split_top" || mode === "auto") {
      set(face, "0", "34%");
      set(game, "34%", "66%");
    } else if (mode === "split_bottom") {
      set(game, "0", "66%");
      set(face, "66%", "34%");
    } else if (mode === "half_top") {
      set(face, "0", "50%");
      set(game, "50%", "50%");
    } else if (mode === "half_bottom") {
      set(game, "0", "50%");
      set(face, "50%", "50%");
    } else {
      set(game, "0", "100%");
      face.style.width = "42%";
      face.style.height = "0";
      face.style.paddingTop = "42%";
      face.style.top = "8%";
      face.style.left = "50%";
      face.style.borderRadius = mode === "circle" ? "50%" : mode === "rounded" ? "6px" : "2px";
    }
    icon.append(game, face);
    return icon;
  }

  function renderLayoutCards() {
    const grid = $("layoutGrid");
    grid.innerHTML = "";
    Object.entries(D.facecamModes).forEach(([id, mode]) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "layout-card" + (state.facecam.mode === id ? " active" : "");
      btn.dataset.id = id;
      btn.title = mode.desc;
      btn.append(layoutIcon(id));
      const name = document.createElement("span");
      name.className = "layout-name";
      name.textContent = mode.label;
      btn.append(name);
      btn.addEventListener("click", () => selectLayout(id));
      grid.append(btn);
    });
  }

  function buildPosGrid(container, current, onPick) {
    container.innerHTML = "";
    POSITION_KEYS.forEach((key) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.dataset.pos = key;
      btn.className = current === key ? "active" : "";
      btn.title = key.replace(/_/g, " ");
      btn.addEventListener("click", () => onPick(key));
      container.append(btn);
    });
  }

  function renderPositionGrids() {
    buildPosGrid($("positionGrid"), state.captions.position, (key) => {
      state.captions.position = key;
      renderPositionGrids();
      refresh();
    });
    buildPosGrid($("sourceGrid"), state.facecam.source_position, (key) => {
      state.facecam.source_position = key;
      $("sourceAuto").checked = false;
      renderPositionGrids();
      refresh();
    });
    buildPosGrid($("overlayGrid"), state.facecam.overlay_position, (key) => {
      state.facecam.overlay_position = key;
      renderPositionGrids();
      refresh();
    });
  }

  /* ------------------------------------------------------------------ */
  /* Selection                                                          */
  /* ------------------------------------------------------------------ */

  function selectStyle(id) {
    state.captions.style = id;
    state.captions.font_size = null;
    state.captions.max_words = null;
    state.captions.max_chars = null;
    state.captions.uppercase = null;
    state.captions.primary_color = null;
    state.captions.accent_color = null;
    state.captions.outline_color = null;
    state.captions.outline_width = null;
    state.captions.glow = null;
    state.captions.background = null;
    state.captions.background_color = null;
    state.captions.background_opacity = null;
    renderStyleCards();
    syncControls();
    refresh();
    toast(`${D.styles[id].label} applied`);
  }

  function selectLayout(id) {
    state.facecam.mode = id;
    if (id === "half_top" || id === "half_bottom") {
      state.facecam.size = 0.5;
    } else if ((id === "split_top" || id === "split_bottom") && state.facecam.size === 0.5) {
      state.facecam.size = 0.33;
    } else if (isOverlay(id) && state.facecam.size > 0.45) {
      state.facecam.size = 0.3;
    }
    renderLayoutCards();
    syncControls();
    refresh();
  }

  /* ------------------------------------------------------------------ */
  /* Controls sync                                                      */
  /* ------------------------------------------------------------------ */

  function setRange(id, value, suffix) {
    const input = $(id);
    if (!input) return;
    input.value = value;
    const out = $(id + "Val");
    if (out) out.textContent = suffix ? `${value}${suffix}` : value;
  }

  function syncControls() {
    const s = resolvedStyle();
    setRange("fontSize", Math.round(s.size));
    setRange("maxWords", s.max_words);
    setRange("maxChars", s.max_chars);
    setRange("outlineWidth", s.outline_width);
    setRange("backgroundOpacity", Number(s.background_opacity).toFixed(2));

    $("uppercase").checked = Boolean(s.uppercase);
    $("glowToggle").checked = Boolean(s.glow);
    $("backgroundToggle").checked = Boolean(s.background);
    $("primaryColor").value = s.primary;
    $("accentColor").value = s.accent;
    $("outlineColor").value = s.outline;
    $("backgroundColor").value = s.background_color;

    setRange("offsetX", state.captions.offset_x);
    setRange("offsetY", state.captions.offset_y);

    $("effectIntensity").value = state.captions.effect_intensity;
    const out = $("effectIntensityVal");
    if (out) out.textContent = Number(state.captions.effect_intensity).toFixed(1);

    setRange("facecamSize", Math.round(state.facecam.size * 100), "%");
    setRange("cropSize", Math.round(state.facecam.crop_size * 100), "%");
    setRange("cornerRadius", state.facecam.corner_radius);
    setRange("borderWidth", state.facecam.border_width);
    $("facecamRatio").value = state.facecam.ratio;
    $("borderToggle").checked = Boolean(state.facecam.border);
    $("autoDetect").checked = Boolean(state.facecam.auto_detect);
    $("borderColor").value = state.facecam.border_color;
    $("sourceAuto").checked = state.facecam.source_position === "auto";

    $("resolution").value = `${state.video.width}x${state.video.height}`;
    $("fps").value = String(state.video.fps);
    setRange("crf", state.video.crf);
    $("preset").value = state.video.preset;
  }

  /* ------------------------------------------------------------------ */
  /* Preview                                                            */
  /* ------------------------------------------------------------------ */

  function applyGameplayImage() {
    const gameplay = $("gameplay");
    const sourceFrame = $("sourceFrame");
    if (imageUrls.gameplay) {
      gameplay.style.backgroundImage = `url("${imageUrls.gameplay}")`;
      sourceFrame.style.backgroundImage = `url("${imageUrls.gameplay}")`;
    } else {
      gameplay.style.backgroundImage = "";
      sourceFrame.style.backgroundImage = "";
    }
    const facecam = $("facecamLayer");
    if (imageUrls.facecam) {
      facecam.style.backgroundImage = `url("${imageUrls.facecam}")`;
    } else {
      facecam.style.backgroundImage = "";
    }
  }

  function renderPhoneLayout() {
    const mode = effectiveLayout();
    const cam = state.facecam;
    const phone = $("phone");
    const gameplay = $("gameplay");
    const facecam = $("facecamLayer");
    const phoneWidth = phone.clientWidth || 300;
    const scale = phoneWidth / 1080;
    const size = Number(cam.size);
    const border = cam.border ? Math.max(1, Number(cam.border_width) * scale) : 0;
    const borderColor = cam.border_color;
    const radius = Number(cam.corner_radius) * scale;

    $("layoutBadge").textContent = D.facecamModes[cam.mode] ? D.facecamModes[cam.mode].label : mode;

    gameplay.style.cssText = "position:absolute;background-size:cover;background-position:center;";
    gameplay.style.inset = "auto";
    facecam.style.display = "block";
    facecam.style.left = "0";
    facecam.style.top = "0";
    facecam.style.width = "100%";
    facecam.style.height = "100%";
    facecam.style.transform = "none";
    facecam.style.borderRadius = "0";
    facecam.style.boxShadow = "none";
    facecam.style.border = "0";

    if (mode === "fullscreen") {
      facecam.style.display = "none";
      gameplay.style.left = "0";
      gameplay.style.top = "0";
      gameplay.style.width = "100%";
      gameplay.style.height = "100%";
      applyGameplayImage();
      return;
    }

    if (mode === "split_top" || mode === "split_bottom" || mode === "half_top" || mode === "half_bottom") {
      const faceTop = mode === "split_bottom" || mode === "half_bottom";
      const facePct = Math.round(size * 1000) / 10;
      facecam.style.height = `${facePct}%`;
      facecam.style.top = faceTop ? `${100 - facePct}%` : "0";
      gameplay.style.left = "0";
      gameplay.style.width = "100%";
      gameplay.style.top = faceTop ? "0" : `${facePct}%`;
      gameplay.style.height = `${100 - facePct}%`;
      if (border) {
        facecam.style.boxShadow = faceTop
          ? `inset 0 ${border}px 0 0 ${borderColor}`
          : `inset 0 -${border}px 0 0 ${borderColor}`;
      }
      applyGameplayImage();
      return;
    }

    // Overlay modes
    gameplay.style.left = "0";
    gameplay.style.top = "0";
    gameplay.style.width = "100%";
    gameplay.style.height = "100%";
    const ratio = mode === "circle" || mode === "square" ? 1 : (ratioValue() || 1);
    const widthPct = Math.max(10, Math.min(70, size * 100));
    const heightPct = widthPct * (9 / 16) / ratio;
    const margin = 4;
    const pos = cam.overlay_position || "top_right";
    let x = 50;
    let y = 50;
    if (pos.includes("left")) x = margin + widthPct / 2;
    else if (pos.includes("right")) x = 100 - margin - widthPct / 2;
    if (pos.includes("top")) y = margin + heightPct / 2;
    else if (pos.includes("bottom")) y = 100 - margin - heightPct / 2;

    facecam.style.width = `${widthPct}%`;
    facecam.style.height = `${heightPct}%`;
    facecam.style.left = `${x}%`;
    facecam.style.top = `${y}%`;
    facecam.style.transform = "translate(-50%, -50%)";
    facecam.style.borderRadius = mode === "circle" ? "50%" : mode === "square" ? "0" : `${radius}px`;
    if (border) facecam.style.boxShadow = `inset 0 0 0 ${border}px ${borderColor}`;
    applyGameplayImage();
  }

  function renderCaptionFrame() {
    const s = resolvedStyle();
    const layer = $("captionLayer");
    const phone = $("phone");
    const phoneWidth = phone.clientWidth || 300;
    const scale = phoneWidth / 1080;
    const maxWords = Math.max(1, Number(s.max_words) || 3);
    const groups = [];
    for (let i = 0; i < PHRASE.length; i += maxWords) groups.push(PHRASE.slice(i, i + maxWords));
    if (!groups.length) return;

    if (state.captionGroup >= groups.length) state.captionGroup = 0;
    const group = groups[state.captionGroup];
    const active = state.captionWord % group.length;
    const animation = state.captions.animation;
    const isNewGroup = state.captionWord === 0;

    layer.innerHTML = "";
    layer.className = "caption-layer" + (s.background ? " boxed" : "");
    layer.style.fontFamily = cssFont(s.font);
    layer.style.fontSize = `${s.size * scale}px`;
    layer.style.fontWeight = s.bold ? "800" : "500";
    layer.style.fontStyle = s.italic ? "italic" : "normal";
    layer.style.letterSpacing = `${s.spacing * scale}px`;
    layer.style.color = s.primary;
    layer.style.textTransform = s.uppercase ? "uppercase" : "none";
    layer.style.webkitTextStroke = s.outline_width > 0 ? `${s.outline_width * scale}px ${s.outline}` : "0";
    layer.style.paintOrder = "stroke fill";
    layer.style.transform = `translate(-50%, -50%) rotate(${s.rotate}deg)`;

    const shadows = [];
    if (s.shadow > 0) shadows.push(`${s.shadow * scale}px ${s.shadow * scale}px 0 ${s.outline}`);
    if (s.glow) shadows.push(`0 0 ${s.glow_strength * scale}px ${s.glow_color || s.accent}`);
    if (s.chromatic_shift > 0) {
      shadows.push(`${s.chromatic_shift * scale}px 0 ${s.chromatic_shift * scale}px ${s.accent}`);
      shadows.push(`-${s.chromatic_shift * scale}px 0 ${s.chromatic_shift * scale}px #00e5ff`);
    }
    layer.style.textShadow = shadows.join(", ");

    if (s.background) {
      layer.style.background = hexToRgba(s.background_color, s.background_opacity);
      layer.style.padding = `${s.box_padding * scale}px ${s.box_padding * 1.4 * scale}px`;
      layer.style.borderRadius = `${Math.max(3, 8 * scale)}px`;
    } else {
      layer.style.background = "transparent";
      layer.style.padding = "0";
    }

    const [x, y] = captionPoint();
    layer.style.left = `${x * 100}%`;
    layer.style.top = `${y * 100}%`;

    const line = document.createElement("span");
    line.className = "cap-line";
    if (isNewGroup && (animation === "slide_up" || animation === "fade_in")) {
      line.classList.add(animation === "slide_up" ? "anim-slide" : "anim-fade");
    }

    const visibleCount = animation === "typewriter" ? active + 1 : group.length;
    group.slice(0, visibleCount).forEach((word, index) => {
      const span = document.createElement("span");
      span.className = "cap-word";
      span.textContent = word;

      const isActive = index === active;
      const isPast = index < active;
      if (isActive) span.classList.add("active");
      if (isPast) span.classList.add("past");

      let color = s.primary;
      if (s.rainbow && s.accent_colors && s.accent_colors.length) {
        color = s.accent_colors[index % s.accent_colors.length];
      }
      if (isActive || (animation === "karaoke_fill" && isPast)) color = s.accent;
      span.style.color = color;

      if (isActive) {
        span.style.fontFamily = cssFont(s.accent_font);
        span.style.fontSize = `${s.accent_size * scale}px`;
        span.style.fontStyle = s.accent_italic ? "italic" : "normal";
        span.style.fontWeight = s.accent_bold ? "800" : "500";
        if (animation === "pop_highlight" || animation === "karaoke_fill") span.classList.add("anim-pop");
        if (animation === "bounce") span.classList.add("anim-bounce");
        if (animation === "shake") span.classList.add("anim-shake");
        if (animation === "wave") span.classList.add("anim-wave");
        if (animation === "zoom_pulse") span.classList.add("anim-zoom");
        if (animation === "elastic") span.classList.add("anim-elastic");
        if (animation === "spiral") span.classList.add("anim-spiral");
        if (animation === "flip") span.classList.add("anim-flip");
        if (animation === "glitch") span.classList.add("anim-glitch");
        if (animation === "pulse") span.classList.add("anim-pulse");
        if (animation === "wave_vertical") span.classList.add("anim-wave-v");
        if (animation === "typewriter_reveal") span.classList.add("anim-typewriter-reveal");
        if (animation === "highlight_sweep") span.classList.add("anim-highlight-sweep");
        if (animation === "shake_3d") span.classList.add("anim-shake-3d");
        if (animation === "rainbow_shift") span.classList.add("anim-rainbow");
      } else if (isPast && animation === "karaoke_fill") {
        span.style.fontFamily = cssFont(s.accent_font);
        span.style.fontSize = `${s.accent_size * scale}px`;
      }

      line.append(span);
    });

    layer.append(line);
  }

  function renderSourceCrop() {
    const box = $("sourceCrop");
    const frame = $("sourceFrame");
    const auto = state.facecam.source_position === "auto";
    const pos = auto ? "center" : state.facecam.source_position;
    const anchor = ANCHORS[pos] || [0.5, 0.5];
    const ratio = ratioValue() || (isOverlay(effectiveLayout()) ? 1 : 16 / 9);
    const width = Math.max(12, Math.min(55, Number(state.facecam.crop_size) * 100));
    let height = width * (16 / 9) / ratio;
    height = Math.max(10, Math.min(72, height));
    const x = anchor[0] * (100 - width);
    const y = anchor[1] * (100 - height);

    box.style.left = `${x}%`;
    box.style.top = `${y}%`;
    box.style.width = `${width}%`;
    box.style.height = `${height}%`;
    box.style.borderStyle = auto ? "dashed" : "solid";
    box.style.borderColor = auto ? "#ffd400" : "#00e5ff";
    $("sourceLabel").textContent = auto ? "AI auto" : pos.replace(/_/g, " ");
    void frame.offsetWidth;
  }

  function refresh() {
    const s = resolvedStyle();
    const anim = D.animations[state.captions.animation];
    $("previewMeta").textContent = `${s.label} · ${anim ? anim.label : state.captions.animation}`;
    renderPhoneLayout();
    renderCaptionFrame();
    renderSourceCrop();
    renderPositionGrids();
    renderEffectCards();
    updateConfigOutput();
  }

  /* ------------------------------------------------------------------ */
  /* Config export                                                      */
  /* ------------------------------------------------------------------ */

  function round(value, digits) {
    const factor = Math.pow(10, digits || 3);
    return Math.round(Number(value) * factor) / factor;
  }

  function buildConfig() {
    const c = state.captions;
    const cam = state.facecam;
    return {
      captions: {
        enabled: Boolean(c.enabled),
        style: c.style,
        animation: c.animation,
        position: c.position,
        custom_x: round(c.custom_x),
        custom_y: round(c.custom_y),
        offset_x: Math.round(Number(c.offset_x) || 0),
        offset_y: Math.round(Number(c.offset_y) || 0),
        font_size: c.font_size == null ? null : Math.round(Number(c.font_size)),
        max_words: c.max_words == null ? null : Math.round(Number(c.max_words)),
        max_chars: c.max_chars == null ? null : Math.round(Number(c.max_chars)),
        uppercase: c.uppercase == null ? null : Boolean(c.uppercase),
        primary_color: c.primary_color,
        accent_color: c.accent_color,
        outline_color: c.outline_color,
        outline_width: c.outline_width == null ? null : Number(c.outline_width),
        glow: c.glow == null ? null : Boolean(c.glow),
        background: c.background == null ? null : Boolean(c.background),
        background_color: c.background_color,
        background_opacity: c.background_opacity == null ? null : round(c.background_opacity, 2),
      },
      facecam: {
        mode: cam.mode,
        source_position: cam.source_position,
        overlay_position: cam.overlay_position,
        crop_size: round(cam.crop_size),
        size: round(cam.size),
        ratio: cam.ratio,
        corner_radius: Math.round(Number(cam.corner_radius) || 0),
        border: Boolean(cam.border),
        border_color: cam.border_color,
        border_width: Math.round(Number(cam.border_width) || 0),
        background_color: cam.background_color,
        auto_detect: Boolean(cam.auto_detect),
      },
      video: {
        width: Number(state.video.width),
        height: Number(state.video.height),
        fps: Number(state.video.fps),
        crf: Number(state.video.crf),
        preset: state.video.preset,
      },
    };
  }

  function updateConfigOutput() {
    $("configOutput").textContent = JSON.stringify(buildConfig(), null, 2);
  }

  function githubEditLink() {
    const host = location.hostname;
    const parts = location.pathname.split("/").filter(Boolean);
    if (host.endsWith(".github.io")) {
      const owner = host.split(".")[0];
      const repo = parts[0] || "auto_clipper";
      return `https://github.com/${owner}/${repo}/edit/main/config.json`;
    }
    return "https://github.com/sunitavyas271983-hub/auto_clipper/edit/main/config.json";
  }

  function toast(message) {
    const el = $("toast");
    el.textContent = message;
    el.classList.add("show");
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => el.classList.remove("show"), 1800);
  }

  /* ------------------------------------------------------------------ */
  /* Event wiring                                                       */
  /* ------------------------------------------------------------------ */

  function bindRange(id, apply, suffix) {
    const input = $(id);
    input.addEventListener("input", () => {
      const value = Number(input.value);
      apply(value);
      const out = $(id + "Val");
      if (out) out.textContent = suffix ? `${value}${suffix}` : value;
      refresh();
    });
  }

  function bindCheckbox(id, apply) {
    $(id).addEventListener("change", (event) => {
      apply(event.target.checked);
      refresh();
    });
  }

  function bindColor(id, apply) {
    $(id).addEventListener("input", (event) => {
      apply(event.target.value);
      refresh();
    });
  }

  function wireControls() {
    bindRange("offsetX", (v) => { state.captions.offset_x = v; });
    bindRange("offsetY", (v) => { state.captions.offset_y = v; });
    bindRange("fontSize", (v) => { state.captions.font_size = v; });
    bindRange("maxWords", (v) => { state.captions.max_words = v; });
    bindRange("maxChars", (v) => { state.captions.max_chars = v; });
    bindRange("outlineWidth", (v) => { state.captions.outline_width = v; });
    bindRange("backgroundOpacity", (v) => { state.captions.background_opacity = v; });
    bindRange("effectIntensity", (v) => { state.captions.effect_intensity = v; });

    bindCheckbox("uppercase", (v) => { state.captions.uppercase = v; });
    bindCheckbox("glowToggle", (v) => { state.captions.glow = v; });
    bindCheckbox("backgroundToggle", (v) => { state.captions.background = v; });

    bindColor("primaryColor", (v) => { state.captions.primary_color = v; });
    bindColor("accentColor", (v) => { state.captions.accent_color = v; });
    bindColor("outlineColor", (v) => { state.captions.outline_color = v; });
    bindColor("backgroundColor", (v) => { state.captions.background_color = v; });

    bindRange("facecamSize", (v) => { state.facecam.size = v / 100; }, "%");
    bindRange("cropSize", (v) => { state.facecam.crop_size = v / 100; }, "%");
    bindRange("cornerRadius", (v) => { state.facecam.corner_radius = v; });
    bindRange("borderWidth", (v) => { state.facecam.border_width = v; });
    bindCheckbox("borderToggle", (v) => { state.facecam.border = v; });
    bindCheckbox("autoDetect", (v) => { state.facecam.auto_detect = v; });
    bindColor("borderColor", (v) => { state.facecam.border_color = v; });

    $("facecamRatio").addEventListener("change", (event) => {
      state.facecam.ratio = event.target.value;
      refresh();
    });
    $("sourceAuto").addEventListener("change", (event) => {
      state.facecam.source_position = event.target.checked ? "auto" : "mid_left";
      renderPositionGrids();
      refresh();
    });

    $("resolution").addEventListener("change", (event) => {
      const [w, h] = event.target.value.split("x").map(Number);
      state.video.width = w;
      state.video.height = h;
      refresh();
    });
    $("fps").addEventListener("change", (event) => { state.video.fps = Number(event.target.value); refresh(); });
    $("preset").addEventListener("change", (event) => { state.video.preset = event.target.value; refresh(); });
    bindRange("crf", (v) => { state.video.crf = v; });

    $("resetCaptions").addEventListener("click", () => {
      selectStyle(state.captions.style);
      toast("Style defaults restored");
    });

    $("copyConfig").addEventListener("click", async () => {
      const text = $("configOutput").textContent;
      try {
        await navigator.clipboard.writeText(text);
        toast("config.json copied");
      } catch (error) {
        const area = document.createElement("textarea");
        area.value = text;
        document.body.append(area);
        area.select();
        document.execCommand("copy");
        area.remove();
        toast("config.json copied");
      }
    });

    $("downloadConfig").addEventListener("click", () => {
      const blob = new Blob([$("configOutput").textContent], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "config.json";
      document.body.append(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      toast("config.json downloaded");
    });

    $("saveToRepo").addEventListener("click", async () => {
      const pat = $("githubPat").value.trim();
      const owner = $("repoOwner").value.trim();
      const repo = $("repoName").value.trim();
      if (!pat || !owner || !repo) {
        toast("Please enter PAT, owner, and repo name");
        return;
      }
      const configText = $("configOutput").textContent;
      try {
        // Get current file SHA
        const getRes = await fetch(
          `https://api.github.com/repos/${owner}/${repo}/contents/config.json?ref=main`,
          { headers: { Authorization: `Bearer ${pat}`, Accept: "application/vnd.github.v3+json" } }
        );
        if (!getRes.ok) throw new Error(`Failed to fetch current config: ${getRes.status}`);
        const { sha } = await getRes.json();

        // Update file
        const putRes = await fetch(
          `https://api.github.com/repos/${owner}/${repo}/contents/config.json`,
          {
            method: "PUT",
            headers: {
              Authorization: `Bearer ${pat}`,
              Accept: "application/vnd.github.v3+json",
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              message: "Update config.json from Config Studio",
              content: btoa(unescape(encodeURIComponent(configText))),
              sha,
              branch: "main",
            }),
          }
        );
        if (!putRes.ok) {
          const err = await putRes.text();
          throw new Error(`Failed to save: ${putRes.status} ${err}`);
        }
        toast("config.json saved to repo!");
        if ($("savePat").checked) localStorage.setItem("gh_pat", pat);
      } catch (error) {
        toast(`Error: ${error.message}`);
      }
    });

    // Load saved PAT from localStorage
    const savedPat = localStorage.getItem("gh_pat");
    if (savedPat) {
      $("githubPat").value = savedPat;
      $("savePat").checked = true;
    }

    // Auto-detect owner/repo from GitHub Pages URL
    if (location.hostname.endsWith(".github.io")) {
      const parts = location.pathname.split("/").filter(Boolean);
      if (parts.length >= 2) {
        $("repoOwner").value = location.hostname.split(".")[0];
        $("repoName").value = parts[0];
      }
    }

    $("gameplayUpload").addEventListener("change", (event) => {
      const file = event.target.files[0];
      if (!file) return;
      if (imageUrls.gameplay) URL.revokeObjectURL(imageUrls.gameplay);
      imageUrls.gameplay = URL.createObjectURL(file);
      applyGameplayImage();
    });
    $("facecamUpload").addEventListener("change", (event) => {
      const file = event.target.files[0];
      if (!file) return;
      if (imageUrls.facecam) URL.revokeObjectURL(imageUrls.facecam);
      imageUrls.facecam = URL.createObjectURL(file);
      applyGameplayImage();
    });
    $("clearImages").addEventListener("click", () => {
      Object.values(imageUrls).forEach((url) => { if (url) URL.revokeObjectURL(url); });
      imageUrls = { gameplay: "", facecam: "" };
      $("gameplayUpload").value = "";
      $("facecamUpload").value = "";
      applyGameplayImage();
      toast("Preview images cleared");
    });

    $("randomizeBtn").addEventListener("click", randomize);
  }

  function wireTabs() {
    document.querySelectorAll(".tab").forEach((tab) => {
      tab.addEventListener("click", () => {
        document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
        document.querySelectorAll(".tab-panel").forEach((p) => p.classList.add("hidden"));
        tab.classList.add("active");
        $("tab-" + tab.dataset.tab).classList.remove("hidden");
      });
    });
  }

  function randomize() {
    const styles = Object.keys(D.styles);
    const anims = Object.keys(D.animations);
    const effects = Object.keys(D.effects);
    const layouts = Object.keys(D.facecamModes);
    state.captions.style = styles[Math.floor(Math.random() * styles.length)];
    state.captions.animation = anims[Math.floor(Math.random() * anims.length)];
    state.captions.effect = effects[Math.floor(Math.random() * effects.length)];
    state.captions.position = POSITION_KEYS[Math.floor(Math.random() * POSITION_KEYS.length)];
    state.facecam.mode = layouts[Math.floor(Math.random() * layouts.length)];
    state.facecam.overlay_position = POSITION_KEYS[Math.floor(Math.random() * POSITION_KEYS.length)];
    state.facecam.size = [0.22, 0.28, 0.33, 0.4, 0.5][Math.floor(Math.random() * 5)];
    state.facecam.ratio = D.ratios[Math.floor(Math.random() * D.ratios.length)];
    state.captions.font_size = null;
    state.captions.max_words = null;
    state.captions.max_chars = null;
    state.captions.uppercase = null;
    state.captions.primary_color = null;
    state.captions.accent_color = null;
    state.captions.outline_color = null;
    state.captions.outline_width = null;
    state.captions.glow = null;
    state.captions.background = null;
    state.captions.background_color = null;
    state.captions.background_opacity = null;
    renderStyleCards();
    renderAnimationCards();
    renderEffectCards();
    renderLayoutCards();
    syncControls();
    refresh();
    toast("Random look generated");
  }

  /* ------------------------------------------------------------------ */
  /* Boot                                                               */
  /* ------------------------------------------------------------------ */

  function startCaptionLoop() {
    if (captionTimer) clearInterval(captionTimer);
    captionTimer = setInterval(() => {
      const s = resolvedStyle();
      const maxWords = Math.max(1, Number(s.max_words) || 3);
      const groupSize = Math.min(maxWords, PHRASE.length);
      state.captionWord += 1;
      if (state.captionWord >= groupSize) {
        state.captionWord = 0;
        state.captionGroup = (state.captionGroup + 1) % Math.ceil(PHRASE.length / groupSize);
      }
      renderCaptionFrame();
    }, 520);
  }

  function boot() {
    if (!D.styles[state.captions.style]) state.captions.style = D.defaultStyle;
    if (!D.animations[state.captions.animation]) state.captions.animation = D.defaultAnimation;

    renderStyleCards();
    renderAnimationCards();
    renderLayoutCards();
    renderPositionGrids();
    wireTabs();
    wireControls();
    syncControls();
    $("githubEditLink").href = githubEditLink();
    refresh();
    startCaptionLoop();
    applyGameplayImage();

    window.addEventListener("resize", () => {
      renderPhoneLayout();
      renderCaptionFrame();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
