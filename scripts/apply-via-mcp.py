#!/usr/bin/env python3
"""Apply Security e-drift content updates via Easy MCP AI when WP_API_TOKEN is set.

Usage:
  export WP_API_TOKEN='wpmcp_...'
  python3 scripts/apply-via-mcp.py           # dry-run tool discovery + plan
  python3 scripts/apply-via-mcp.py --apply   # perform updates

Safe defaults: never prints the token. Aborts if token missing.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MCP_URL = "https://blog.lugton.co.uk/wp-json/easy-mcp-ai/v1/mcp"
HOME_ID = 870
PRIVACY_ID = 251


def mcp_request(token: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        MCP_URL,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        raise SystemExit(f"MCP HTTP {e.code}: {body[:800]}") from e

    # Handle possible SSE wrapping
    if body.lstrip().startswith("event:") or "data:" in body[:40]:
        chunks = []
        for line in body.splitlines():
            if line.startswith("data:"):
                chunks.append(line[5:].strip())
        body = "\n".join(chunks) if chunks else body

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return {"raw": body[:2000]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Write changes to WordPress")
    args = parser.parse_args()

    token = os.environ.get("WP_API_TOKEN", "").strip()
    if not token:
        print("WP_API_TOKEN is not set. Export the Easy MCP AI Bearer token, then re-run.")
        print("Dry-run plan only:\n")
        plan()
        return 2

    # Initialize / list tools
    init = mcp_request(
        token,
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "edrift-apply", "version": "1.0"},
            },
        },
    )
    print("initialize:", json.dumps(init, indent=2)[:1500])

    tools = mcp_request(
        token,
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
    )
    print("tools/list:", json.dumps(tools, indent=2)[:4000])

    if not args.apply:
        plan()
        print("\nRe-run with --apply after confirming tool names above.")
        return 0

    home_html = (ROOT / "site/content/homepage.html").read_text(encoding="utf-8")
    privacy_html = (ROOT / "site/content/privacy-policy.html").read_text(encoding="utf-8")
    # Logo-matched title
    home_title = "Security e-Drift"

    # Tool names vary by plugin version — try common Easy MCP AI names.
    candidates = [
        ("update_post", {"id": HOME_ID, "title": home_title, "content": home_html}),
        ("wp_update_post", {"ID": HOME_ID, "post_title": home_title, "post_content": home_html}),
        ("posts_update", {"id": HOME_ID, "title": home_title, "content": home_html}),
    ]

    print("Attempting homepage update (page", HOME_ID, ")…")
    updated = False
    for name, arguments in candidates:
        result = mcp_request(
            token,
            {
                "jsonrpc": "2.0",
                "id": 10,
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments},
            },
        )
        print(name, "=>", json.dumps(result)[:500])
        if result.get("error"):
            continue
        # success heuristic
        if "error" not in json.dumps(result).lower() or "isError" not in json.dumps(result):
            updated = True
            break

    if not updated:
        print("Could not auto-match a write tool. Use tools/list output and update scripts/apply-via-mcp.py tool names.")
        return 1

    print("Attempting privacy update (page", PRIVACY_ID, ")…")
    mcp_request(
        token,
        {
            "jsonrpc": "2.0",
            "id": 11,
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": {"id": PRIVACY_ID, "content": privacy_html}
                if "id" in arguments
                else {"ID": PRIVACY_ID, "post_content": privacy_html},
            },
        },
    )
    print("Done. Verify on the live site and complete nav/footer/CSS manually per site/APPLY.md.")
    return 0


def plan() -> None:
    print(
        """Planned live updates:
  1. Page 870 (Home)       <- site/content/homepage.html
  2. Page 251 (Privacy)    <- site/content/privacy-policy.html
Manual (wp-admin / theme):
  3. Append site/theme/edrift-patches.css to child theme edrift.css; bump version
  4. Rebuild primary nav per site/content/nav-ia.md
  5. Add footer HTML from site/content/footer.html
  6. Deploy security/subscribe-endpoint.php
  7. Work through security/hardening-checklist.md
"""
    )


if __name__ == "__main__":
    sys.exit(main())
