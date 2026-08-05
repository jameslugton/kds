#!/usr/bin/env python3
"""Deploy voice-card revamp: flagship pages + core how-to posts."""

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
}

POSTS = {
    461: {
        "file": REVAMP / "post-461.html",
        "title": "How Scams Reach You (and How to Spot Them Before They Catch You)",
        "excerpt": "Stop. Pause. Three questions before you click — a plain habit for spotting scams across email, phone, WhatsApp, and more.",
    },
    463: {
        "file": REVAMP / "post-463.html",
        "title": "What To Do If You’ve Been Caught Out by a Scam",
        "excerpt": "A clear order of actions after a miss — stop contact, guard accounts, tell the bank, report — without the jargon.",
    },
    239: {
        "file": REVAMP / "post-239.html",
        "title": "Everyday Cybersecurity Habits (No Cape Required)",
        "excerpt": "Ordinary habits for non-technical people: pause before you click, unique passwords, and an extra step to guard accounts.",
    },
    288: {
        "file": REVAMP / "post-288.html",
        "title": "A 10-Minute Cyber Check",
        "excerpt": "A short device, inbox, and account routine you can keep — plus a self-check on whether your bank passcode is strong enough.",
    },
    781: {
        "file": REVAMP / "post-781.html",
        "title": "Before You Paste It Into the Bot: AI Risks Worth Slowing Down For",
        "excerpt": "Slow down before you paste and before you use the answer — secrets, wrong certainty, and documents that try to steer the bot.",
    },
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


def main() -> int:
    token = os.environ.get("WP_API_TOKEN", "").strip()
    if not token:
        print("WP_API_TOKEN required", file=sys.stderr)
        return 2

    m = MCP(token)
    m.call(
        "initialize",
        {
            "protocolVersion": "2025-11-25",
            "capabilities": {},
            "clientInfo": {"name": "edrift-voice-revamp", "version": "1.0"},
        },
    )
    m.notify("notifications/initialized")

    for page_id, path in PAGES.items():
        html = path.read_text(encoding="utf-8")
        print(f"Updating page {page_id} ({path.name})…")
        print(m.tool("wp_update_page", {"page_id": page_id, "content": html, "status": "publish"}))

    for post_id, meta in POSTS.items():
        html = meta["file"].read_text(encoding="utf-8")
        # Keep humanize copies in sync for 239/288
        humanize = VOICE / "humanize" / f"post-{post_id}.html"
        if humanize.parent.exists():
            humanize.write_text(html, encoding="utf-8")
        voice_post = VOICE / f"post-{post_id}.html"
        if voice_post.exists() or post_id in (239, 288):
            voice_post.write_text(html, encoding="utf-8")
        print(f"Updating post {post_id} ({meta['title']})…")
        print(
            m.tool(
                "wp_update_post",
                {
                    "post_id": post_id,
                    "title": meta["title"],
                    "content": html,
                    "excerpt": meta["excerpt"],
                    "status": "publish",
                },
            )
        )

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
