#!/usr/bin/env python3
"""Deploy design-imperfection fixes to Security e-Drift via Easy MCP AI.

Rewrites hub/home markup (no atmos / feature pills / brand restamp on inner pages)
and injects site/theme/edrift-design-fixes.css inline + into reusable block 572.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOICE = ROOT / "site/content/voice"
MCP_URL = "https://blog.lugton.co.uk/wp-json/easy-mcp-ai/v1/mcp"


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
            "clientInfo": {"name": "edrift-design-fix", "version": "1.0"},
        },
    )
    m.notify("notifications/initialized")

    pages = [
        (870, "Security e-Drift", "home.html"),
        (247, "About Security e-Drift and James Lugton", "about.html"),
        (837, "Resources", "resources.html"),
        (1006, "Stories", "stories.html"),
        (548, "Online scams — phishing, fakes and fraud tips", "scams.html"),
        (838, "AI, human risk & scams", "ai-hub.html"),
    ]
    for pid, title, fname in pages:
        content = (VOICE / fname).read_text(encoding="utf-8")
        print(f"Updating page {pid}…")
        print(m.tool("wp_update_page", {"page_id": pid, "title": title, "content": content, "status": "publish"}))
        m.tool(
            "wp_update_post_meta",
            {
                "post_id": pid,
                "post_type": "pages",
                "meta": {
                    "_kad_post_title": "hide",
                    "_kad_post_classname": "",
                    "_kad_post_transparent": "",
                    "_edrift_hub_type": "",
                },
            },
        )

    home = (VOICE / "home.html").read_text(encoding="utf-8")
    style = re.search(r"<style id=\"edrift-design-fixes\">[\s\S]*?</style>", home)
    if style:
        aff = m.tool("wp_get_block", {"block_id": 572})
        old = (aff or {}).get("content") or ""
        block = f'<!-- wp:html -->\n{style.group(0)}\n<!-- /wp:html -->\n\n'
        if "edrift-design-fixes" in old:
            new = re.sub(
                r"<!-- wp:html -->\s*<style id=\"edrift-design-fixes\">[\s\S]*?</style>\s*<!-- /wp:html -->\s*",
                block,
                old,
                count=1,
            )
        else:
            new = block + old
        print("Updating block 572…")
        print(m.tool("wp_update_block", {"block_id": 572, "content": new}))

    print("Done. Theme PHP still may add body.edrift-hub-landing on some page IDs; CSS neutralizes it.")
    print("For a permanent theme CSS merge, append site/theme/edrift-design-fixes.css to assets/edrift.css on the host.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
