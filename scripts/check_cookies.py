"""
Standalone cookie health check used by .github/workflows/cookie-health.yml.

Run locally:
    python scripts/check_cookies.py

Exit codes:
    0 = at least one strategy works (PO Token, cookie, or no-cookie)
    1 = all strategies failed
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from cookie_manager import CookieManager, is_bot_error, PO_TOKEN_CLIENTS, NO_COOKIE_CLIENTS  # noqa: E402

TEST_URL = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # "Me at the zoo", stable public video


def test_strategy(label, args):
    command = ["yt-dlp"] + args + [
        "--simulate", "--skip-download", "--no-warnings", "--no-playlist",
        "--socket-timeout", "30",
        TEST_URL,
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    except Exception as exc:
        return False, str(exc)

    output = ((result.stdout or "") + "\n" + (result.stderr or "")).strip()
    if result.returncode == 0:
        return True, "OK"
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    detail = lines[-1] if lines else f"exit code {result.returncode}"
    return False, detail


def main():
    manager = CookieManager()
    results = []

    # Test Tier 1: PO Token strategies
    base_args = ["--js-runtimes", "node", "--remote-components", "ejs:github", "--no-warnings"]
    for client in PO_TOKEN_CLIENTS:
        label = f"po-token-{client}"
        args = base_args + ["--extractor-args", f"youtube:player_client={client}", "--extractor-args", "youtube:po_token=bgutil.ytdlp_pot_provider"]
        ok, detail = test_strategy(label, args)
        results.append({"strategy": label, "valid": ok, "detail": detail[-800:]})
        print(f"{label}: {'VALID' if ok else 'INVALID'} - {detail[:200]}")

    # Test Tier 2: Cookie strategies
    for item in manager.files:
        label = item["label"]
        args = base_args + ["--cookies", item["path"]]
        ok, detail = test_strategy(label, args)
        results.append({"strategy": label, "valid": ok, "detail": detail[-800:]})
        print(f"{label}: {'VALID' if ok else 'INVALID'} - {detail[:200]}")

    # Test Tier 3: No-cookie fallbacks
    for client in NO_COOKIE_CLIENTS:
        label = f"no-cookies-{client.replace(',', '-')}"
        args = base_args + ["--extractor-args", f"youtube:player_client={client}"]
        ok, detail = test_strategy(label, args)
        results.append({"strategy": label, "valid": ok, "detail": detail[-800:]})
        print(f"{label}: {'VALID' if ok else 'INVALID'} - {detail[:200]}")

    # Test Tier 4: Failed cookies with web_safari (if any cookies configured)
    for item in manager.files:
        if item["label"] in {r["strategy"] for r in results if not r["valid"]}:
            continue
        label = f"{item['label']}-web-safari"
        args = base_args + ["--cookies", item["path"], "--extractor-args", "youtube:player_client=web_safari"]
        ok, detail = test_strategy(label, args)
        results.append({"strategy": label, "valid": ok, "detail": detail[-800:]})
        print(f"{label}: {'VALID' if ok else 'INVALID'} - {detail[:200]}")

    payload = {
        "checked_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "results": results,
        "total_tested": len(results),
        "valid": sum(1 for item in results if item["valid"]),
    }
    with open("cookie_status.json", "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)

    if payload["valid"] > 0:
        print(f"Cookie health OK: {payload['valid']}/{payload['total_tested']} strategy(s) valid.")
        return 0

    details = "\n".join(f"{item['strategy']}: {item['detail']}" for item in results)
    if any(is_bot_error(item["detail"]) for item in results):
        manager.write_alert(details)
    print("Cookie health FAILED: every strategy is invalid.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
