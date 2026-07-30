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
    # Hide Kadence page title so the logo-matching hero is the only header
    m.tool(
        "wp_update_post_meta",
        {"post_id": 870, "post_type": "pages", "meta": {"_kad_post_title": "hide"}},
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
    m.tool(
        "wp_update_post_meta",
        {"post_id": 837, "post_type": "pages", "meta": {"_kad_post_title": "hide"}},
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
    m.tool(
        "wp_update_post_meta",
        {"post_id": 247, "post_type": "pages", "meta": {"_kad_post_title": "hide"}},
    )

    print("Hardening AI hub…")
    m.tool(
        "wp_replace_in_post",
        {
            "id": 838,
            "field": "post_content",
            "search": "Security e-drift",
            "replace": "Security e-Drift",
            "max_replacements": 20,
        },
    )
    print(
        m.tool(
            "wp_yoast_update_post_seo",
            {
                "post_id": 838,
                "seo_title": "AI, human risk & scams | Security e-Drift",
                "og_title": "AI, human risk & scams | Security e-Drift",
                "twitter_title": "AI, human risk & scams | Security e-Drift",
                "meta_description": "A curated hub on AI security, human risk, scams, and small-business defences — practical guides from Security e-Drift.",
            },
        )
    )

    print("Hardening scams hub…")
    m.tool(
        "wp_replace_in_post",
        {
            "id": 548,
            "field": "post_content",
            "search": "Security e-drift",
            "replace": "Security e-Drift",
            "max_replacements": 20,
        },
    )
    # Ensure a visible H1 (Kadence title may be styled away on some templates)
    scams = m.tool("wp_get_page", {"page_id": 548})
    content = (scams or {}).get("content") or ""
    if 'class="edrift-product-hero"' not in content and "edrift-product-hero" not in content:
        hero = (
            '<!-- wp:html -->\n'
            '<div class="edrift-product-hero">'
            '<h1 class="edrift-product-hero__title">Online scams</h1>'
            '<p class="edrift-product-hero__lede">'
            "Phishing, fakes, and fraud tips — calm guidance for UK homes and small teams."
            "</p></div>\n"
            "<!-- /wp:html -->\n\n"
        )
        print(
            m.tool(
                "wp_update_page",
                {
                    "page_id": 548,
                    "title": "Online scams — phishing, fakes and fraud tips",
                    "content": hero + content,
                    "status": "publish",
                },
            )
        )
    m.tool(
        "wp_update_post_meta",
        {"post_id": 548, "post_type": "pages", "meta": {"_kad_post_title": "hide"}},
    )
    print(
        m.tool(
            "wp_yoast_update_post_seo",
            {
                "post_id": 548,
                "seo_title": "Online scams | Security e-Drift",
                "og_title": "Online scams | Security e-Drift",
                "twitter_title": "Online scams | Security e-Drift",
                "meta_description": "Phishing, fakes, and fraud tips — calm guidance from Security e-Drift.",
            },
        )
    )

    print("Refreshing key page SEO titles…")
    for pid, seo_title, og_title in [
        (870, "Security e-Drift — the quiet compromise", "Security e-Drift — the quiet compromise"),
        (837, "Resources & next steps | Security e-Drift", "Resources & next steps | Security e-Drift"),
        (247, "About Security e-Drift — James Lugton", "About Security e-Drift — James Lugton"),
    ]:
        m.tool(
            "wp_yoast_update_post_seo",
            {
                "post_id": pid,
                "seo_title": seo_title,
                "og_title": og_title,
                "twitter_title": og_title,
            },
        )

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
