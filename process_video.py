import sys
import os
import re
import glob
import json
import time
import base64
import subprocess
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
import requests
from faster_whisper import WhisperModel
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

from clipper_config import load_config
from caption_engine import build_ass
from facecam_layouts import build_facecam_filter, get_video_info
from cookie_manager import CookieManager, is_bot_error

CONFIG = load_config()
COOKIE_MANAGER = CookieManager()

VIDEO_URL = os.environ.get("VIDEO_URL", "").strip()
FACECAM_POS = (
    os.environ.get("FACECAM_POS", CONFIG["facecam"]["source_position"]).strip()
    or CONFIG["facecam"]["source_position"]
)
MAX_UPLOADS = int(os.environ.get("MAX_UPLOADS", "6") or "6")
LOOKBACK_HOURS = int(os.environ.get("LOOKBACK_HOURS", "25") or "25")
PUBLISH_MODE = os.environ.get("PUBLISH_MODE", "schedule_7pm").strip() or "schedule_7pm"
SCHEDULE_GAP_MINUTES = int(os.environ.get("SCHEDULE_GAP_MINUTES", "10") or "10")
ARCHIVE_AFTER_DAYS = int(os.environ.get("ARCHIVE_AFTER_DAYS", "10") or "10")
MAX_ARCHIVE_PER_RUN = int(os.environ.get("MAX_ARCHIVE_PER_RUN", "5") or "5")
ALERT_EMAIL = os.environ.get("ALERT_EMAIL", "").strip()
DRIVE_ARCHIVE_FOLDER = "AutoShorts_10Day_Archive"
MAX_SCAN_VIDEOS_PER_RUN = 20

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
YT_API_KEY = os.environ.get("YT_API_KEY", "").strip()

QUEUE_FILE = "clip_queue.json"
STATE_FILE = "scanned_state.json"
WHISPER_MODEL = None
GEMINI_MODELS = []

# Edit this list to track your own target YouTube channels (Sequential Scan + English/AI-Dub Filter)
CHANNELS = [
    {"name": "IShowSpeed", "handle": "IShowSpeed", "is_english": True},
    {"name": "MrBeast Gaming", "handle": "MrBeastGaming", "is_english": True},
    {"name": "Mikecrack", "handle": "Mikecrack", "is_english": False},
    {"name": "JuegaGerman", "handle": "JuegaGerman", "is_english": False},
    {"name": "Jess No Limit", "handle": "JessNoLimit", "is_english": False},
    {"name": "Fernanfloo", "handle": "Fernanfloo", "is_english": False},
    {"name": "DaFuq!?Boom!", "handle": "DaFuqBoom", "is_english": True},
    {"name": "TheDonato", "handle": "TheDonato", "is_english": False},
]


class BotBlockError(Exception):
    pass


def run_ytdlp(args, check_file=None):
    """Try every cookie / no-cookie strategy until one succeeds."""
    base = ["yt-dlp", "--js-runtimes", "node", "--remote-components", "ejs:github", "--no-warnings"]
    strategies = COOKIE_MANAGER.strategies(base + args)

    last_err = ""
    for label, command in strategies:
        try:
            res = subprocess.run(command, capture_output=True, text=True, timeout=900)
        except subprocess.TimeoutExpired:
            last_err = "yt-dlp timed out after 15 minutes"
            COOKIE_MANAGER.mark_failed(label, last_err)
            print(f"  -> yt-dlp ({label}) fail: {last_err}")
            continue

        combined = (res.stdout or "") + "\n" + (res.stderr or "")
        file_ok = True if not check_file else bool(glob.glob(check_file))
        if res.returncode == 0 and file_ok:
            COOKIE_MANAGER.mark_success(label)
            return res

        err_lines = [ln.strip() for ln in (res.stderr or "").splitlines() if ln.strip()]
        last_err = err_lines[-1] if err_lines else f"exit code {res.returncode}"
        COOKIE_MANAGER.mark_failed(label, last_err)
        print(f"  -> yt-dlp ({label}) fail: {last_err}")

    if COOKIE_MANAGER.saw_bot_block:
        COOKIE_MANAGER.write_alert(last_err)
        raise BotBlockError(f"YouTube bot-check / expired cookies: {last_err}")
    raise RuntimeError(f"yt-dlp failed: {last_err}")



def load_queue():
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_queue(queue):
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            data.setdefault("channel_uploads", {})
            data.setdefault("processed_videos", [])
            return data
    return {"channel_uploads": {}, "processed_videos": []}


def save_state(state):
    state["processed_videos"] = state["processed_videos"][-500:]
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def parse_iso_duration(duration_str):
    if not duration_str:
        return 0
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration_str)
    if not m:
        return 0
    h = int(m.group(1) or 0)
    mins = int(m.group(2) or 0)
    s = int(m.group(3) or 0)
    return h * 3600 + mins * 60 + s


def parse_iso_datetime(dt_str):
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None


def get_today_ist_date():
    ist = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(ist).date()


def get_today_ist_str():
    return get_today_ist_date().strftime("%Y-%m-%d")


def get_clip_age_days(clip, today_date=None):
    if today_date is None:
        today_date = get_today_ist_date()
    disc = clip.get("discovered_date")
    if not disc:
        clip["discovered_date"] = today_date.strftime("%Y-%m-%d")
        return 0
    try:
        disc_date = datetime.strptime(disc, "%Y-%m-%d").date()
        return max(0, (today_date - disc_date).days)
    except Exception:
        clip["discovered_date"] = today_date.strftime("%Y-%m-%d")
        return 0


