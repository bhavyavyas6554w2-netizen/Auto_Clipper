"""
Cookie manager for yt-dlp with PO Token support.

Problems this solves:
  * One cookies.txt expires -> the whole run dies.
  * GitHub Actions datacenter IPs trigger "Sign in to confirm you're not a bot".
  * Users cannot tell whether the cookie is broken or the download is blocked.

Features:
  * Tier 1: Cookie-free downloads using PO Token (bgutil-ytdlp-pot-provider) with
    player clients: tv_embedded, android, ios, web, mweb
  * Tier 2: Up to 3 cookie sets: YT_COOKIES, YT_COOKIES_2, YT_COOKIES_3.
    Accepts Netscape cookies.txt, base64-encoded cookies.txt, a file path,
    or a JSON cookie export.
  * Tier 3: No-cookie fallbacks with different YouTube player clients.
  * Writes cookie_alert.json when every strategy fails, so the GitHub
    workflow can open an issue automatically.
  * Optional YT_PROXY for a residential proxy.
"""

import base64
import json
import os
import re
from datetime import datetime, timezone

COOKIE_ENV_NAMES = ("YT_COOKIES", "YT_COOKIES_2", "YT_COOKIES_3")
COOKIE_HEADER = "# Netscape HTTP Cookie File"

# Tier 1: PO Token player clients (most permissive first)
PO_TOKEN_CLIENTS = ("tv_embedded", "android", "ios", "web", "mweb")

# Tier 3: No-cookie fallback clients
NO_COOKIE_CLIENTS = ("android,ios", "web_safari", "web")


def is_bot_error(text):
    low = (text or "").lower()
    return any(
        marker in low
        for marker in (
            "sign in to confirm",
            "not a bot",
            "cookies are no longer valid",
            "login_required",
            "confirm you're not a bot",
            "this content isn't available, try again later",
        )
    )


def _looks_like_netscape(text):
    return "\t" in text and not text.lstrip().startswith(("{", "["))


def _json_to_netscape(text):
    try:
        data = json.loads(text)
    except Exception:
        return None
    if isinstance(data, dict):
        data = data.get("cookies") or data.get("Cookies") or []
    if not isinstance(data, list) or not data:
        return None

    lines = [COOKIE_HEADER]
    for cookie in data:
        if not isinstance(cookie, dict):
            continue
        domain = str(cookie.get("domain") or cookie.get("host") or "")
        if not domain:
            continue
        include_sub = "TRUE" if domain.startswith(".") else "FALSE"
        path = str(cookie.get("path") or "/")
        secure = "TRUE" if cookie.get("secure") else "FALSE"
        expires = cookie.get("expirationDate") or cookie.get("expires") or cookie.get("expiry") or 0
        try:
            expires = int(float(expires))
        except Exception:
            expires = 0
        name = str(cookie.get("name") or "")
        value = str(cookie.get("value") or "")
        lines.append("\t".join([domain, include_sub, path, secure, str(expires), name, value]))
    return "\n".join(lines) + "\n" if len(lines) > 1 else None


def _decode_cookie_value(raw):
    raw = (raw or "").strip()
    if not raw:
        return ""

    if os.path.exists(raw) and os.path.isfile(raw) and os.path.getsize(raw) < 2_000_000:
        try:
            with open(raw, "r", encoding="utf-8", errors="ignore") as handle:
                raw = handle.read().strip()
        except Exception:
            pass

    if raw.startswith("{") or raw.startswith("["):
        converted = _json_to_netscape(raw)
        if converted:
            return converted

    if not _looks_like_netscape(raw) and re.fullmatch(r"[A-Za-z0-9+/=\s]+", raw):
        try:
            decoded = base64.b64decode(raw, validate=False).decode("utf-8", errors="ignore").strip()
            if decoded.startswith("{") or decoded.startswith("["):
                converted = _json_to_netscape(decoded)
                if converted:
                    return converted
            if _looks_like_netscape(decoded):
                return decoded
        except Exception:
            pass

    return raw


