<div align="center">

# ⚡ Auto Clipper — 100% Free AI YouTube Shorts Cloud Pipeline

**Turn long YouTube videos & ended livestreams into viral, auto-captioned Shorts automatically every single day — on GitHub Actions ($0 Server Cost).**

[![GitHub Stars](https://img.shields.io/github/stars/sunitavyas271983-hub/auto_clipper?style=for-the-badge&color=ff3b6b)](https://github.com/sunitavyas271983-hub/auto_clipper/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/sunitavyas271983-hub/auto_clipper?style=for-the-badge&color=00d4ff)](https://github.com/sunitavyas271983-hub/auto_clipper/network/members)
[![License: MIT](https://img.shields.io/github/license/sunitavyas271983-hub/auto_clipper?style=for-the-badge&color=a855f7)](LICENSE)
![100% Free](https://img.shields.io/badge/Cost-$0%20Free%20Cloud-22c55e?style=for-the-badge)

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automated-2088FF?style=flat-square&logo=github-actions&logoColor=white)
![Gemini AI](https://img.shields.io/badge/Gemini_AI-Viral_Clip_Finder-8E75B2?style=flat-square&logo=google-gemini&logoColor=white)
![Whisper AI](https://img.shields.io/badge/Faster_Whisper-Word_Captions-10A37F?style=flat-square)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Auto_9:16_Render-007808?style=flat-square&logo=ffmpeg&logoColor=white)

<br />

**[🚀 Use This Template](https://github.com/sunitavyas271983-hub/auto_clipper/generate) · [🎨 Config Studio (GitHub Pages)](https://sunitavyas271983-hub.github.io/auto_clipper/) · [📖 Setup Guide](#-quick-setup-guide) · [🍪 Cookie Survival](#-cookie-survival-guide) · [🐛 Report Bug](https://github.com/sunitavyas271983-hub/auto_clipper/issues)**

</div>

---

## 🎬 Live Output Demo

> **Before/After Shorts examples** — place your rendered Shorts in `assets/demo.mp4` and uncomment below.

```markdown
![Demo](assets/demo.mp4)
```

---

## 🧠 How the Pipeline Works

```mermaid
graph LR
    A[8 YouTube Channels] -->|YouTube Data API| B[Rank by Views & Filter English/AI-Dub]
    B -->|Transcript / Heatmap| C[Gemini AI Viral Clip Finder]
    C --> D[50-50 Smart Queue: 3 Fresh + 3 Pending]
    D -->|yt-dlp + Whisper + FFmpeg| E[Auto Facecam Crop + Mixed-Font Glow Captions]
    E -->|YouTube API| F[Auto-Schedule Every 10 Min from 7 PM]
    D -->|10+ Days Old| G[Render & Backup to Google Drive + Gmail Alert]
```

---

## ✨ All Features

### 🎯 Core Pipeline
| Feature | What It Does |
| :--- | :--- |
| **☁️ 100% Cloud & Free** | Runs daily on GitHub Actions — your PC/laptop can stay completely off. |
| **🎯 Zero-Cookie Scanning** | Scans target channels sequentially via YouTube Data API, skips live streams, grabs ended lives + normal videos, and ranks by views. |
| **🌐 English & AI-Dub Filter** | Automatically filters native English videos or non-English videos that have an English AI-dub audio track. |
| **⚖️ 50-50 Smart Queue** | Publishes **3 fresh (today's)** + **3 pending (oldest-first)** clips daily, with automatic fallback if fresh clips are fewer than 3. |
| **⏰ Smart Auto-Scheduling** | Schedules up to 6 Shorts starting at **7:00 PM IST** with a **10-minute gap**. |
| **💾 10-Day Drive + Email Backup** | Unused clips older than 10 days are rendered, archived to Google Drive, and emailed to you with direct links. |

### 🎥 9 Facecam Layouts (NEW)
| Mode | Description | Best For |
| :--- | :--- | :--- |
| `auto` | AI picks `split_top` or `fullscreen` | Default, hands-off |
| `fullscreen` | Facecam fills entire 9:16 frame | IRL streams, vlogs |
| `split_top` | Facecam top 33%, gameplay bottom 67% | Standard gaming stream |
| `split_bottom` | Gameplay top 67%, facecam bottom 33% | Reaction videos |
| `half_top` | 50/50 split, facecam top | Equal emphasis |
| `half_bottom` | 50/50 split, facecam bottom | Streamer overlay at bottom |
| `circle` | Circular facecam overlay (corner) | Modern streamer style |
| `square` | Square facecam overlay (corner) | Clean boxy look |
| `rounded` | Rounded-square overlay (corner) | Soft, friendly aesthetic |

**All layouts support:**
- Configurable **overlay position** (9 corners: top/mid/bottom × left/center/right)
- Configurable **source position** (where the facecam sits in the original video)
- Configurable **size** (12%–55% of output)
- Configurable **aspect ratio** (auto, 16:9, 4:3, 1:1, 3:4, 9:16, 21:9)
- **Corner radius**, **border**, **border color/width**
- **AI auto-detect** with Gemini Vision (falls back to preset positions)

### 🔥 20 Caption Styles + 10 Animations (NEW)

**Caption Styles** (each with font, colors, glow, background, spacing):
| Style | Font | Vibe |
| :--- | :--- | :--- |
| `editorial_glow` | Poppins + Playfair | **Default** — bold editorial with italic accent glow |
| `neon_cyber` | Orbitron / Rajdhani | Cyberpunk neon pink/cyan |
| `typewriter_mono` | Space Mono / Roboto Mono | Retro terminal monospace |
| `comic_pop` | Bangers / Luckiest Guy | Comic-book shouty |
| `minimal_clean` | Inter / DM Sans | Clean modern UI |
| `retro_vhs` | VT323 / Press Start 2P | VHS glitch, chromatic aberration |
| `cinematic_wide` | Cinzel / Marcellus | Movie trailer scope |
| `bold_block` | Anton / Archivo Black | Thick high-contrast block |
| `gradient_flow` | Poppins / Montserrat | Rainbow gradient fill |
| `karaoke_sync` | Rubik / Nunito | Karaoke progressive fill |
| `handwritten` | Permanent Marker / Amatic SC | Hand-drawn marker |
| `glitch_fx` | Monoton / Rubik Glitch | Digital corruption |
| `elegant_serif` | Playfair Display / Libre Baskerville | Classy editorial |
| `arcade_pixel` | Press Start 2P / VT323 | 8-bit arcade |
| `news_ticker` | Roboto Condensed / Inter | Breaking news banner |
| `manga_shout` | Bangers / Luckiest Guy | Manga sound effects |
| `soft_dream` | Quicksand / Nunito | Pastel kawaii |
| `graffiti_tag` | Permanent Marker / Nosifer | Street art tags |
| `horror_drip` | Creepster / Eater | Blood drip horror |
| `sci_fi_hud` | Rajdhani / Orbitron | Sci-fi HUD overlay |

**Caption Animations** (per-word or per-line):
| Animation | Effect |
| :--- | :--- |
| `pop_highlight` | ✨ Active word pops + font/color change |
| `bounce` | 🏀 Elastic bounce on appear |
| `slide_up` | ⬆️ Line slides up into view |
| `fade_in` | 🌫️ Gentle cross-fade |
| `typewriter` | ⌨️ One word at a time |
| `zoom_pulse` | 🔍 Subtle zoom pulse |
| `shake` | 📳 Micro shake |
| `wave` | 🌊 Vertical wave motion |
| `karaoke_fill` | 🎤 Progressive fill like karaoke |
| `static` | ▫️ No animation (instant) |
| `elastic` | 🔁 Rubber-band stretch & snap |
| `spiral` | 🌀 Rotating spiral scale |
| `flip` | 🔄 3D flip reveal |
| `glitch` | 📺 Digital corruption glitch |
| `pulse` | 💓 Breathing scale pulse |
| `wave_vertical` | 〰️ Vertical sine wave motion |
| `typewriter_reveal` | ⌨️ Per-character typewriter |
| `highlight_sweep` | 💡 Color sweep highlight |
| `shake_3d` | 📦 3D perspective shake |
| `rainbow_shift` | 🌈 Hue-rotate color cycle |

**Caption Positions** (9 presets + custom X/Y + pixel offsets):
`top_left` · `top_center` · `top_right` · `mid_left` · `mid_center` · `mid_right` · `bottom_left` · `bottom_center` · `bottom_right` · `custom`

### ✨ 10 Caption Effects (NEW)
Combinable with any style — adds glow, scanlines, vignette, chromatic aberration, and more:
| Effect | Description |
| :--- | :--- |
| `neon_glow` | Vibrant neon glow with customizable color |
| `fire_glow` | Warm fire-like glow with flicker |
| `ice_glow` | Cool blue-white frosted glow |
| `rgb_shift` | Chromatic aberration (red/cyan split) |
| `scanlines` | Retro CRT scanline overlay |
| `vignette` | Darkened edges with center focus |
| `stroke_outline` | Thick multi-layer outline |
| `drop_shadow` | Deep 3D drop shadow |
| `chromatic_aberration` | Animated RGB channel separation |
| `halftone` | Comic-book halftone dot pattern |

### 🛡️ Cookie Survival System (NEW)
| Problem | Solution |
| :--- | :--- |
| Single cookie expires → whole run dies | **Tier 1: PO Token (cookie-free)** via `bgutil-ytdlp-pot-provider` — works for 95% of videos without any cookies |
| GitHub IP blocked → "Sign in to confirm you're not a bot" | **Multi-tier fallback**: PO Token → 3 Cookie sets → No-cookie clients → Proxy |
| Can't tell if cookie is broken | **Daily health check workflow** tests all strategies + **GitHub issue auto-creation** on total failure |
| Residential IP needed | **Optional `YT_PROXY`** support (applied to all tiers) |
| Age-gated content | Cookies automatically used only when PO Token fails (age-restricted videos) |

**Strategy Priority (tried in order):**
```
Tier 1 (Cookie-free):  PO Token + tv_embedded → android → ios → web → mweb
Tier 2 (Cookies):      YT_COOKIES → YT_COOKIES_2 → YT_COOKIES_3 (auto-rotation)
Tier 3 (No-cookie):    android/ios → web_safari → web
Tier 4 (Last resort):  Failed cookies + web_safari client
```

---

## 🚀 Quick Setup Guide

### Step 1: Copy This Template (Private Repo)
1. Click the green **Use this template** → **Create a new repository** button at the top of this page.
2. Set visibility to **Private** (keeps your logs and clip queue hidden).
3. Go to **Settings → Actions → General → Workflow permissions**, enable **Read and write permissions**, and click **Save**.

> **Why Private?** Your clip queue (`clip_queue.json`), scan state (`scanned_state.json`), and cookies stay out of public logs. GitHub Actions minutes are free for private repos on all plans.

### Step 2: Google Cloud APIs & Credentials
1. Create a project in [Google Cloud Console](https://console.cloud.google.com/).
2. Enable **YouTube Data API v3**, **Google Drive API**, and **Gmail API**.
3. Set up **OAuth Consent Screen** (External) and add your Gmail under **Test users**.
4. In **Credentials**, create:
   - **API Key** → `YT_API_KEY`
   - **OAuth Client ID (Web App)** with redirect URI `https://developers.google.com/oauthplayground` → `YT_CLIENT_ID` & `YT_CLIENT_SECRET`

### Step 3: Generate 2 Refresh Tokens (OAuth 2.0 Playground)
Open [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/), click **Settings (⚙️)**, check **Use your own OAuth credentials**, and enter your Client ID & Secret.

> **Important:** Generate YouTube and Drive/Gmail tokens **separately** (combining them triggers Google `Error 400`).

1. **`YT_REFRESH_TOKEN`**: Authorize scope `https://www.googleapis.com/auth/youtube.upload` → Exchange → Copy `refresh_token`.
2. **`DRIVE_GMAIL_REFRESH_TOKEN`**: Authorize scopes `https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/gmail.send` → Exchange → Copy `refresh_token`.

### Step 4: Export Cookies (`YT_COOKIES` + Optional `YT_COOKIES_2`, `YT_COOKIES_3`)
1. Use a **dummy Gmail account** (never your main channel).
2. Enable **Get cookies.txt LOCALLY** browser extension in **Incognito mode**.
3. Log in to YouTube in Incognito → visit `https://www.youtube.com/robots.txt` in the same tab → export **Netscape `.txt`** → close Incognito **without clicking Sign Out**.
3. Paste the **entire file content** as secret `YT_COOKIES`.
4. **Optional but recommended:** Repeat with a second dummy account for `YT_COOKIES_2` (and third for `YT_COOKIES_3`). The pipeline auto-rotates them.
5. **Optional:** Add `YT_PROXY` (e.g., `http://user:pass@host:port`) for residential proxy if GitHub IPs are blocked.

### Step 5: Add 11 GitHub Secrets
Go to your Private repo's **Settings → Secrets and variables → Actions → New repository secret**:

| Secret Name | Required? | Purpose |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | ✅ | Free API key from [Google AI Studio](https://aistudio.google.com/) |
| `YT_API_KEY` | ✅ | YouTube Data API v3 Key |
| `YT_CLIENT_ID` | ✅ | Google OAuth Client ID |
| `YT_CLIENT_SECRET` | ✅ | Google OAuth Client Secret |
| `YT_REFRESH_TOKEN` | ✅ | Refresh token for `youtube.upload` |
| `DRIVE_GMAIL_REFRESH_TOKEN` | ✅ | Refresh token for `drive.file` + `gmail.send` |
| `YT_COOKIES` | ✅ | Full Netscape `cookies.txt` content (Account 1) |
| `YT_COOKIES_2` | 🔄 | Account 2 cookies for rotation |
| `YT_COOKIES_3` | 🔄 | Account 3 cookies for rotation |
| `YT_PROXY` | ⭕ | Residential proxy URL (optional) |
| `ALERT_EMAIL` | ✅ | Your Gmail for 10-day Drive backup alerts |

### Step 6: Enable GitHub Pages for Config Studio (Optional)
1. Go to **Settings → Pages** → **Build and deployment** → Source: **Deploy from a branch** → Branch: `main` / Folder: `/docs` → **Save**.
2. Your Config Studio will be live at `https://<your-username>.github.io/auto_clipper/`.
3. Or just open `docs/index.html` locally in any browser — no server needed!

### Step 7: Run the Pipeline
1. Go to **Actions → Auto YouTube Shorts Pipeline → Run workflow**.
2. Optionally override caption style, facecam layout, etc. from the workflow inputs.
3. Watch the logs — first Short renders in ~2–3 minutes.

---

## ⚙️ Configuration Reference (`config.json`)

The pipeline reads `config.json` at repo root. You can edit it manually, or use the **Config Studio** (GitHub Pages / local `docs/index.html`) to generate it visually.

```json
{
  "captions": {
    "enabled": true,
    "style": "editorial_glow",
    "animation": "pop_highlight",
    "effect": "none",
    "effect_intensity": 1.0,
    "position": "bottom_center",
    "custom_x": 0.5,
    "custom_y": 0.76,
    "offset_x": 0,
    "offset_y": 0,
    "font_size": null,
    "max_words": null,
    "max_chars": null,
    "uppercase": null,
    "primary_color": null,
    "accent_color": null,
    "outline_color": null,
    "outline_width": null,
    "glow": null,
    "background": null,
    "background_color": null,
    "background_opacity": null
  },
  "facecam": {
    "mode": "auto",
    "source_position": "auto",
    "overlay_position": "top_right",
    "crop_size": 0.3,
    "size": 0.3,
    "ratio": "auto",
    "corner_radius": 28,
    "border": true,
    "border_color": "#FFFFFF",
    "border_width": 4,
    "background_color": "#000000",
    "auto_detect": true
  },
  "video": {
    "width": 1080,
    "height": 1920,
    "fps": 30,
    "crf": 23,
    "preset": "fast"
  }
}
```

### Field Guide

#### `captions`
| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `enabled` | bool | `true` | Master toggle for captions |
| `style` | string | `editorial_glow` | One of 20 style IDs |
| `animation` | string | `pop_highlight` | One of 20 animation IDs |
| `effect` | string | `none` | One of 10 effect IDs |
| `effect_intensity` | float 0.1–3.0 | `1.0` | Effect strength multiplier |
| `position` | string | `bottom_center` | One of 9 presets or `custom` |
| `custom_x` | float 0–1 | `0.5` | X for `custom` position |
| `custom_y` | float 0–1 | `0.76` | Y for `custom` position |
| `offset_x` | int px | `0` | Pixel nudge X |
| `offset_y` | int px | `0` | Pixel nudge Y |
| `font_size` | int/null | `null` | Override style base size (px on 1080 canvas) |
| `max_words` | int/null | `null` | Words per line (1–6) |
| `max_chars` | int/null | `null` | Chars per line (8–30) |
| `uppercase` | bool/null | `null` | Force uppercase |
| `primary_color` | hex/null | `null` | Main text color |
| `accent_color` | hex/null | `null` | Active word color |
| `outline_color` | hex/null | `null` | Stroke color |
| `outline_width` | float/null | `null` | Stroke width |
| `glow` | bool/null | `null` | Enable glow |
| `background` | bool/null | `null` | Box behind text |
| `background_color` | hex/null | `null` | Box color |
| `background_opacity` | float 0–1/null | `null` | Box opacity |

#### `facecam`
| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `mode` | enum | `auto` | `auto\|fullscreen\|split_top\|split_bottom\|half_top\|half_bottom\|circle\|square\|rounded` |
| `source_position` | enum | `auto` | Where facecam is in source (AI auto-detect or 9 positions) |
| `overlay_position` | enum | `top_right` | Where overlay sits in 9:16 output (9 positions) |
| `crop_size` | float 0.1–0.6 | `0.3` | Source crop fraction |
| `size` | float 0.1–0.55 | `0.3` | Output size fraction (split height / overlay width) |
| `ratio` | enum | `auto` | `auto\|16:9\|4:3\|1:1\|3:4\|9:16\|21:9` |
| `corner_radius` | int 0–300 | `28` | Rounded corner px (circle=50% auto) |
| `border` | bool | `true` | Show border |
| `border_color` | hex | `#FFFFFF` | Border color |
| `border_width` | int 0–30 | `4` | Border px |
| `background_color` | hex | `#000000` | Fallback bg for circle/square |
| `auto_detect` | bool | `true` | Use Gemini Vision to find facecam |

#### `video`
| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `width` | int | `1080` | Output width |
| `height` | int | `1920` | Output height |
| `fps` | int | `30` | 30 or 60 |
| `crf` | int 14–35 | `23` | Quality (lower=better) |
| `preset` | enum | `fast` | `ultrafast`…`slow` |

---

## 🎨 Config Studio (Visual Builder)

A zero-dependency static site in `docs/` — works on **GitHub Pages** or by double-clicking `docs/index.html`.

### Features
- **Live 9:16 phone preview** with gameplay gradient, facecam overlay, animated caption simulation
- **20 style cards** with live font/color samples
- **20 animation cards** with icons
- **10 effect cards** with icons (neon glow, fire, ice, RGB shift, scanlines, vignette, stroke, drop shadow, chromatic aberration, halftone)
- **9 position grid** + fine-tune X/Y sliders
- **9 facecam layout cards** with mini diagrams
- **Source/overlay position grids** + size/ratio/corner-radius controls
- **Upload your own screenshots** for realistic preview
- **One-click `config.json` copy/download**
- **Save directly to your private repo** via GitHub REST API (Fine-Grained PAT stored in browser localStorage)
- **Hindi/English help** built in

### Deploy to GitHub Pages
1. Repo **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` → Folder: `/docs`
4. Save → wait ~1 minute
5. Visit `https://<your-username>.github.io/auto_clipper/`

> **Private repo caveat:** GitHub Pages on private repos requires a paid GitHub plan (Pro/Team/Enterprise). On free accounts, either make the repo public or just open `docs/index.html` locally — it works 100% offline.

### 💾 Save to Repo (GitHub API)
The Config Studio can commit `config.json` directly to your private repo:

1. **Generate a Fine-Grained PAT** at [GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens](https://github.com/settings/personal-access-tokens/new)
   - **Repository access**: Select your private repo only
   - **Permissions**: Contents → **Read & Write**
   - **Expiration**: 90 days recommended
2. In Config Studio → **Export tab** → **Save to Repo** section:
   - Owner/Repo auto-filled on GitHub Pages, or enter manually
   - Paste your PAT (stored only in browser `localStorage`)
   - Check "Remember PAT in browser" to persist
   - Click **Save config.json to Repo** → commits to `main` branch
3. Next workflow run uses the new config automatically!

> **Security**: PAT never leaves your browser. No server involved. Clear anytime with "Clear saved PAT".

---

## 🍪 Cookie Survival Guide

### Why Cookies Break
- YouTube expires cookies after ~2–4 weeks of inactivity
- GitHub Actions runs on Microsoft Azure IPs → flagged as "bot"
- Incognito mode clears cookies on close → export **before** closing

### Bulletproof Setup
1. **Use a dedicated dummy Google account** (not your main channel).
2. **Enable "Get cookies.txt LOCALLY"** (Firefox/Chrome extension).
3. **Open Incognito → Log in → Visit `youtube.com/robots.txt` → Export → Close Incognito.**
   - Do **NOT** click "Sign out" — that invalidates the cookie instantly.
4. Paste full file content as `YT_COOKIES` secret.
5. **Add `YT_COOKIES_2` from a second dummy account** — auto-rotation doubles cookie lifetime.
6. **Optional:** Add `YT_PROXY` (residential proxy) if GitHub IPs are blocked.

### How Rotation Works
```
Run starts
   ├─ Try last-working cookie set (sticky)
   ├─ Try other cookie sets (YT_COOKIES_2, YT_COOKIES_3)
   ├─ Try no-cookie + android/ios client
   ├─ Try no-cookie + web_safari client
   └─ All fail → write cookie_alert.json → GitHub Issue created automatically
```

### Daily Health Check
The `cookie-health.yml` workflow runs daily at 11:30 AM IST:
- Tests all configured cookie sets against a stable public video
- Uploads `cookie_status.json` as artifact (30-day retention)
- Opens a GitHub Issue if **every** set fails

### Emergency Fix
If you see "Sign in to confirm you're not a bot" in logs:
1. Export fresh cookies from Incognito (new dummy account works best)
2. Update `YT_COOKIES` (and `YT_COOKIES_2`/`YT_COOKIES_3`) in GitHub Secrets
3. Re-run the workflow — no code changes needed

---

## 🛠️ Project Structure

```
auto_clipper/
├── .github/
│   └── workflows/
│       ├── main.yml              # Daily pipeline + manual triggers
│       └── cookie-health.yml     # Daily cookie health check
├── docs/                         # Config Studio (GitHub Pages)
│   ├── index.html                # UI
│   ├── style.css                 # Dark theme, responsive
│   ├── app.js                    # State, preview, export
│   ├── data.js                   # Auto-generated from Python presets
│   └── .nojekyll                 # Bypass Jekyll on Pages
├── tools/
│   └── build_web_data.py         # Regenerates docs/data.js
├── scripts/
│   └── check_cookies.py          # Standalone cookie health check
├── config.json                   # User-editable config (or from Studio)
├── process_video.py              # Main pipeline entry point
├── clipper_config.py             # Config loader + env overrides
├── caption_styles.py             # 20 styles, 20 animations, 10 effects, 9 positions
├── caption_engine.py             # ASS caption renderer
├── facecam_layouts.py            # 9 layouts, filter graph builder
├── cookie_manager.py             # Multi-cookie rotation + fallbacks
├── requirements.txt
├── clip_queue.json               # Auto-managed (git tracked)
├── scanned_state.json            # Auto-managed (git tracked)
└── README.md
```

---

## 🔧 Advanced: Workflow Inputs (Manual Runs)

When you click **Run workflow**, you can override any config value:

| Input | Values | Overrides |
| :--- | :--- | :--- |
| `video_url` | URL or empty | Single video instead of channel scan |
| `facecam_pos` | `auto` + 6 positions | Fallback source position |
| `max_uploads_now` | 1–10 | Shorts per run |
| `lookback_hours` | 1–168 | Scan window |
| `publish_mode` | `schedule_7pm` \| `public_now` | Scheduling |
| `caption_style` | 20 style IDs + empty | `captions.style` |
| `caption_animation` | 20 anim IDs + empty | `captions.animation` |
| `caption_effect` | 10 effect IDs + empty | `captions.effect` |
| `caption_effect_intensity` | 0.1–3.0 + empty | `captions.effect_intensity` |
| `caption_position` | 9 positions + `custom` + empty | `captions.position` |
| `facecam_mode` | 9 mode IDs + empty | `facecam.mode` |
| `facecam_size` | 0.12–0.55 + empty | `facecam.size` |
| `facecam_ratio` | `auto` + 6 ratios + empty | `facecam.ratio` |

---

## 🐛 Troubleshooting

| Symptom | Fix |
| :--- | :--- |
| `BotBlockError` / "Sign in to confirm" | Refresh cookies, add `YT_COOKIES_2`, set `YT_PROXY` |
| `ModuleNotFoundError` | Check `requirements.txt` — all deps in workflow install step |
| Fonts missing in captions | Workflow downloads 16 Google Fonts — re-run if network flaked |
| Facecam not detected | Set `facecam.source_position` preset, disable `auto_detect` |
| Shorts not scheduling | Check `PUBLISH_MODE`, YouTube API quota, `YT_REFRESH_TOKEN` validity |
| Drive archive fails | Verify `DRIVE_GMAIL_REFRESH_TOKEN` scopes (`drive.file` + `gmail.send`) |

---

## 📜 License

Released under the **MIT License** — free to use, modify, and build upon. If this saves you hours of editing, a ⭐ Star is always appreciated!

---

## 🙏 Credits

- **Gemini AI** — Viral clip selection
- **Faster Whisper** — Word-level transcription
- **yt-dlp** — Robust YouTube downloading
- **FFmpeg** — 9:16 rendering, facecam compositing
- **Google Fonts** — 16 typefaces for caption styles
- **GitHub Actions** — Free cloud compute

---

<div align="center">
<b>Made with ❤️ for creators who want to post Shorts daily without editing.</b><br>
<a href="https://github.com/sunitavyas271983-hub/auto_clipper/generate"><b>Use This Template →</b></a>
</div>