def get_next_publish_time(slot_index, last_scheduled_dt=None):
    """
    Schedules Shorts starting at 7:00 PM IST with SCHEDULE_GAP_MINUTES (10 min) intervals.
    If 7:00 PM has already passed, starts 5 minutes from now and keeps the 10-minute spacing.
    """
    ist = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(ist)
    base_7pm = now_ist.replace(hour=19, minute=0, second=0, microsecond=0)
    target_dt = base_7pm + timedelta(minutes=SCHEDULE_GAP_MINUTES * slot_index)
    min_allowed = now_ist + timedelta(minutes=5)

    if last_scheduled_dt is not None:
        min_allowed = max(min_allowed, last_scheduled_dt + timedelta(minutes=SCHEDULE_GAP_MINUTES))

    final_dt = max(target_dt, min_allowed).replace(second=0, microsecond=0)
    if final_dt < now_ist + timedelta(minutes=2):
        final_dt += timedelta(minutes=5)

    return final_dt


def get_youtube_read_client():
    if not YT_API_KEY:
        return None
    return build("youtube", "v3", developerKey=YT_API_KEY)


def resolve_uploads_playlist(yt_read, ch, state):
    handle = ch["handle"]
    cached = state["channel_uploads"].get(handle)
    if cached:
        return cached

    resp = yt_read.channels().list(
        part="contentDetails,snippet",
        forHandle=handle
    ).execute()
    items = resp.get("items", [])
    if not items:
        print(f"Warning: Channel handle @{handle} not found.")
        return None

    uploads_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    state["channel_uploads"][handle] = uploads_id
    save_state(state)
    return uploads_id


def discover_candidates_from_channels(state):
    yt_read = get_youtube_read_client()
    if not yt_read:
        print("ERROR: YT_API_KEY secret is missing! Add YT_API_KEY in GitHub Secrets for auto channel scan.")
        return []

    cutoff_dt = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    processed_set = set(state.get("processed_videos", []))
    all_candidates = []

    print(f"Scanning {len(CHANNELS)} channels sequentially (Last {LOOKBACK_HOURS}h)...")

    for idx, ch in enumerate(CHANNELS, start=1):
        name = ch["name"]
        print(f"\n[{idx}/{len(CHANNELS)}] Visiting channel: {name} (@{ch['handle']})...")
        try:
            uploads_id = resolve_uploads_playlist(yt_read, ch, state)
            if not uploads_id:
                continue

            pl_resp = yt_read.playlistItems().list(
                part="contentDetails",
                playlistId=uploads_id,
                maxResults=15
            ).execute()
            vid_ids = [
                it["contentDetails"]["videoId"]
                for it in pl_resp.get("items", [])
                if it.get("contentDetails", {}).get("videoId")
            ]
            if not vid_ids:
                print(f"  -> {name}: No videos found, skipping.")
                continue

            v_resp = yt_read.videos().list(
                part="snippet,contentDetails,statistics,liveStreamingDetails",
                id=",".join(vid_ids)
            ).execute()

            ended_lives = []
            normal_videos = []
            is_currently_live = False

            for item in v_resp.get("items", []):
                vid = item["id"]
                snip = item.get("snippet", {})
                live_status = snip.get("liveBroadcastContent", "none")
                live_details = item.get("liveStreamingDetails") or {}

                if live_status in ("live", "upcoming"):
                    is_currently_live = True
                    print(f"  -> Currently LIVE/Upcoming ({snip.get('title', '')[:50]}) -> skipping active stream.")
                    continue

                if vid in processed_set:
                    continue

                duration_sec = parse_iso_duration(item.get("contentDetails", {}).get("duration", ""))
                if duration_sec < 60:
                    continue

                actual_end = parse_iso_datetime(live_details.get("actualEndTime"))
                published_at = parse_iso_datetime(snip.get("publishedAt"))
                ref_time = actual_end or published_at
                if not ref_time or ref_time < cutoff_dt:
                    continue

                views = int(item.get("statistics", {}).get("viewCount", 0) or 0)
                api_audio_lang = (snip.get("defaultAudioLanguage") or snip.get("defaultLanguage") or "").lower()

                candidate = {
                    "video_id": vid,
                    "video_url": f"https://www.youtube.com/watch?v={vid}",
                    "channel_name": name,
                    "is_english_channel": ch["is_english"],
                    "api_audio_lang": api_audio_lang,
                    "title": snip.get("title", ""),
                    "view_count": views,
                    "duration": duration_sec,
                    "is_ended_live": bool(actual_end)
                }

                if actual_end:
                    ended_lives.append(candidate)
                else:
                    normal_videos.append(candidate)

            channel_found = ended_lives + normal_videos
            if not channel_found:
                status_note = "(Active live only, no new ended lives/videos)" if is_currently_live else "(No new ended lives or videos in lookback window)"
                print(f"  -> {name}: Skip {status_note}")
            else:
                print(f"  -> {name}: Found {len(ended_lives)} ended live + {len(normal_videos)} normal videos!")
                all_candidates.extend(channel_found)

        except Exception as e:
            print(f"  -> {name} scan error: {e}")

        time.sleep(0.5)

    all_candidates.sort(key=lambda x: x["view_count"], reverse=True)
    print(f"\nFound {len(all_candidates)} new videos/ended-lives (Ranked by views):")
    for i, c in enumerate(all_candidates, start=1):
        kind = "Ended Live" if c["is_ended_live"] else "Video"
        print(f"  #{i} [{c['view_count']:,} views] ({c['channel_name']} - {kind}) {c['title'][:65]}")

    return all_candidates


def check_english_audio_availability(meta, is_english_channel, api_audio_lang):
    formats = meta.get("formats") or []
    audio_formats = [f for f in formats if f.get("acodec") and f.get("acodec") != "none"]
    en_formats = [f for f in audio_formats if (f.get("language") or "").lower().startswith("en")]

    if en_formats:
        return True, True

    if is_english_channel or api_audio_lang.startswith("en"):
        return True, False

    return False, False


def get_ytdlp_metadata(video_url):
    res = run_ytdlp(["--dump-json", "--no-playlist", video_url])
    return json.loads(res.stdout)