class CookieManager:
    def __init__(self, env=None):
        env = env or os.environ
        self.proxy = (env.get("YT_PROXY") or "").strip()
        self.files = []
        self.active_label = None
        self.failed = set()
        self.last_error = ""
        self.saw_bot_block = False
        self.env = env

        for index, name in enumerate(COOKIE_ENV_NAMES, start=1):
            raw = env.get(name, "")
            content = _decode_cookie_value(raw)
            if not content:
                continue
            if not content.startswith(COOKIE_HEADER):
                content = COOKIE_HEADER + "\n" + content
            filename = "cookies.txt" if index == 1 else f"cookies_{index}.txt"
            try:
                with open(filename, "w", encoding="utf-8") as handle:
                    handle.write(content.rstrip("\n") + "\n")
            except Exception as exc:
                print(f"Cookie warning: could not write {filename}: {exc}")
                continue
            self.files.append({"label": name, "path": filename})

        if self.files:
            print(f"Cookie sets loaded: {', '.join(f['label'] for f in self.files)}")
        else:
            print("Cookie warning: no YT_COOKIES secret set; using no-cookie fallback.")
        if self.proxy:
            print("Cookie: YT_PROXY is configured.")

    def _with_proxy(self, args):
        if self.proxy:
            return args + ["--proxy", self.proxy]
        return args

    def strategies(self, base_args):
        """Ordered list of (label, full_args). Tier 1: PO Token (cookie-free), Tier 2: Cookies, Tier 3: No-cookie fallbacks."""
        strategies = []

        # TIER 1: PO Token - Cookie-free downloads (most permissive clients first)
        for client in PO_TOKEN_CLIENTS:
            strategies.append((
                f"po-token-{client}",
                self._with_proxy([
                    "--extractor-args", f"youtube:player_client={client}",
                    "--extractor-args", "youtube:po_token=bgutil.ytdlp_pot_provider"
                ] + base_args),
            ))

        # TIER 2: Cookie rotation (if cookies configured)
        ordered = []
        if self.active_label:
            ordered.extend(f for f in self.files if f["label"] == self.active_label)
        ordered.extend(f for f in self.files if f["label"] != self.active_label)

        for item in ordered:
            if item["label"] in self.failed:
                continue
            strategies.append((
                item["label"],
                self._with_proxy(["--cookies", item["path"]] + base_args),
            ))

        # TIER 3: No-cookie fallbacks with different player clients
        strategies.append(("no-cookies", self._with_proxy(list(base_args))))
        for client in NO_COOKIE_CLIENTS:
            strategies.append((
                f"no-cookies-{client.replace(',', '-')}",
                self._with_proxy(["--extractor-args", f"youtube:player_client={client}"] + base_args),
            ))

        # TIER 4: Failed cookies with web_safari client (last resort)
        for item in ordered:
            if item["label"] in self.failed:
                continue
            strategies.append((
                f"{item['label']}-web-safari",
                self._with_proxy(
                    ["--cookies", item["path"], "--extractor-args", "youtube:player_client=web_safari"]
                    + base_args
                ),
            ))
        return strategies

    def mark_success(self, label):
        if label and label != self.active_label:
            self.active_label = label
            print(f"Cookie: using {label} for the rest of this run.")
        self.saw_bot_block = False

    def mark_failed(self, label, error):
        self.last_error = error or self.last_error
        if label and label in {f["label"] for f in self.files}:
            self.failed.add(label)
            print(f"Cookie: {label} failed -> trying the next strategy.")
        if is_bot_error(error):
            self.saw_bot_block = True

    def write_alert(self, details=""):
        payload = {
            "checked_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "message": "Every YouTube download strategy failed. The cookies are probably expired, or the GitHub runner IP is blocked.",
            "details": (details or self.last_error or "")[-3000:],
            "configured_cookie_sets": [f["label"] for f in self.files],
            "failed_cookie_sets": sorted(self.failed),
            "how_to_fix": [
                "Open YouTube in Incognito with a dummy Google account.",
                "Install the 'Get cookies.txt LOCALLY' extension and export youtube.com cookies in Netscape format.",
                "Update the YT_COOKIES secret in GitHub -> Settings -> Secrets and variables -> Actions.",
                "Optional: add a second account's cookies as YT_COOKIES_2 for automatic rotation.",
                "Optional: set YT_PROXY to a residential proxy if GitHub's IP is blocked.",
                "Re-run the workflow.",
            ],
        }
        try:
            with open("cookie_alert.json", "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2, ensure_ascii=False)
            print("Cookie alert written to cookie_alert.json")
        except Exception as exc:
            print(f"Cookie alert warning: {exc}")
        return payload

    def status(self):
        return {
            "cookie_sets": [f["label"] for f in self.files],
            "failed": sorted(self.failed),
            "active": self.active_label,
            "proxy": bool(self.proxy),
        }
