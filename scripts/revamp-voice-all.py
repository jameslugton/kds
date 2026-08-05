#!/usr/bin/env python3
"""Deploy full voice-card revamp: flagship hubs + all non-story posts."""

from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOICE = ROOT / "site/content/voice"
REVAMP = VOICE / "revamp"
MCP_URL = "https://blog.lugton.co.uk/wp-json/easy-mcp-ai/v1/mcp"

PAGES = {
    870: VOICE / "home.html",
    247: VOICE / "about.html",
    837: VOICE / "resources.html",
    548: VOICE / "scams.html",
    838: VOICE / "ai-hub.html",
    1006: VOICE / "stories.html",
}

# Earlier wave + full wave
CORE_POSTS = {
    461: "How Scams Reach You (and How to Spot Them Before They Catch You)",
    463: "What To Do If You’ve Been Caught Out by a Scam",
    239: "Everyday Cybersecurity Habits (No Cape Required)",
    288: "A 10-Minute Cyber Check",
    781: "Before You Paste It Into the Bot: AI Risks Worth Slowing Down For",
}


class MCP:
    def __init__(self, token: str):
        self.token = token
        self.sid = None
        self._n = 0

    def _req(self, payload: dict) -> dict:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.sid:
            headers["Mcp-Session-Id"] = self.sid
        req = urllib.request.Request(
            MCP_URL, data=json.dumps(payload).encode(), method="POST", headers=headers
        )
        with urllib.request.urlopen(req, timeout=180) as r:
            body = r.read().decode("utf-8", "replace")
            if r.headers.get("Mcp-Session-Id"):
                self.sid = r.headers.get("Mcp-Session-Id")
        if not body.strip():
            return {}
        if body.lstrip().startswith("event:") or "data:" in body[:80]:
            chunks = [line[5:].strip() for line in body.splitlines() if line.startswith("data:")]
            body = "\n".join(c for c in chunks if c and c != "[DONE]")
            if not body:
                return {}
        return json.loads(body)

    def call(self, method: str, params=None) -> dict:
        self._n += 1
        payload = {"jsonrpc": "2.0", "id": self._n, "method": method}
        if params is not None:
            payload["params"] = params
        return self._req(payload)

    def notify(self, method: str, params=None) -> None:
        payload = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params
        self._req(payload)

    def tool(self, name: str, arguments: dict):
        res = self.call("tools/call", {"name": name, "arguments": arguments})
        if "error" in res:
            return res
        content = res.get("result", {}).get("content", [])
        texts = [c.get("text", "") for c in content if c.get("type") == "text"]
        joined = "\n".join(texts)
        try:
            return json.loads(joined)
        except Exception:
            return {"text": joined, "isError": res.get("result", {}).get("isError")}


def load_post_map() -> dict[int, str]:
    """id -> title from manifest + core."""
    titles = dict(CORE_POSTS)
    manifest = json.loads((REVAMP / "manifest.json").read_text(encoding="utf-8"))
    for row in manifest:
        titles[int(row["id"])] = row["title"]
    return titles


def resolve_html(post_id: int) -> Path:
    for path in (
        REVAMP / f"post-{post_id}.html",
        VOICE / "humanize" / f"post-{post_id}.html",
        VOICE / f"post-{post_id}.html",
    ):
        if path.exists():
            return path
    raise FileNotFoundError(f"No HTML for post {post_id}")


def main() -> int:
    token = os.environ.get("WP_API_TOKEN", "").strip()
    if not token:
        print("WP_API_TOKEN required", file=sys.stderr)
        return 2

    titles = load_post_map()
    m = MCP(token)
    m.call(
        "initialize",
        {
            "protocolVersion": "2025-11-25",
            "capabilities": {},
            "clientInfo": {"name": "edrift-voice-revamp-all", "version": "2.0"},
        },
    )
    m.notify("notifications/initialized")

    # Light how-to guides intro via replace
    print("Patching how-to guides intro…")
    print(
        m.tool(
            "wp_replace_in_post",
            {
                "id": 420,
                "field": "post_content",
                "search": "<h2 class=\"wp-block-heading\">Start with these evergreen guides</h2>",
                "replace": (
                    "<p>Plain guides for non-technical people who need to protect themselves — "
                    "pick one habit, use it this week.</p>\n\n"
                    "<!-- wp:heading -->\n"
                    "<h2 class=\"wp-block-heading\">Start with these guides</h2>\n"
                    "<!-- /wp:heading -->"
                ),
            },
        )
    )

    for page_id, path in PAGES.items():
        html = path.read_text(encoding="utf-8")
        print(f"Updating page {page_id} ({path.name})…")
        out = m.tool("wp_update_page", {"page_id": page_id, "content": html, "status": "publish"})
        err = out.get("isError") or (isinstance(out.get("text"), str) and "Error" in out.get("text", "")[:40])
        print("  OK" if not err else out)

    failures = []
    for post_id, title in sorted(titles.items()):
        path = resolve_html(post_id)
        html = path.read_text(encoding="utf-8")
        print(f"Updating post {post_id} ({title[:50]})…")
        out = m.tool(
            "wp_update_post",
            {
                "post_id": post_id,
                "title": title,
                "content": html,
                "status": "publish",
            },
        )
        if out.get("isError") or (isinstance(out, dict) and out.get("id") != post_id and "Error" in str(out)):
            # success objects have id
            if not (isinstance(out, dict) and out.get("id") == post_id):
                failures.append((post_id, out))
                print("  FAIL", out)
            else:
                print("  OK")
        else:
            print("  OK" if out.get("id") == post_id else out)

    print(f"Done. Failures: {len(failures)}")
    for pid, out in failures:
        print(pid, out)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
