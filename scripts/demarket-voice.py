#!/usr/bin/env python3
"""Calm the marketing/hype voice on Security e-Drift pages and worst AI-filler posts.

Preserves layout/CSS. Removes conversion hype, repetition, unsupported claims,
and stock AI-blog filler. Requires WP_API_TOKEN.
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


def multi_replace(text: str, pairs: list[tuple[str, str]]) -> str:
    for old, new in pairs:
        if old not in text:
            # allow already-applied
            continue
        text = text.replace(old, new)
    return text


def demarket_home(html: str) -> str:
    return multi_replace(
        html,
        [
            (
                "Clear guidance for UK homes and small teams. Scams, AI habits, and everyday security — without the jargon or the fear.",
                "Clear guidance for UK homes and small teams. Scams, AI habits, and everyday security — in plain English.",
            ),
            ("Print the SMB checklist", "SMB checklist"),
            ("Or pick your door", "Browse topics"),
            ('aria-label="What you get"', 'aria-label="At a glance"'),
            ("Practical, not theatrical", "Guides and stories"),
            (
                "Written for people who open the laptop between school runs, shop tills, and real invoices — not for people who live in a SOC.",
                "Written for people who open the laptop between school runs, shop tills, and real invoices.",
            ),
            ("Your next move", "Useful starting points"),
            ("Print this. Tick it this week.", "Small Business Cybersecurity Checklist 2026"),
            (
                "Cold start? Don’t browse — use one artefact. The Small Business Cybersecurity Checklist 2026 is the baseline most micro teams can finish in one sitting.",
                "A practical baseline for micro and small teams — MFA, invoices, backups, and a simple 90-day plan.",
            ),
            ("Short sessions that change Tuesday behaviour", "Short sessions tied to everyday work"),
            ("All resources &amp; session requests", "All resources"),
            ("Templates, hubs, and calm awareness sessions", "Checklists, hubs, and session notes"),
            ("Three doors in", "Where to start"),
            ("Already know what this week feels like? Pick one door.", "Three common starting points."),
            ("Dated field notes — so you can see the place is alive.", "Recent pieces."),
            (
                "The Complete Small Business Cybersecurity Checklist 2026",
                "Small Business Cybersecurity Checklist 2026",
            ),
            ("Get monthly scam alerts + new templates", "Email updates"),
            (
                "Practical notes for UK homes and small teams — new checklists and AI habits when they ship. No spam. Free to leave.",
                "Occasional notes when new checklists or guides are published. Unsubscribe anytime.",
            ),
            ("Get the updates", "Subscribe"),
            ("Stories that stick", "Stories"),
            (
                "Short chapters. No tech jargon. Security learned the way people actually remember it.",
                "Short chapters from Jim’s shop and the river tales.",
            ),
            (
                "Small mistakes in a small business that snowball — and the calm fixes that stop them.",
                "Small mistakes in a small business that snowball — and the ordinary fixes that stop them.",
            ),
            ("Request a calm awareness session", "Ask about an awareness session"),
            (
                "<em>Written and security-checked by James Lugton.</em> Educational guidance only — not formal assurance or legal advice.",
                "Written by James Lugton. Educational guidance only — not formal assurance or legal advice.",
            ),
            (
                "<strong>How this stays free:</strong> light ads and occasional affiliate links. If I recommend a tool and you buy through a link, I may earn a small fee at no extra cost to you — <a href=\"/affiliate-disclosure/\">full disclosure</a>.",
                "Light ads and occasional affiliate links help keep the blog free to read — <a href=\"/affiliate-disclosure/\">disclosure</a>.",
            ),
        ],
    )


def demarket_about(html: str) -> str:
    return multi_replace(
        html,
        [
            (
                "A working analyst in <em>Yorkshire</em> — calm guidance, no theatre",
                "About James Lugton",
            ),
            (
                "I write Security e-Drift so everyday security stays clear and usable — for families, freelancers, and small teams who need clarity, not jargon.",
                "I write Security e-Drift for families, freelancers, and small teams who need clear security guidance they can use.",
            ),
            ("Why e-Drift exists", "Why this blog"),
            ('aria-label="What you get"', 'aria-label="At a glance"'),
            (
                "and small‑business routines that reduce blast radius without slowing anyone down.",
                "and small‑business routines that keep risk smaller without turning every day into a project.",
            ),
            (
                "The tagline on the logo — <em>the quiet compromise</em> — is the thing we catch before it becomes a week from hell.",
                "The tagline on the logo — <em>the quiet compromise</em> — is the thing worth catching while the fix is still ordinary.",
            ),
            (
                "I’ve run calm awareness conversations for small retail and office teams who needed habits they could use the same week — invoice checks, MFA prompts, and AI paste rules — without a fear slide deck.",
                "I’ve run awareness sessions for small retail and office teams who needed habits they could use the same week — invoice checks, MFA prompts, and AI paste rules — without scare tactics.",
            ),
            ("What to do next", "Further reading"),
            ("Pick one action. One is enough.", "A few useful next reads."),
            ("Request a calm awareness session", "Ask about an awareness session"),
            ("Why work with James →", "About the writing →"),
        ],
    )


def demarket_resources(html: str) -> str:
    return multi_replace(
        html,
        [
            (
                "Pick one <em>artefact</em>. Use it this week.",
                "Resources",
            ),
            (
                "Awareness fades without a next action. Checklists, templates, and practical sessions — then come back when you need the next one.",
                "Checklists, templates, and session notes for UK homes and small teams.",
            ),
            ('aria-label="What you get"', 'aria-label="At a glance"'),
            ("Start with one artefact", "Guides and templates"),
            (
                "written for real small businesses, not enterprise theatre.",
                "written for small businesses.",
            ),
            (
                "Short sessions that change Tuesday behaviour — including phishing simulation do’s and don’ts.",
                "Short sessions tied to everyday work — including phishing simulation do’s and don’ts.",
            ),
            ("Request a calm awareness session", "Awareness sessions"),
            (
                "Practical sessions for small teams and community groups — phishing judgement, AI-related human risk, and everyday habits. No scare slides.",
                "Sessions for small teams and community groups on phishing judgement, AI-related human risk, and everyday habits.",
            ),
            (
                "Outcomes: spot urgency tricks, pause before acting, know a simple kill-switch / verify habit",
                "Focus: spot urgency tricks, pause before acting, and use a simple verify / stop habit",
            ),
            ("Email to request a session", "Email to ask about a session"),
            ("Why work with James →", "About James →"),
            ("Stay in the habit", "Email updates"),
            ("Get monthly scam alerts + new templates", "Occasional updates"),
            (
                "Practical notes for UK homes and small teams when new checklists and habits ship. No spam.",
                "Notes when new checklists or guides are published. Unsubscribe anytime.",
            ),
            ("Get the updates", "Subscribe"),
        ],
    )


def demarket_stories(html: str) -> str:
    return multi_replace(
        html,
        [
            (
                "Security you can <em>remember</em> — short chapters that stick",
                "Stories",
            ),
            (
                "No tech jargon. Security learned the way people actually remember it — Jim’s shop and River tales.",
                "Short chapters from Jim’s shop and the river tales — security learned through ordinary situations.",
            ),
            ('aria-label="What you get"', 'aria-label="At a glance"'),
            ("Lessons that stick", "Short chapters"),
        ],
    )


def demarket_scams(html: str) -> str:
    return multi_replace(
        html,
        [
            (
                "When something feels <em>off</em> — calm next steps",
                "Online scams",
            ),
            (
                "Phishing, fakes, and fraud tips for UK homes and small teams. Spot the ask, pause the urgency, and know what to do after a miss.",
                "Phishing, fakes, and fraud tips for UK homes and small teams — how to spot the ask, pause the urgency, and what to do after a miss.",
            ),
            ("See AI risk", "AI &amp; human risk"),
            ('aria-label="What you get"', 'aria-label="At a glance"'),
        ],
    )


def demarket_ai_hub(html: str) -> str:
    html = multi_replace(
        html,
        [
            (
                "AI changes the speed and polish of scams — but people still decide. This hub gathers Security e-Drift’s strongest guidance on AI tools, human risk, and everyday fraud.",
                "AI changes the speed and polish of scams — but people still decide. This hub collects Security e-Drift guides on AI tools, human risk, and everyday fraud.",
            ),
            (
                "A curated hub on AI security, human risk, scams, and small-business defences — practical guides from Security e-Drift.",
                "Guides on AI tools, human risk, scams, and small-business habits from Security e-Drift.",
            ),
        ],
    )
    # Replace fake "Coming up / scheduled" block with published pieces only
    old_block = re.search(
        r"<!-- wp:heading -->\s*<h2 class=\"wp-block-heading\">Coming up / scheduled</h2>.*?<!-- /wp:list -->",
        html,
        flags=re.S,
    )
    if old_block:
        replacement = """<!-- wp:heading -->
