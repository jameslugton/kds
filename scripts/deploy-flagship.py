#!/usr/bin/env python3
"""Deploy flagship Security e-Drift marketing package to production via Easy MCP AI."""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
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
        with urllib.request.urlopen(req, timeout=120) as r:
            body = r.read().decode("utf-8", "replace")
            if r.headers.get("Mcp-Session-Id"):
                self.sid = r.headers.get("Mcp-Session-Id")
        if not body.strip():
            return {}
        if body.lstrip().startswith("event:") or "data:" in body[:80]:
            chunks = [line[5:].strip() for line in body.splitlines() if line.startswith("data:")]
            body = "\n".join(c for c in chunks if c and c != "[DONE]")
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
            return {
                "text": joined,
                "isError": res.get("result", {}).get("isError"),
            }


def strip_file_comment(html: str) -> str:
    return re.sub(r"^<!--.*?-->\n*", "", html, count=1, flags=re.S).strip()


def build_home() -> str:
    css = (ROOT / "site/theme/edrift-patches.css").read_text(encoding="utf-8")
    # Keep CSS lean in HTML: drop file header comment block only
    css = re.sub(r"^/\*\*.*?\*/\n*", "", css, count=1, flags=re.S)
    body = strip_file_comment((ROOT / "site/content/homepage.html").read_text(encoding="utf-8"))
    # Replace placeholder style block
    if '<style id="edrift-marketing-patches">' in body:
        body = re.sub(
            r'<style id="edrift-marketing-patches">.*?</style>',
            f'<style id="edrift-marketing-patches">\n{css}\n</style>',
            body,
            count=1,
            flags=re.S,
        )
    else:
        body = f'<style id="edrift-marketing-patches">\n{css}\n</style>\n{body}'
    return f"<!-- wp:html -->\n{body}\n<!-- /wp:html -->"


def wrap_html(path: Path) -> str:
    body = strip_file_comment(path.read_text(encoding="utf-8"))
    css = (ROOT / "site/theme/edrift-patches.css").read_text(encoding="utf-8")
    css = re.sub(r"^/\*\*.*?\*/\n*", "", css, count=1, flags=re.S)
    # Lighter inline CSS on inner pages: product hero + shelf + subscribe + manifesto rule
    return (
        "<!-- wp:html -->\n"
        f'<style id="edrift-marketing-patches">\n{css}\n</style>\n'
        f"{body}\n"
        "<!-- /wp:html -->"
    )


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
            "clientInfo": {"name": "edrift-flagship", "version": "2.0"},
        },
    )
    m.notify("notifications/initialized")

    print("Updating site settings…")
    print(
        m.tool(
            "wp_update_site_settings",
            {
                "title": "Security e-Drift",
                "description": "Cybersecurity that stays calm — so you can stay sharp.",
            },
        )
    )

    print("Updating homepage…")
    print(
        m.tool(
            "wp_update_page",
            {
                "page_id": 870,
                "title": "Security e-Drift",
                "content": build_home(),
                "status": "publish",
            },
        )
    )

    print("Updating resources…")
    print(
        m.tool(
            "wp_update_page",
            {
                "page_id": 837,
                "title": "Resources & next steps",
                "content": wrap_html(ROOT / "site/content/resources.html"),
                "status": "publish",
            },
        )
    )

    print("Updating about…")
    print(
        m.tool(
            "wp_update_page",
            {
                "page_id": 247,
                "title": "About Security e-Drift and James Lugton",
                "content": wrap_html(ROOT / "site/content/about.html"),
                "status": "publish",
            },
        )
    )

    print("Fixing AI hub callout…")
    print(
        m.tool(
            "wp_replace_in_post",
            {
                "post_id": 838,
                "search": "<strong>Remember this:</strong> <strong>Niche focus:</strong> AI + human risk + scams + small-business security. Start here, then pick one habit to practise.",
                "replace": "<strong>Remember this:</strong> prefer AI as an advisor by default. Promote a tool to actor only with a narrow job — and a human brake.",
            },
        )
    )

    # Also fix brand casing on AI hub intro if present
    m.tool(
        "wp_replace_in_post",
        {
            "post_id": 838,
            "search": "Security e-drift’s",
            "replace": "Security e-Drift’s",
        },
    )

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