def parse_vtt_to_chunks(vtt_path, max_chars=50000):
    chunks = []
    current_lines = []
    current_len = 0
    current_sec = 0
    last_text = ""
    time_pattern = re.compile(r"(\d+):(\d+):(\d+)\.\d+|(\d+):(\d+)\.\d+")

    with open(vtt_path, "r", encoding="utf-8", errors="ignore") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
                continue
            if "-->" in line:
                m = time_pattern.search(line)
                if m:
                    if m.group(1) is not None:
                        current_sec = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
                    else:
                        current_sec = int(m.group(4)) * 60 + int(m.group(5))
                continue

            clean = re.sub(r"<[^>]+>", "", line).strip()
            if clean and clean != last_text:
                entry = f"[{current_sec}s] {clean}"
                current_lines.append(entry)
                current_len += len(entry) + 1
                last_text = clean

                if current_len >= max_chars:
                    chunks.append("\n".join(current_lines))
                    current_lines = []
                    current_len = 0

    if current_lines:
        chunks.append("\n".join(current_lines))
    return chunks


def get_gemini_models():
    global GEMINI_MODELS
    if GEMINI_MODELS:
        return GEMINI_MODELS

    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
    resp = requests.get(list_url, timeout=30)
    resp.raise_for_status()
    models = resp.json().get("models", [])

    candidates = []
    for m in models:
        name = m.get("name", "").replace("models/", "")
        methods = m.get("supportedGenerationMethods", [])
        if "generateContent" not in methods:
            continue
        low = name.lower()
        if any(bad in low for bad in ("tts", "image", "audio", "embed", "aqa", "vision", "robotics", "computer", "veo", "imagen", "gemma", "live")):
            continue
        if "gemini" in low:
            candidates.append(name)

    def priority(name):
        low = name.lower()
        if "flash" in low and not any(x in low for x in ("latest", "omni", "lite", "exp", "preview", "thinking")):
            return 0
        if "flash" in low and "omni" in low:
            return 1
        if low == "gemini-flash-latest":
            return 2
        if "flash" in low:
            return 3
        return 4

    candidates.sort(key=lambda n: n.lower(), reverse=True)
    candidates.sort(key=priority)

    if not candidates:
        raise RuntimeError("No working Gemini text model found for this API key!")

    GEMINI_MODELS = candidates
    print(f"Auto-selected Gemini model: {GEMINI_MODELS[0]}")
    return GEMINI_MODELS


def rotate_model_to_back(model_name):
    if model_name in GEMINI_MODELS and len(GEMINI_MODELS) > 1:
        GEMINI_MODELS.remove(model_name)
        GEMINI_MODELS.append(model_name)


def call_gemini_json(prompt, image_b64=None):
    models = get_gemini_models()
    parts_payload = [{"text": prompt}]
    if image_b64:
        parts_payload.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": image_b64
            }
        })

    payload = {
        "contents": [{"parts": parts_payload}],
        "generationConfig": {"responseMimeType": "application/json"}
    }

    for round_num in range(2):
        for model_name in list(models):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
            try:
                resp = requests.post(url, json=payload, timeout=60)
            except requests.exceptions.RequestException:
                rotate_model_to_back(model_name)
                continue

            if resp.status_code in (400, 403, 404):
                if not image_b64 and model_name in GEMINI_MODELS and len(GEMINI_MODELS) > 1:
                    GEMINI_MODELS.remove(model_name)
                else:
                    rotate_model_to_back(model_name)
                continue

            if resp.status_code in (429, 500, 502, 503, 504):
                rotate_model_to_back(model_name)
                time.sleep(2)
                continue

            if not resp.ok:
                rotate_model_to_back(model_name)
                continue

            try:
                data = resp.json()
                parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                text_parts = [p.get("text", "") for p in parts if p.get("text") and not p.get("thought")]
                if not text_parts:
                    return []
                raw_text = "".join(text_parts).strip()
                raw_text = re.sub(r"^```(?:json)?|```$", "", raw_text).strip()
                return json.loads(raw_text)
            except Exception:
                rotate_model_to_back(model_name)
                continue

        if round_num == 0:
            time.sleep(20)

    return None