<h2 class="wp-block-heading">Also on AI risk</h2>
<!-- /wp:heading -->

<!-- wp:list -->
<ul class="wp-block-list"><!-- wp:list-item -->
<li><a href="/shadow-ai-at-work-and-at-home/">Shadow AI at Work and at Home</a></li>
<!-- /wp:list-item -->
<!-- wp:list-item -->
<li><a href="/if-someone-else-is-steering-your-ai/">If Someone Else Is Steering Your AI</a></li>
<!-- /wp:list-item -->
<!-- wp:list-item -->
<li><a href="/when-automation-keeps-going/">When Automation Keeps Going</a></li>
<!-- /wp:list-item -->
</ul>
<!-- /wp:list -->"""
        html = html[: old_block.start()] + replacement + html[old_block.end() :]
    return html


def demarket_post_191(html: str) -> str:
    html = multi_replace(
        html,
        [
            (
                "In the ever-evolving landscape of cybersecurity, few threats have proven as persistent and damaging as Magecart and e-skimming attacks. These client-side exploits target the very heart of e-commerce: the checkout page. But as attackers grow more sophisticated, so must our defenses. Enter script monitoring—a proactive strategy that not only detects malicious behaviour but also empowers authorisation, decline and justification of why and the purpose of scripts that are prese",
                "Magecart and e-skimming attacks still hit checkout pages because they run in the browser, where ordinary firewalls and endpoint tools often cannot see them. Script monitoring helps you notice what is loading on the page — and decide which scripts are allowed, declined, or need a clear business reason.",
            ),
            ("🚀 Final Thoughts", "Closing note"),
            (
                "Magecart and e-skimming are not going away—but with script monitoring, businesses can fight back. By authorising safe scripts and declining malicious ones or ones you’re not sure about, organisations can transform their security posture from reactive to resilient. It’s not just about stopping attacks it’s about staying one step ahead and knowing what is running and happening.",
                "Magecart and e-skimming are not disappearing. Authorising known-good scripts, declining unknowns, and knowing what runs at checkout reduces the chance of a quiet skim lasting for weeks.",
            ),
        ],
    )
    # Fix truncated opener if original was mid-word - handle longer original
    if "ever-evolving landscape" in html:
        html = re.sub(
            r"In the ever-evolving landscape of cybersecurity,.*?(?=\n|<h2|##|</p>)",
            "Magecart and e-skimming attacks still hit checkout pages because they run in the browser, where ordinary firewalls and endpoint tools often cannot see them. Script monitoring helps you notice what is loading on the page — and decide which scripts are allowed, declined, or need a clear business reason. ",
            html,
            count=1,
            flags=re.S,
        )
    return html


def demarket_post_195(html: str) -> str:
    html = multi_replace(
        html,
        [
            (
                "In the shadowy corners of the internet, a new breed of cyberattack is taking shape one that blends artificial intelligence, Magecart style e-skimming, and the deceptive finesse of clickjacking. It’s not just a technical threat; it’s a psychological one. And it’s turning the web into a minefield of trust.",
                "Some checkout attacks now mix familiar tricks: Magecart-style skimming, clickjacking overlays, and AI-written bait that looks ordinary. The technical pieces matter — but so does the habit of slowing down when a page asks for payment details.",
            ),
            ("🎯 The Setup: A Watering Hole with Digital Bait", "How the trap is set"),
            ("🛡️ Final Thoughts: Trust Is the New Attack Surface", "Closing note"),
            (
                "As AI continues to evolve, so do the tactics of cybercriminals. The line between real and fake is blurring and the cost of misplaced trust is rising. In this new era, security isn’t just about firewalls and patches. It’s about vigilance, visibility, and verifying everything. Because when AI, vulnerabilities, and Magecart collide, the result isn’t just a breach, it’s a breach of trust.",
                "As the bait gets more polished, the useful response stays ordinary: verify the page, watch what scripts run at checkout, and treat unexpected payment prompts with suspicion.",
            ),
        ],
    )
    if "shadowy corners of the internet" in html:
        html = re.sub(
            r"In the shadowy corners of the internet,.*?(?=\n|<h2|##|🎯|</p>)",
            "Some checkout attacks now mix familiar tricks: Magecart-style skimming, clickjacking overlays, and AI-written bait that looks ordinary. The technical pieces matter — but so does the habit of slowing down when a page asks for payment details. ",
            html,
            count=1,
            flags=re.S,
        )
    return html


def demarket_post_169(html: str) -> str:
    html = multi_replace(
        html,
        [
            (
                "You wake up to an email from your bank. “Urgent: Suspicious activity detected on your account.” Your heart races. You click the link. It looks real. But is it? Scammers have mastered the art of deception, using everything from fake emails to AI-powered deepfake technology. These scams are getting so advanced that even tech-savvy people are falling for them. So, how do you stay ahead of the game? Let’s break it down.",
                "An email that looks like your bank — “Urgent: suspicious activity” — is designed to make you move before you think. Phishing has always worked that way. Deepfakes add another polish to voice and video. You do not need special tools to respond well: pause, verify through a channel you already trust, and do not use the links or numbers in the message.",
            ),
            ("## The Phishing Tricks You Need to Watch Out For", "## Common phishing tricks"),
            ("Final Thought", "Closing note"),
            (
                "Phishing scams aren’t just obvious anymore they’re disguised as normal emails, messages, and even deepfake videos. The good news? You don’t need to be a cybersecurity expert to stay safe. Just question everything, trust your instincts, and never rush into clicking or responding. Stay sharp. Stay safe. Scammers can’t win if you don’t play their game.",
                "Phishing is often disguised as ordinary mail, texts, or even a familiar-sounding voice note. You do not need to be an expert: slow down, verify out of band, and treat urgency as a warning sign rather than a reason to hurry.",
            ),
        ],
    )
    return html


def demarket_post_148(html: str) -> str:
    html = multi_replace(
        html,
        [
            (
                "Ever received an email that looked too real to be fake? Maybe a message claiming to be from your bank, asking you to \"verify your account details\" right away? These tricks are part of a social engineering scam —where fraudsters manipulate people into handing over private information, no hacking required. Unlike movie-style cyberattacks that rely on fancy code, social engineering targets people , using deception, urgency, and even fear to get you to act before you think.",
                "A message that looks like your bank and asks you to “verify your account details” right away is often social engineering: someone trying to get you to hand over information or access without needing to break any software. The pressure is the point — urgency, fear, and familiarity.",
            ),
            ("🔍 Stay Alert, Stay Secure", "Closing note"),
            (
                "Social engineering is sneaky, but knowledge is your best defense. Always question unusual requests, double-check who you're dealing with, and trust your instincts . Cybercriminals rely on people acting too quickly—so take a moment, stay cautious, and don’t give them an easy win!",
                "Unusual requests deserve a pause. Check who you are dealing with through a channel you already trust, and do not let urgency decide for you.",
            ),
        ],
    )
    return html


def demarket_post_140(html: str) -> str:
    html = multi_replace(
        html,
        [
            (
                "In the evolving landscape of cybersecurity, organizations often focus on technical solutions—firewalls, encryption, intrusion detection systems. However, one of the most critical elements of cyber defense isn't a piece of software or hardware. It's the human firewall —the individuals who interact with systems daily, making decisions that can either fortify or weaken security.",
                "Organisations often buy firewalls, encryption, and detection tools first. Those matter. So do the everyday decisions people make: whether to click, approve, share, or pause. That ordinary judgement is what people mean by a “human firewall.”",
            ),
            (
                "But at the core, human awareness and responsibility will remain the ultimate line of defense . The strongest security systems are not built solely with technology—they are built with people who understand their role in protecting data, systems, and software. Strengthening the human firewall is not just a necessity; it is an imperative for securing the future.",
                "Tools help, but they do not replace clear habits. The useful work is helping people recognise pressure, verify odd requests, and know who to ask when something feels wrong.",
            ),
        ],
    )
    if "evolving landscape of cybersecurity" in html:
        html = re.sub(
            r"In the evolving landscape of cybersecurity,.*?(?=\n|<h2|##|What Is|</p>)",
            "Organisations often buy firewalls, encryption, and detection tools first. Those matter. So do the everyday decisions people make: whether to click, approve, share, or pause. That ordinary judgement is what people mean by a “human firewall.” ",
            html,
            count=1,
            flags=re.S,
        )
    return html


def demarket_post_239(html: str) -> str:
    html = multi_replace(
        html,
        [
            (
                "It’s for Everyday Champions —- Like You Cybersecurity isn’t reserved for degrees, certifications, or tech jargon. It’s for parents, freelancers, shop owners, students, small businesses, grandparents—for you. For everyone. You don’t need a hoodie or a job title. You just need to care enough to protect what matters. Because the difference between clicking a bad link and keeping your money, identity, and privacy safe? It’s often just a moment of awareness—a pause to ask: Is this real? Is this safe?",
                "Cybersecurity is not reserved for degrees, certifications, or job titles. Parents, freelancers, shop owners, students, and grandparents all make security decisions. The useful skill is ordinary: a pause to ask whether a message, link, or request is real before you act.",
            ),
            ("🧠 What ", "What "),
        ],
    )
    # Soften cheerleading ending if present
    html = re.sub(
        r"You’re not just reacting.*?it starts with you\.?",
        "Small habits — pausing on odd messages, keeping software current, talking about scams at home or work — do more than slogans.",
        html,
        count=1,
        flags=re.S,
    )
    return html


def demarket_post_288(html: str) -> str:
    html = multi_replace(
        html,
        [
            (
                "Most people imagine cybersecurity as something complicated — firewalls, encryption, specialist tools. But the truth is far more ordinary: your daily habits do more to protect you than any piece of software ever will. A simple 10‑minute check, done once a day with quiet consistency, can stop the majority of opportunistic attacks long before they become disasters. It’s the digital equivalent of locking your doors and checking the windows — small actions that prevent big problems.",
                "Cybersecurity often sounds like specialist tools. Day to day, a short habit usually matters more: a few minutes to check devices, accounts, and updates. Think of it like locking the door and glancing at the windows — small, repeatable, and easy to keep.",
            ),
            (
                "can stop the majority of opportunistic attacks long before they become disasters.",
                "can catch common problems early.",
            ),
            ("The Real Outcome: Quiet Confidence", "Why bother"),
            (
                "When you build this into your day — the same way you check the front door is locked — something shifts. You feel more in control. You stop worrying about “what if”. You stop being an easy target. It’s a small system. But like all small systems, it scales beautifully.",
                "Kept up for a few weeks, the check becomes ordinary. You notice odd account mail sooner, and fewer updates pile up unread.",
            ),
        ],
    )
    return html


def demarket_post_839(html: str) -> str:
    return multi_replace(
        html,
        [
            (
                "This checklist is a practical 2026 baseline — not a compliance certificate, and not theatre.",
                "This checklist is a practical 2026 baseline — not a compliance certificate.",
            ),
            (
                "A small business that consistently does the boring basics outperforms one that buys a tool and ignores people.",
                "A small business that keeps up the boring basics is usually safer than one that buys a tool and ignores everyday habits.",
            ),
        ],
    )


POST_META = {
    191: {
        "title": "Magecart, E-Skimming and Script Monitoring",
        "excerpt": "Checkout skimming often hides in browser scripts. What Magecart and e-skimming look like, and why watching scripts matters.",
        "transform": demarket_post_191,
    },
    195: {
        "title": "When AI, Magecart and Clickjacking Overlap",
        "excerpt": "How skimming, clickjacking, and polished bait can meet at checkout — and what to verify before you pay.",
        "transform": demarket_post_195,
    },
    169: {
        "title": "Phishing and Deepfakes: Pause Before You Trust the Message",
        "excerpt": "Urgent bank-style alerts and familiar voices are not always real. How to slow down on phishing and deepfake scams.",
        "transform": demarket_post_169,
    },
    148: {
        "title": "Social Engineering Scams: Spot the Ask Before You Act",
        "excerpt": "How social engineering uses urgency and familiarity — and how to pause before you hand anything over.",
        "transform": demarket_post_148,
    },
    140: {
        "title": "The Human Firewall: Why Everyday Judgement Still Matters",
        "excerpt": "Tools help, but people still decide. What a “human firewall” means in ordinary work.",
        "transform": demarket_post_140,
    },
    239: {
        "title": "Everyday Cybersecurity Habits (No Cape Required)",
        "excerpt": "Simple habits for parents, freelancers, and small teams — no jargon required.",
        "transform": demarket_post_239,
    },
    288: {
        "title": "A 10-Minute Cyber Check",
        "excerpt": "A short daily check for devices, accounts, and updates — small enough to keep.",
        "transform": demarket_post_288,
    },
    839: {
        "title": "Small Business Cybersecurity Checklist 2026",
        "excerpt": "A practical 2026 checklist for micro and small businesses — access, updates, invoices, backups, people, and a 90-day starter plan.",
        "transform": demarket_post_839,
    },
}


def apply_local() -> None:
    mapping = {
        "home.html": demarket_home,
        "about.html": demarket_about,
        "resources.html": demarket_resources,
        "stories.html": demarket_stories,
        "scams.html": demarket_scams,
        "ai-hub.html": demarket_ai_hub,
    }
    for name, fn in mapping.items():
        path = VOICE / name
        path.write_text(fn(path.read_text(encoding="utf-8")), encoding="utf-8")
        print(f"local {name}")

    for pid, meta in POST_META.items():
        path = VOICE / f"post-{pid}.html"
        path.write_text(meta["transform"](path.read_text(encoding="utf-8")), encoding="utf-8")
        print(f"local post-{pid}.html -> {meta['title']}")


def deploy(m: MCP) -> None:
    pages = [
        (870, "Security e-Drift", "home.html"),
        (247, "About Security e-Drift and James Lugton", "about.html"),
        (837, "Resources", "resources.html"),
        (1006, "Stories", "stories.html"),
        (548, "Online scams — phishing, fakes and fraud tips", "scams.html"),
        (838, "AI, human risk & scams", "ai-hub.html"),
    ]
    for page_id, title, fname in pages:
        content = (VOICE / fname).read_text(encoding="utf-8")
        print(f"Updating page {page_id} ({title})…")
        print(m.tool("wp_update_page", {"page_id": page_id, "title": title, "content": content, "status": "publish"}))

    # Soften Yoast blurbs that oversell
    print(
        m.tool(
            "wp_yoast_update_post_seo",
            {
                "post_id": 838,
                "seo_title": "AI, human risk & scams | Security e-Drift",
                "og_title": "AI, human risk & scams | Security e-Drift",
                "twitter_title": "AI, human risk & scams | Security e-Drift",
                "meta_description": "Guides on AI tools, human risk, and everyday fraud from Security e-Drift.",
            },
        )
    )
    print(
        m.tool(
            "wp_yoast_update_post_seo",
            {
                "post_id": 837,
                "seo_title": "Resources | Security e-Drift",
                "og_title": "Resources | Security e-Drift",
                "twitter_title": "Resources | Security e-Drift",
                "meta_description": "Checklists, templates, and session notes from Security e-Drift.",
            },
        )
    )
    print(
        m.tool(
            "wp_yoast_update_post_seo",
            {
                "post_id": 839,
                "seo_title": "Small Business Cybersecurity Checklist 2026 | Security e-Drift",
                "og_title": "Small Business Cybersecurity Checklist 2026 | Security e-Drift",
                "twitter_title": "Small Business Cybersecurity Checklist 2026 | Security e-Drift",
                "meta_description": "A practical 2026 checklist for micro and small businesses from Security e-Drift.",
            },
        )
    )

    for pid, meta in POST_META.items():
        content = (VOICE / f"post-{pid}.html").read_text(encoding="utf-8")
        print(f"Updating post {pid} ({meta['title']})…")
        print(
            m.tool(
                "wp_update_post",
                {
                    "post_id": pid,
                    "title": meta["title"],
                    "content": content,
                    "excerpt": meta["excerpt"],
                    "status": "publish",
                },
            )
        )


def main() -> int:
    token = os.environ.get("WP_API_TOKEN", "").strip()
    if not token:
        print("WP_API_TOKEN required", file=sys.stderr)
        return 2

    apply_local()

    if "--local-only" in sys.argv:
        print("Local files updated only.")
        return 0

    m = MCP(token)
    m.call(
        "initialize",
        {
            "protocolVersion": "2025-11-25",
            "capabilities": {},
            "clientInfo": {"name": "edrift-demarket", "version": "1.0"},
        },
    )
    m.notify("notifications/initialized")
    deploy(m)
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