def detect_facecam_crop(video_path):
    if not CONFIG["facecam"].get("auto_detect", True):
        return None
    try:
        if os.path.exists("frame.jpg"):
            os.remove("frame.jpg")

        for seek in ("8", "1"):
            subprocess.run([
                "ffmpeg", "-y", "-ss", seek, "-i", video_path,
                "-frames:v", "1", "-q:v", "3", "frame.jpg"
            ], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists("frame.jpg"):
                break

        if not os.path.exists("frame.jpg"):
            return None

        with open("frame.jpg", "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")

        prompt = """
        Analyze this screenshot from a YouTube gaming video or animation.
        Check if there is a picture-in-picture real streamer facecam/webcam box overlaid on top of gameplay.

        STRICT RULES:
        - Do NOT confuse in-game characters, animations, or cutscenes with a real streamer webcam.
        - If there IS a real streamer facecam overlay, set "has_facecam": true and return its tight bounding box [ymin, xmin, ymax, xmax] normalized from 0 to 1000.
        - If there is NO webcam overlay, OR if a real person already fills the whole screen (full-screen IRL / animation), set "has_facecam": false.

        Return ONLY valid JSON:
        {
          "has_facecam": true,
          "box_2d": [ymin, xmin, ymax, xmax]
        }
        """

        res = call_gemini_json(prompt, image_b64=img_b64)
        if not isinstance(res, dict):
            return None

        if not res.get("has_facecam"):
            print("AI Auto-Detect: Full-screen 9:16 mode selected.")
            return "FULLSCREEN"

        box = res.get("box_2d")
        if not isinstance(box, list) or len(box) != 4:
            return None

        ymin, xmin, ymax, xmax = [max(0.0, min(1000.0, float(v))) / 1000.0 for v in box]
        xmin, xmax = min(xmin, xmax), max(xmin, xmax)
        ymin, ymax = min(ymin, ymax), max(ymin, ymax)
        w = min(1.0 - xmin, xmax - xmin)
        h = min(1.0 - ymin, ymax - ymin)

        if w > 0.70 or h > 0.70:
            return "FULLSCREEN"
        if w < 0.05 or h < 0.05:
            return None

        print(f"AI Auto-Detect: Facecam detected (x={xmin:.2f}-{xmax:.2f}, y={ymin:.2f}-{ymax:.2f})")
        return {"x": xmin, "y": ymin, "w": w, "h": h}
    except Exception as exc:
        print(f"AI Auto-Detect warning: {exc}")
        return None


def ask_gemini_for_chunk(chunk_text, chunk_index, total_chunks, video_title, channel_name):
    prompt = f"""
    You are an expert USA viral YouTube Shorts editor analyzing part {chunk_index}/{total_chunks} of a video by "{channel_name}" titled "{video_title}".
    Find ALL genuinely viral, hilarious, raging, shocking, or epic moments in this part.

    STRICT RULES:
    - Return ONLY English titles, descriptions, and tags targeted at USA / global English gaming viewers.
    - Mention "{channel_name}" naturally in the title or description when relevant.
    - Decide the count dynamically based ONLY on real quality (return [] if boring/intro/starting soon).
    - Only include moments with viral_score >= 8 (out of 10).
    - Each clip MUST be 35 to 55 seconds long (end - start between 35 and 55).
    - Clips must NOT overlap.

    Return ONLY a valid JSON array:
    [
      {{
        "start": <integer start seconds>,
        "end": <integer end seconds>,
        "viral_score": <integer 8 to 10>,
        "title": "<catchy English viral title under 85 chars with #Shorts>",
        "description": "<engaging 2-line English description with relevant hashtags #Shorts>",
        "tags": ["Shorts", "Gaming", "{channel_name}", "<topic tag 1>", "<topic tag 2>"]
      }}
    ]

    Transcript:
    {chunk_text}
    """
    data = call_gemini_json(prompt)
    return data if isinstance(data, list) else []


def extract_clips_from_heatmap(meta, candidate, facecam_pos, has_en_audio_tag):
    heatmap = meta.get("heatmap") or []
    if not heatmap:
        return []

    duration = float(meta.get("duration") or candidate.get("duration") or 0)
    min_start = 120 if duration > 600 else 10
    source_title = meta.get("title") or candidate.get("title") or "Gaming Highlight"
    channel_name = candidate["channel_name"]
    today_str = get_today_ist_str()

    ranked = sorted(heatmap, key=lambda x: x.get("value", 0), reverse=True)
    clips = []
    for point in ranked:
        val = float(point.get("value", 0))
        if val < 0.65:
            break
        peak_mid = (float(point["start_time"]) + float(point["end_time"])) / 2.0
        start = int(max(min_start, peak_mid - 15))
        end = int(min(duration, start + 45)) if duration else start + 45
        if end - start < 25:
            continue
        if any(abs(c["start"] - start) < 55 for c in clips):
            continue

        clips.append({
            "video_id": candidate["video_id"],
            "video_url": candidate["video_url"],
            "channel_name": channel_name,
            "view_count": candidate["view_count"],
            "discovered_date": today_str,
            "has_en_audio_tag": has_en_audio_tag,
            "facecam_pos": facecam_pos,
            "start": start,
            "end": end,
            "viral_score": max(8, min(10, int(round(val * 10)))),
            "title": f"{channel_name} Insane Moment! #Shorts",
            "description": f"Most replayed viral moment from {channel_name}! #Shorts #Gaming",
            "tags": ["Shorts", "Gaming", channel_name, "Highlights", "Viral"],
            "source_title": source_title,
            "needs_ai_title": True
        })
        if len(clips) >= 10:
            break

    print(f"  -> Found {len(clips)} peaks from YouTube Most Replayed graph.")
    return clips


def scan_candidate_video(candidate, facecam_pos):
    video_url = candidate["video_url"]
    channel_name = candidate["channel_name"]
    print(f"\nScanning [{candidate['view_count']:,} views] {channel_name}: {candidate['title'][:65]}")

    meta = get_ytdlp_metadata(video_url)
    if meta.get("is_live"):
        print("  -> Active livestream detected, skipping.")
        return [], False

    eligible, has_en_audio_tag = check_english_audio_availability(
        meta, candidate["is_english_channel"], candidate.get("api_audio_lang", "")
    )
    if not eligible:
        print("  -> SKIP: Neither native English nor English AI-Dub track available.")
        return [], True

    dub_note = "English Audio/Dub track confirmed" if has_en_audio_tag else "Native English audio"
    print(f"  -> Eligible ({dub_note})! Extracting best clips...")

    source_title = meta.get("title") or candidate.get("title") or "Gaming Highlight"
    today_str = get_today_ist_str()

    for old in glob.glob("subs*.vtt"):
        os.remove(old)

    try:
        run_ytdlp(
            [
                "--write-auto-subs", "--write-subs",
                "--sub-lang", "en",
                "--sleep-subtitles", "5",
                "--sub-format", "vtt",
                "--skip-download",
                "-o", "subs",
                video_url
            ],
            check_file="subs*.vtt"
        )
    except BotBlockError:
        raise
    except Exception:
        pass

    vtt_files = glob.glob("subs*.vtt")
    if not vtt_files:
        print("  -> No English subtitles found, checking Most Replayed heatmap...")
        heatmap_clips = extract_clips_from_heatmap(meta, candidate, facecam_pos, has_en_audio_tag)
        if heatmap_clips:
            return heatmap_clips, True
        dur = int(meta.get("duration") or candidate.get("duration") or 0)
        if 60 <= dur <= 240:
            start = max(5, dur // 4)
            end = min(dur, start + 48)
            return [{
                "video_id": candidate["video_id"],
                "video_url": video_url,
                "channel_name": channel_name,
                "view_count": candidate["view_count"],
                "discovered_date": today_str,
                "has_en_audio_tag": has_en_audio_tag,
                "facecam_pos": facecam_pos,
                "start": start,
                "end": end,
                "viral_score": 8,
                "title": f"{source_title[:65]} #Shorts",
                "description": f"Epic moment from {channel_name}! #Shorts #Gaming",
                "tags": ["Shorts", "Gaming", channel_name, "Viral"],
                "source_title": source_title,
                "needs_ai_title": True
            }], True
        print("  -> No subtitles and no heatmap found -> skip.")
        return [], True

    chunks = parse_vtt_to_chunks(vtt_files[0])
    print(f"  -> {len(chunks)} transcript parts ready. Analyzing with Gemini...")

    found_clips = []
    for idx, chunk in enumerate(chunks, start=1):
        try:
            clips = ask_gemini_for_chunk(chunk, idx, len(chunks), source_title, channel_name)
            for c in clips:
                score = int(c.get("viral_score", 0))
                if score < 8:
                    continue
                start = max(0, int(c["start"]))
                end = int(c["end"])
                if end - start < 20 or end - start > 58:
                    end = start + 45

                if any(abs(existing["start"] - start) < 35 for existing in found_clips):
                    continue

                found_clips.append({
                    "video_id": candidate["video_id"],
                    "video_url": video_url,
                    "channel_name": channel_name,
                    "view_count": candidate["view_count"],
                    "discovered_date": today_str,
                    "has_en_audio_tag": has_en_audio_tag,
                    "facecam_pos": facecam_pos,
                    "start": start,
                    "end": end,
                    "viral_score": score,
                    "title": str(c.get("title", f"{channel_name} Viral Moment #Shorts"))[:95],
                    "description": str(c.get("description", f"#Shorts #Gaming #{channel_name.replace(' ', '')}")),
                    "tags": c.get("tags") if isinstance(c.get("tags"), list) else ["Shorts", "Gaming", channel_name],
                    "source_title": source_title
                })
        except Exception as e:
            print(f"  -> Chunk {idx} error: {e}")

        if idx < len(chunks):
            time.sleep(2)

    found_clips.sort(key=lambda x: x["viral_score"], reverse=True)
    print(f"  -> Added {len(found_clips)} viral clips to queue.")
    return found_clips, True


def generate_english_title_from_speech(spoken_text, source_title, channel_name):
    try:
        prompt = f"""
        Based on this English spoken transcript from a viral gaming Short by "{channel_name}" (video: "{source_title}"), write a catchy USA/English YouTube Shorts title, description, and tags.
        Return ONLY valid JSON:
        {{
          "title": "<catchy English viral title under 85 chars with #Shorts>",
          "description": "<2-line engaging English description with hashtags #Shorts>",
          "tags": ["Shorts", "Gaming", "{channel_name}", "<tag4>", "<tag5>"]
        }}
        Spoken text: {spoken_text[:1500]}
        """
        data = call_gemini_json(prompt)
        if isinstance(data, dict) and data.get("title"):
            return data
    except Exception:
        pass
    return None


def format_ass_time(sec):
    total_cs = max(0, int(round(float(sec) * 100)))
    cs = total_cs % 100
    total_s = total_cs // 100
    s = total_s % 60
    total_m = total_s // 60
    m = total_m % 60
    h = total_m // 60
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def generate_animated_captions(video_path, ass_path="captions.ass"):
    global WHISPER_MODEL
    if not CONFIG["captions"].get("enabled", True):
        print("Captions disabled in config.json -> rendering without captions.")
        return False, ""
    try:
        print("Generating word-level captions with Whisper AI...")
        subprocess.run([
            "ffmpeg", "-y", "-i", video_path,
            "-vn", "-ac", "1", "-ar", "16000", "audio.wav"
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if WHISPER_MODEL is None:
            WHISPER_MODEL = WhisperModel("base", device="cpu", compute_type="int8")

        segments, _ = WHISPER_MODEL.transcribe("audio.wav", language="en", word_timestamps=True)

        words = []
        for seg in segments:
            if not seg.words:
                continue
            for w in seg.words:
                clean = re.sub(r"[{}\\]", "", w.word).strip()
                if clean:
                    words.append({
                        "text": clean,
                        "start": max(0.0, float(w.start)),
                        "end": max(float(w.end), float(w.start) + 0.08),
                    })

        if not words:
            return False, ""

        full_speech = " ".join(w["text"] for w in words)
        ok, meta = build_ass(words, CONFIG["captions"], ass_path)
        if ok:
            print(
                "Captions ready: "
                f"{meta['style']} | {meta['animation']} | "
                f"{meta['words']} words | position {meta['position']}"
            )
            return True, full_speech
        return False, full_speech
    except Exception as e:
        print(f"Captions warning: {e}")
        return False, ""


def cleanup_temp_files():
    for temp in ("raw_clip.mp4", "final_short.mp4", "captions.ass", "audio.wav", "frame.jpg"):
        if os.path.exists(temp):
            os.remove(temp)


def download_and_render_short(clip):
    cleanup_temp_files()

    if clip.get("has_en_audio_tag"):
        fmt = "bestvideo[height<=1080][ext=mp4]+bestaudio[language^=en][ext=m4a]/bestvideo[height<=1080]+bestaudio[language^=en]/best[height<=1080][language^=en]/best[height<=1080]"
    else:
        fmt = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]/best"

    print(f"Downloading clip ({clip['start']}s-{clip['end']}s)...")
    run_ytdlp(
        [
            "-f", fmt,
            "--download-sections", f"*{clip['start']}-{clip['end']}",
            "--force-keyframes-at-cuts",
            "--merge-output-format", "mp4",
            "-o", "raw_clip.mp4",
            clip["video_url"]
        ],
        check_file="raw_clip.mp4"
    )

    has_captions, spoken_text = generate_animated_captions("raw_clip.mp4", "captions.ass")
    auto_crop = detect_facecam_crop("raw_clip.mp4")

    info = get_video_info("raw_clip.mp4")
    cam_cfg = dict(CONFIG["facecam"])
    out_w = int(CONFIG["video"]["width"])
    out_h = int(CONFIG["video"]["height"])
    filter_complex, details = build_facecam_filter(
        info,
        cam_cfg,
        auto_crop,
        ass_path="captions.ass" if has_captions else None,
        out_w=out_w,
        out_h=out_h,
    )
    crop = details.get("crop")
    crop_label = (
        f"{crop['w']}x{crop['h']} @ {crop['x']},{crop['y']}"
        if crop else "none"
    )
    print(
        f"Rendering final Short | layout={details['mode']} | "
        f"facecam crop={crop_label} | size={cam_cfg['size']:.2f} | "
        f"ratio={cam_cfg['ratio']} | captions={'on' if has_captions else 'off'}"
    )

    subprocess.run([
        "ffmpeg", "-y", "-i", "raw_clip.mp4",
        "-filter_complex", filter_complex,
        "-map", "[v]", "-map", "0:a?",
        "-c:v", "libx264", "-preset", CONFIG["video"]["preset"],
        "-crf", str(CONFIG["video"]["crf"]),
        "-r", str(CONFIG["video"]["fps"]),
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        "final_short.mp4"
    ], check=True)
    return spoken_text


def get_google_credentials(refresh_token_env="YT_REFRESH_TOKEN"):
    token = os.environ.get(refresh_token_env, "").strip()
    if not token:
        return None
    creds = Credentials(
        token=None,
        refresh_token=token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["YT_CLIENT_ID"],
        client_secret=os.environ["YT_CLIENT_SECRET"]
    )
    creds.refresh(Request())
    return creds


def upload_to_youtube(youtube, file_path, title, description, tags=None, publish_at_dt=None):
    today_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00.0Z")

    if publish_at_dt is not None:
        publish_at_utc = publish_at_dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        status_body = {
            "privacyStatus": "private",
            "publishAt": publish_at_utc,
            "selfDeclaredMadeForKids": False
        }
    else:
        status_body = {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }

    body = {
        "snippet": {
            "title": title[:95],
            "description": description,
            "tags": tags or ["Shorts", "Gaming", "Highlights"],
            "categoryId": "20",
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en"
        },
        "status": status_body,
        "recordingDetails": {
            "recordingDate": today_utc
        }
    }
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(
        part="snippet,status,recordingDetails",
        body=body,
        media_body=media
    )
    response = request.execute()
    if publish_at_dt is not None:
        ist_label = publish_at_dt.strftime("%I:%M %p IST")
        print(f"Scheduled Success ({ist_label})! https://youtube.com/shorts/{response['id']}")
    else:
        print(f"Upload Success (Public Now)! https://youtube.com/shorts/{response['id']}")


def order_clips_by_views_and_age(clips, today_date, prioritize_age=False):
    groups = {}
    for clip in clips:
        vid_key = clip.get("video_id") or clip.get("video_url")
        groups.setdefault(vid_key, []).append(clip)

    for vid_key in groups:
        groups[vid_key].sort(key=lambda c: int(c.get("viral_score", 0)), reverse=True)

    def video_sort_key(vk):
        grp = groups[vk]
        views = int(grp[0].get("view_count", 0))
        if prioritize_age:
            max_age = max(get_clip_age_days(c, today_date) for c in grp)
            return (max_age, views)
        return views

    ranked_vids = sorted(groups.keys(), key=video_sort_key, reverse=True)

    ordered = []
    round_idx = 0
    while True:
        added_this_round = False
        for vk in ranked_vids:
            if round_idx < len(groups[vk]):
                ordered.append(groups[vk][round_idx])
                added_this_round = True
        if not added_this_round:
            break
        round_idx += 1

    return ordered


def pick_5050_clips_for_today(queue, max_uploads):
    """
    50-50 Rule:
    - Target: 3 Current (today) + 3 Pending (oldest day sections first, highest views first).
    - Auto-fills any shortfall from the other pool.
    - Separates clips >= ARCHIVE_AFTER_DAYS (10 days) for Google Drive backup.
    """
    today_date = get_today_ist_date()
    current_clips = []
    pending_clips = []
    expired_clips = []

    for clip in queue:
        age = get_clip_age_days(clip, today_date)
        if age >= ARCHIVE_AFTER_DAYS:
            expired_clips.append(clip)
        elif age == 0:
            current_clips.append(clip)
        else:
            pending_clips.append(clip)

    ordered_current = order_clips_by_views_and_age(current_clips, today_date, prioritize_age=False)
    ordered_pending = order_clips_by_views_and_age(pending_clips, today_date, prioritize_age=True)

    target_current = (max_uploads + 1) // 2
    target_pending = max_uploads - target_current

    take_current = min(len(ordered_current), target_current)
    take_pending = min(len(ordered_pending), target_pending)

    shortfall = max_uploads - (take_current + take_pending)
    if shortfall > 0:
        extra_pending = min(len(ordered_pending) - take_pending, shortfall)
        take_pending += extra_pending
        shortfall -= extra_pending

    if shortfall > 0:
        extra_current = min(len(ordered_current) - take_current, shortfall)
        take_current += extra_current

    chosen_current = ordered_current[:take_current]
    chosen_pending = ordered_pending[:take_pending]

    selected = []
    max_len = max(len(chosen_current), len(chosen_pending))
    for i in range(max_len):
        if i < len(chosen_current):
            selected.append(chosen_current[i])
        if i < len(chosen_pending):
            selected.append(chosen_pending[i])

    age_counts = {}
    for c in pending_clips:
        a = get_clip_age_days(c, today_date)
        age_counts[a] = age_counts.get(a, 0) + 1
    age_summary = ", ".join(f"{d}d-old:{age_counts[d]}" for d in sorted(age_counts.keys(), reverse=True)) or "None"
    print(f"\nQueue Status -> Today (0d): {len(current_clips)} | Pending ({age_summary}) | 10d+ Expired: {len(expired_clips)}")
    print(f"50-50 Selection -> {len(chosen_current)} Current + {len(chosen_pending)} Pending = {len(selected)} Total Uploads")

    return selected, expired_clips


def get_or_create_drive_folder(drive, folder_name):
    safe_name = folder_name.replace("'", "\\'")
    q = f"name='{safe_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    resp = drive.files().list(q=q, spaces="drive", fields="files(id, name, webViewLink)").execute()
    files = resp.get("files", [])
    if files:
        return files[0]["id"], files[0].get("webViewLink", f"https://drive.google.com/drive/folders/{files[0]['id']}")

    meta = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder"
    }
    created = drive.files().create(body=meta, fields="id, webViewLink").execute()
    return created["id"], created.get("webViewLink", f"https://drive.google.com/drive/folders/{created['id']}")


def send_archive_email(creds, archived_records, folder_link, remaining_expired):
    if not ALERT_EMAIL:
        print("Gmail Alert skipped: ALERT_EMAIL secret is not configured.")
        return

    try:
        gmail = build("gmail", "v1", credentials=creds)
        lines = [
            f"Hi! {len(archived_records)} pending clips reached {ARCHIVE_AFTER_DAYS}+ days old,",
            "so they have been rendered and safely backed up to your Google Drive folder:\n",
            f"Google Drive Folder: {folder_link}\n",
            "Archived Clips:"
        ]
        for idx, rec in enumerate(archived_records, start=1):
            lines.append(
                f"{idx}. [{rec['discovered_date']}] {rec['channel_name']} ({rec['view_count']:,} views) - {rec['title']}\n"
                f"   Video Link: {rec['drive_link']}"
            )
        if remaining_expired > 0:
            lines.append(f"\nNote: {remaining_expired} more expired clips remain and will be archived on the next run.")

        msg = MIMEText("\n".join(lines), "plain", "utf-8")
        msg["to"] = ALERT_EMAIL
        msg["subject"] = f"AutoShorts Alert: {len(archived_records)} Expired Clips (10+ Days) Saved to Google Drive"

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
        gmail.users().messages().send(userId="me", body={"raw": raw}).execute()
        print("Email Alert sent successfully.")
    except HttpError as e:
        print(f"Gmail Alert Warning (Drive upload succeeded, email failed): {e}")
    except Exception as e:
        print(f"Gmail Alert Warning: {e}")


def archive_expired_clips_to_drive(creds, expired_clips, queue):
    if not expired_clips:
        return
    if creds is None:
        print("10-Day Archive skipped: DRIVE_GMAIL_REFRESH_TOKEN secret is not set (clips kept safely in queue).")
        return

    today_date = get_today_ist_date()
    expired_clips.sort(
        key=lambda c: (get_clip_age_days(c, today_date), int(c.get("view_count", 0))),
        reverse=True
    )
    batch = expired_clips[:MAX_ARCHIVE_PER_RUN]
    print(f"\n=== 10-Day Archive: {len(expired_clips)} expired clips found (archiving {len(batch)} to Google Drive) ===")

    try:
        drive = build("drive", "v3", credentials=creds)
        folder_id, folder_link = get_or_create_drive_folder(drive, DRIVE_ARCHIVE_FOLDER)
    except HttpError as e:
        print(f"Google Drive API Error (Clips kept safely in queue): {e}")
        return
    except Exception as e:
        print(f"Google Drive setup warning: {e}")
        return

    archived_records = []
    for idx, clip in enumerate(batch, start=1):
        print(f"\n[Archive {idx}/{len(batch)}] Rendering for Drive: {clip['title']} ({clip.get('discovered_date')})")
        try:
            spoken_text = download_and_render_short(clip)
            if clip.get("needs_ai_title") and spoken_text:
                ai_meta = generate_english_title_from_speech(
                    spoken_text, clip.get("source_title", ""), clip.get("channel_name", "Gaming")
                )
                if ai_meta:
                    clip["title"] = str(ai_meta.get("title", clip["title"]))[:95]

            safe_ch = re.sub(r"[^A-Za-z0-9_-]+", "_", clip.get("channel_name", "Creator"))[:25]
            safe_title = re.sub(r"[^A-Za-z0-9_-]+", "_", clip.get("title", "Clip"))[:50]
            filename = f"{clip.get('discovered_date', 'old')}_{safe_ch}_{safe_title}.mp4"

            file_metadata = {
                "name": filename,
                "parents": [folder_id]
            }
            media = MediaFileUpload("final_short.mp4", mimetype="video/mp4", resumable=True)
            uploaded = drive.files().create(
                body=file_metadata,
                media_body=media,
                fields="id, webViewLink"
            ).execute()

            drive_link = uploaded.get("webViewLink", f"https://drive.google.com/file/d/{uploaded['id']}/view")
            print(f"Drive Upload Success! {drive_link}")

            archived_records.append({
                "title": clip["title"],
                "channel_name": clip.get("channel_name", "Creator"),
                "discovered_date": clip.get("discovered_date", "N/A"),
                "view_count": int(clip.get("view_count", 0)),
                "drive_link": drive_link
            })

            if clip in queue:
                queue.remove(clip)
            save_queue(queue)
        except BotBlockError as e:
            print(f"BOT BLOCK during Drive archive (Clips kept safely in queue): {e}")
            break
        except HttpError as e:
            print(f"Google Drive upload error (Clip kept safely in queue): {e}")
            break
        except Exception as e:
            print(f"Archive clip error: {e}")
            clip["archive_retries"] = clip.get("archive_retries", 0) + 1
            if clip["archive_retries"] >= 2 and clip in queue:
                queue.remove(clip)
            save_queue(queue)
        finally:
            cleanup_temp_files()

    if archived_records:
        remaining_expired = max(0, len(expired_clips) - len(archived_records))
        send_archive_email(creds, archived_records, folder_link, remaining_expired)


def main():
    queue = load_queue()
    state = load_state()

    cap = CONFIG["captions"]
    cam = CONFIG["facecam"]
    print(
        "Active config | "
        f"caption={cap['style']} / {cap['animation']} / {cap['position']} | "
        f"facecam={cam['mode']} / source={cam['source_position']} / "
        f"size={cam['size']:.2f} / ratio={cam['ratio']} | "
        f"video={CONFIG['video']['width']}x{CONFIG['video']['height']}@{CONFIG['video']['fps']}fps"
    )

    try:
        if VIDEO_URL:
            candidate = {
                "video_id": VIDEO_URL,
                "video_url": VIDEO_URL,
                "channel_name": "Gaming Creator",
                "is_english_channel": True,
                "api_audio_lang": "en",
                "title": VIDEO_URL,
                "view_count": 999999999,
                "duration": 0,
                "is_ended_live": False
            }
            new_clips, _ = scan_candidate_video(candidate, FACECAM_POS)
            for nc in new_clips:
                is_dup = any(
                    q["video_url"] == nc["video_url"] and abs(q["start"] - nc["start"]) < 35
                    for q in queue
                )
                if not is_dup:
                    queue.append(nc)
            save_queue(queue)
        else:
            candidates = discover_candidates_from_channels(state)
            for cand in candidates[:MAX_SCAN_VIDEOS_PER_RUN]:
                new_clips, mark_done = scan_candidate_video(cand, FACECAM_POS)
                for nc in new_clips:
                    is_dup = any(
                        q["video_url"] == nc["video_url"] and abs(q["start"] - nc["start"]) < 35
                        for q in queue
                    )
                    if not is_dup:
                        queue.append(nc)
                if mark_done:
                    if cand["video_id"] not in state["processed_videos"]:
                        state["processed_videos"].append(cand["video_id"])
                    save_state(state)
                save_queue(queue)
                time.sleep(3)
    except BotBlockError as e:
        print(f"FATAL BOT BLOCK DURING SCAN: {e}")
        save_queue(queue)
        save_state(state)
        sys.exit(1)

    if not queue:
        print("Queue is empty — no clips available to upload right now.")
        return

    today_date = get_today_ist_date()
    selected_clips, expired_clips = pick_5050_clips_for_today(queue, MAX_UPLOADS)
    mode_label = f"Auto-schedule from 7:00 PM IST ({SCHEDULE_GAP_MINUTES}m gap)" if PUBLISH_MODE == "schedule_7pm" else "Public Immediately"

    print(f"Uploading Top {len(selected_clips)} clips ({mode_label}):")
    for i, sc in enumerate(selected_clips, start=1):
        age = get_clip_age_days(sc, today_date)
        tag = "NEW (Today)" if age == 0 else f"PENDING ({age}d old)"
        print(f"  Upload #{i} [{tag}] [{sc.get('view_count', 0):,} views] {sc.get('channel_name', 'Creator')} - {sc['title'][:55]}")

    yt_creds = get_google_credentials("YT_REFRESH_TOKEN")
    youtube = build("youtube", "v3", credentials=yt_creds)
    uploaded_count = 0
    last_scheduled_dt = None
    fatal_bot_block = False

    for clip in selected_clips:
        print(f"\n--- Uploading {uploaded_count + 1}/{len(selected_clips)}: {clip['title']} ({clip['start']}s-{clip['end']}s) ---")
        try:
            spoken_text = download_and_render_short(clip)
            if clip.get("needs_ai_title") and spoken_text:
                ai_meta = generate_english_title_from_speech(
                    spoken_text, clip.get("source_title", ""), clip.get("channel_name", "Gaming")
                )
                if ai_meta:
                    clip["title"] = str(ai_meta.get("title", clip["title"]))[:95]
                    clip["description"] = str(ai_meta.get("description", clip["description"]))
                    if isinstance(ai_meta.get("tags"), list):
                        clip["tags"] = ai_meta["tags"]

            publish_at_dt = None
            if PUBLISH_MODE == "schedule_7pm":
                publish_at_dt = get_next_publish_time(uploaded_count, last_scheduled_dt)

            upload_to_youtube(
                youtube, "final_short.mp4", clip["title"], clip["description"], clip.get("tags"),
                publish_at_dt=publish_at_dt
            )
            if publish_at_dt is not None:
                last_scheduled_dt = publish_at_dt
            if clip in queue:
                queue.remove(clip)
            uploaded_count += 1
            save_queue(queue)
        except BotBlockError as e:
            print(f"BOT BLOCK ALERT: {e}")
            print("Clips are safely saved in queue (not deleted).")
            fatal_bot_block = True
            break
        except HttpError as e:
            if "quotaExceeded" in str(e):
                print("Daily YouTube API quota reached! Remaining clips will upload tomorrow.")
                break
            print(f"YouTube API Error: {e}")
            clip["retries"] = clip.get("retries", 0) + 1
            if clip["retries"] >= 2 and clip in queue:
                queue.remove(clip)
            save_queue(queue)
        except Exception as e:
            print(f"Clip processing error: {e}")
            clip["retries"] = clip.get("retries", 0) + 1
            if clip["retries"] >= 2 and clip in queue:
                queue.remove(clip)
            save_queue(queue)
        finally:
            cleanup_temp_files()

    # After YouTube uploads, archive 10+ day old clips to Google Drive + send Email alert
    if expired_clips and not fatal_bot_block:
        drive_creds = get_google_credentials("DRIVE_GMAIL_REFRESH_TOKEN")
        archive_expired_clips_to_drive(drive_creds, expired_clips, queue)

    print(f"\nDone! {uploaded_count} Shorts uploaded/scheduled today. {len(queue)} clips safely stored in queue.")
    if fatal_bot_block and uploaded_count == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
