#!/usr/bin/env python3
"""Humanize Security e-Drift posts: strip AI-stock patterns and formula templates.

Requires WP_API_TOKEN. Rewrites high-risk posts and de-templates the AI/basics series.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HDIR = ROOT / "site/content/voice/humanize"
MCP_URL = "https://blog.lugton.co.uk/wp-json/easy-mcp-ai/v1/mcp"

AFFILIATE = '<!-- wp:block {"ref":572} /-->\n\n'


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


def strip_emoji(text: str) -> str:
    return re.sub(
        r"[🚀🎯🛡️🔍🕷️🧠✅⚠️🔥💡📌🔐✨🌟💳🔒🚨❌⭐️✔︎☐☑︎]\s*",
        "",
        text,
    )


def detemplate_series(html: str, closing: str) -> str:
    """Remove repeated Remember this / A habit to keep scaffolding; vary the close."""
    html = strip_emoji(html)
    # Callout "Remember this:" → quieter inline
    html = re.sub(
        r"(?is)<p[^>]*>\s*<strong>\s*Remember this:\s*</strong>\s*(.*?)</p>",
        r"<p>\1</p>",
        html,
    )
    html = re.sub(r"(?m)^\s*Remember this:\s*", "", html)
    # Heading variants
    html = re.sub(
        r"(?is)(?:<h[2-4][^>]*>\s*)?A habit to keep(?:\s*</h[2-4]>)?",
        "",
        html,
    )
    html = re.sub(r"(?m)^\s*A habit to keep\s*", "", html)
    html = re.sub(
        r"(?is)<h[2-4][^>]*>\s*A practical rule of thumb\s*</h[2-4]>",
        "<h2>What I tell people to try first</h2>",
        html,
    )
    html = re.sub(
        r"(?is)<h[2-4][^>]*>\s*A one-week experiment[^\n<]*</h[2-4]>",
        "<h2>Try this for a week</h2>",
        html,
    )
    html = re.sub(
        r"(?is)<h[2-4][^>]*>\s*A habit to keep\s*</h[2-4]>",
        "",
        html,
    )
    # Replace trailing habit paragraph if still present with unique closing
    if closing and "Related:" not in html[-400:]:
        # append closing before hub links if needed
        pass
    # Swap final "A habit to keep ..." free-text blocks
    html = re.sub(
        r"(?is)A habit to keep\s+.*?(?=(?:Put the rules|For the wider|Hub:|More in the|Related:|NCSC|$))",
        closing + " ",
        html,
        count=1,
    )
    return html


# --- Full rewrites (plain HTML + affiliate block) ---

REWRITES: dict[int, dict] = {
    138: {
        "title": "Ransomware in Plain English",
        "excerpt": "What ransomware actually does to a laptop or small shop — and the boring habits that limit the damage.",
        "content": AFFILIATE
        + """
<p>Ransomware locks your files and asks for money. That is the whole trick. It is not clever theatre. It is a padlock on the wrong side of the door, with a note taped to it.</p>
<p>I see the same pattern in small places: someone clicks a rushed attachment, or a fake “invoice” lands while the shop is busy. A few hours later the till laptop will not open the shared folder, and the backup turns out to be the same drive that just got encrypted.</p>
<h2>What it looks like on an ordinary Tuesday</h2>
<p>Files rename themselves. Documents will not open. Sometimes a full-screen message appears with a countdown and a cryptocurrency address. Sometimes there is no message at all — just silence where your photos or invoices used to be.</p>
<p>Paying does not guarantee a key. Paying can also mark you as someone who pays. I am not going to pretend there is a neat answer once you are already locked out. The useful work happens earlier.</p>
<h2>What actually helps</h2>
<ul>
<li><strong>Backups you can restore from cold.</strong> A copy that is not plugged in all day. Test a restore once, even if it feels tedious.</li>
<li><strong>Updates.</strong> Old flaws are how a lot of this still arrives.</li>
<li><strong>Admin rights sparingly.</strong> Daily browsing does not need the keys to the kingdom.</li>
<li><strong>Attachment suspicion.</strong> Unexpected zip files and “enable macros” documents are still common.</li>
</ul>
<p>If you run a small team, write down who to call and which backups exist — before anyone needs that list at 8pm.</p>
<p>Related: <a href="/malware-basics-protect-your-devices-in-plain-english/">malware basics</a> · <a href="/complete-small-business-cybersecurity-checklist-2026/">SMB checklist</a> · <a href="/scams/">scams hub</a>.</p>
""",
    },
    193: {
        "title": "The Good, the Bad, and the Ugly of AI",
        "excerpt": "Useful AI, messy AI, and the bits that quietly shift judgement — without the hype reel.",
        "content": AFFILIATE
        + """
<p>AI is already in the tools people use between school runs and invoices: drafts, summaries, photo tidy-ups, “what does this email mean?” That can be genuinely handy. It can also sand the caution off a decision that needed a slower second look.</p>
<h2>The good</h2>
<p>Used as a helper for thinking, AI is often fine. It can sketch a reply you then rewrite. It can explain an error message in normal English. It can suggest a spreadsheet fix you still check. The important part is that you stay the person who sends, pays, or publishes.</p>
<h2>The bad</h2>
<p>It is confident when it is wrong. It will invent a citation, a policy clause, or a “fact” that sounds right. If you paste customer details or passwords into a random chat box, you have also handed them to a system you do not run. Convenience has a memory.</p>
<h2>The ugly</h2>
<p>Scams get a polish. Voices can be faked. Job applications and profiles can be mass-produced. The ugliest part for small teams is not sci-fi — it is a believable message that arrives at 4:55pm asking for a “quick payment change.”</p>
<p>My working rule is simple: let AI advise. Do not let it act with money, mailbox identity, or live systems unless there is a narrow job and a human confirm. More on that split here: <a href="/ai-advisor-or-ai-actor-why-blast-radius-matters/">advisor vs actor</a>.</p>
<p>Related: <a href="/before-you-paste-it-into-the-bot-ai-risks-worth-slowing-down-for/">before you paste</a> · <a href="/ai-human-risk-scams/">AI hub</a>.</p>
""",
    },
    242: {
        "title": "Always On, Always at Risk",
        "excerpt": "Familiar places still have awkward network habits — cafés, trains, shared tablets, and the router at home.",
        "content": AFFILIATE
        + """
<p>Feeling comfortable somewhere is not the same as being careful with the network. Most of the awkwardness I see is ordinary: a phone that auto-joins café Wi‑Fi, a shared tablet with work email still logged in, a hotel login page that looks almost right.</p>
<h2>Familiar places still need a pause</h2>
<p>At home, update the router when you remember, and do not leave the admin password as the one printed on the sticker forever. On a train or in a café, prefer mobile data for banking and anything with a password. If you must use public Wi‑Fi, keep the session short and avoid “remember this network.”</p>
<h2>Shared devices</h2>
<p>Family tablets mix homework, shopping, and sometimes a work mailbox. That mix is where sessions linger. Sign out of the accounts that matter. Use a separate browser profile if two people share a laptop.</p>
<h2>QR codes and “helpful” cables</h2>
<p>A QR sticker on a parking meter or a free USB cable on a counter can be genuine. It can also be a shortcut somewhere you did not mean to go. If the prompt feels off, type the address yourself.</p>
<p>None of this needs a cape. It needs a few boring defaults you keep when you are tired.</p>
<p>Related: <a href="/cybersecurity-at-home/">cybersecurity at home</a> · <a href="/scams/">scams hub</a>.</p>
""",
    },
    244: {
        "title": "Spot It, Stop It: Saying Something About Online Scams",
        "excerpt": "If a payment page or message feels wrong, walking away — and warning someone else — still matters.",
        "content": AFFILIATE
        + """
<p>If something online feels off, do not talk yourself out of that feeling. A lot of fraud still works because people stay polite and quiet.</p>
<h2>Payment pages that do not look like themselves</h2>
<p>Check the address bar. Look for https and a domain that matches the company you think you are paying. Be wary of pages that ask for a card PIN, “verification photos,” or extra personal details a normal checkout never needs. Logos that look stretched or slightly wrong are a clue, not a quirk.</p>
<h2>Messages that want speed and secrecy</h2>
<p>“Don’t tell anyone” and “do this in the next ten minutes” are not how banks and suppliers usually talk. Call them on a number you already have — not the number in the message.</p>
<h2>Say something</h2>
<p>If you nearly fell for it, tell the person next to you. If a colleague almost paid a fake invoice, say it in the group chat. Scams spread through silence as much as through software.</p>
<p>Before you enter card details: did you type the address yourself, does the page look normal for that firm, and would you be happy showing the screen to someone you trust?</p>
<p>Related: <a href="/scams/">online scams hub</a> · <a href="/what-to-do-if-youve-been-caught-out-by-a-scam/">what to do after a miss</a>.</p>
""",
    },
    175: {
        "title": "How to Spot Phishing Without Overthinking It",
        "excerpt": "Phishing still works on tired evenings. A short habit beats trying to memorise every scam variant.",
        "content": AFFILIATE
        + """
<p>Phishing is a message that wants you to act before you think — sign in, send money, share a code. The brand looks familiar. The pressure is the point.</p>
<p>You will not catch every new variant. You do not need to. You need one slow habit for anything that asks for credentials or cash.</p>
<h2>What usually gives it away</h2>
<ul>
<li>Unexpected urgency (“account locks in 15 minutes”).</li>
<li>A link you did not go looking for.</li>
<li>A request for passwords, codes, or payment changes through a channel that started with them, not you.</li>
<li>Odd wording, or perfect wording that still feels slightly off for that organisation.</li>
</ul>
<h2>What to do instead</h2>
<p>Do not use the link in the message. Open the site or app yourself from a bookmark or by typing the address. If it is a phone call, hang up and dial a number from the back of a card or a statement.</p>
<p>Turn on multi-factor authentication where you can — especially email. Email is the spare key to everything else.</p>
<p>Related: <a href="/phishing-attacks-how-to-spot-and-avoid-scam-emails/">phishing basics</a> · <a href="/scams/">scams hub</a> · <a href="https://www.ncsc.gov.uk/collection/phishing-scams" rel="noopener noreferrer">NCSC phishing guidance</a>.</p>
""",
    },
    282: {
        "title": "Covert Malware: The Quiet Kind",
        "excerpt": "Not all malware smashes the window. Some of it sits quietly and listens — and ordinary habits still matter.",
        "content": AFFILIATE
        + """
<p>Some malware is noisy: locked screens, pop-ups, a machine that suddenly crawls. Covert malware is quieter. It tries to blend in, collect what it can, and stay longer than a smash-and-grab.</p>
<p>You may not get a dramatic warning. You might get odd battery drain, unfamiliar browser helpers, or outbound connections you never meant to allow. On a small shop PC, that can mean customer details leaving through a door nobody is watching.</p>
<h2>What helps in ordinary places</h2>
<ul>
<li>Keep the OS and browser updated.</li>
<li>Use built-in protection; skip random “optimiser” downloads.</li>
<li>Limit admin rights for day-to-day use.</li>
<li>Be stubborn about unexpected installers and email attachments.</li>
</ul>
<p>If a device starts behaving strangely after a rushed download, disconnect it from the network and get a clean look at what changed — do not keep logging into banking on it “just to finish something.”</p>
<p>Related: <a href="/malware-basics-protect-your-devices-in-plain-english/">malware basics</a> · <a href="/shadow-ai-at-work-and-at-home/">shadow AI</a>.</p>
""",
    },
    270: {
        "title": "Cybersecurity at the Pier: Don’t Take the Bait",
        "excerpt": "A pier story about shiny bait — and why curiosity still needs a pause online.",
        "content": AFFILIATE
        + """
<p>Picture a pier on a bright day. You spot something shiny under the boards — a bottle, a phone, a “prize.” You reach for it. It is tied to a rope. Suddenly you are the one being pulled.</p>
<p>Online bait works the same way. The shiny object is a too-good email, a fake delivery text, a QR code that promises a shortcut. The rope is the link, the attachment, or the login page that was waiting for your hands.</p>
<p>The useful habit is not paranoia. It is refusing to grab the first shiny thing when you did not go looking for it. Open the bank app yourself. Type the retailer address yourself. Call the courier on a number from the parcel, not the text.</p>
<p>Curiosity is fine. Untested shortcuts are how people get dragged off the pier.</p>
<p>Related: <a href="/scams/">scams hub</a> · <a href="/how-scams-reach-you-and-how-to-spot-them-before-they-catch-you/">how scams reach you</a>.</p>
""",
    },
    266: {
        "title": "Cybersecurity Hitchhikers: When Trust Hands Over the Keys",
        "excerpt": "A road-trip metaphor for the helper you invited in — plugins, staff access, and ‘temporary’ accounts that linger.",
        "content": AFFILIATE
        + """
<p>You are on a road trip. Someone thumbs a lift. They seem fine. You chat. Miles later you stop for fuel, and they already know where you keep the spare key.</p>
<p>A lot of digital risk looks like that hitchhiker: a browser extension that “helps,” a contractor login that was never removed, a shared password in a chat thread, a plugin installed for one weekend and left forever.</p>
<p>Trust is not the problem. Unreviewed access is. Give people and tools the least they need. Put an end date on temporary accounts. Review who can see the mailbox and the accounts folder every so often — especially after someone leaves.</p>
<p>If something goes wrong, revoke first, tidy later. Politeness should not keep a stranger in the passenger seat.</p>
<p>Related: <a href="/complete-small-business-cybersecurity-checklist-2026/">SMB checklist</a> · <a href="/if-someone-else-is-steering-your-ai/">who is steering your AI</a>.</p>
""",
    },
}

SERIES_CLOSINGS = {
    863: "Before you connect a tool to mail or money, ask what else that permission touches. If the honest answer is “everything,” keep it as advisor.",
    788: "Do not give unsupervised action on day one. Know how you would disconnect it, watch the first batch, and keep money and mailbox recovery under human hands.",
    789: "One person, one AI login, on devices you control. Convenience is not worth a stranger reading last month’s prompts.",
    790: "Watch the first batch. If the first few outputs look odd, stop — do not “let it finish” out of politeness to the machine.",
    791: "If you would feel awkward naming the tool to a partner or manager, that is a signal to slow down and use an approved option instead.",
    87: "Unexpected link plus a password ask means stop. Open the site yourself.",
    88: "Start with email, banking, and a password manager. Widen from there.",
    89: "If an install was not something you searched for on purpose, decline it.",
    90: "Pause is still the defence. Verify on a channel you already trust.",
    91: "Auto-update where you can; glance at the router monthly; never install an “update” from a stranger’s link.",
}


def fix_150(html: str) -> str:
    html = strip_emoji(html)
    html = html.replace(
        "This is where cyber hygiene comes in. It’s not just for tech experts —it’s for anyone who wants to stay safe online . Just like we lock our doors",
        "Think of it like locking the door",
    )
    html = re.sub(
        r"This is where cyber hygiene comes in\..*?Just like we",
        "Think of it like how we",
        html,
        count=1,
        flags=re.S,
    )
    html = re.sub(
        r"So, the next time you see a software update pop up,.*?out of reach of cybercriminals\.",
        "When an update appears, do it when you can. When an email feels wrong, pause. Treat passwords like house keys — few copies, none on sticky notes under the keyboard.",
        html,
        count=1,
        flags=re.S,
    )
    return html


def fix_169(html: str) -> str:
    html = strip_emoji(html)
    html = html.replace("## Common phishing tricks", "## Common phishing tricks")
    html = re.sub(
        r"Share this knowledge to keep family & friends safe\.\s*",
        "",
        html,
    )
    html = re.sub(
        r"Closing note\s*",
        "",
        html,
    )
    return html


def fix_140(html: str) -> str:
    html = strip_emoji(html)
    html = re.sub(
        r"What Is the Human Firewall\?",
        "What people mean by it",
        html,
    )
    html = html.replace(
        "The human firewall refers to the collective security awareness and behaviors of individuals within an organization",
        "In practice it means the people who open the mail, approve the payment, and decide whether a request feels wrong",
    )
    return html


def fix_195(html: str) -> str:
    html = strip_emoji(html)
    html = html.replace("Closing note", "")
    html = re.sub(
        r"Cybercriminals rely on human nature, urgency and distraction\.\s*",
        "",
        html,
    )
    return html


def fix_172(html: str) -> str:
    return strip_emoji(html)


def fix_239(html: str) -> str:
    html = strip_emoji(html)
    html = html.replace("digital resilience", "a bit more safety for the people around you")
    return html


def fix_288(html: str) -> str:
    return strip_emoji(html)


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
            "clientInfo": {"name": "edrift-humanize", "version": "1.0"},
        },
    )
    m.notify("notifications/initialized")

    # Full rewrites
    for pid, meta in REWRITES.items():
        path = HDIR / f"post-{pid}.html"
        path.write_text(meta["content"].strip() + "\n", encoding="utf-8")
        print(f"rewrite {pid} {meta['title']}")
        print(
            m.tool(
                "wp_update_post",
                {
                    "post_id": pid,
                    "title": meta["title"],
                    "content": meta["content"].strip(),
                    "excerpt": meta["excerpt"],
                    "status": "publish",
                },
            )
        )

    # Series detemplating
    for pid, closing in SERIES_CLOSINGS.items():
        raw = (HDIR / f"post-{pid}.html").read_text(encoding="utf-8")
        # if we already fully rewrote, skip
        if pid in REWRITES:
            continue
        new = detemplate_series(raw, closing)
        # Ensure unique closing appears once near end if habit block removed poorly
        if closing.split()[0] not in new[-500:]:
            new = new.rstrip() + "\n\n<p>" + closing + "</p>\n"
        (HDIR / f"post-{pid}.html").write_text(new, encoding="utf-8")
        print(f"detemplate {pid}")
        print(m.tool("wp_update_post", {"post_id": pid, "content": new, "status": "publish"}))

    # Surgical fixes
    surgical = {
        150: fix_150,
        169: fix_169,
        140: fix_140,
        195: fix_195,
        172: fix_172,
        239: fix_239,
        288: fix_288,
    }
    for pid, fn in surgical.items():
        raw = (HDIR / f"post-{pid}.html").read_text(encoding="utf-8")
        new = fn(raw)
        (HDIR / f"post-{pid}.html").write_text(new, encoding="utf-8")
        print(f"surgical {pid}")
        print(m.tool("wp_update_post", {"post_id": pid, "content": new, "status": "publish"}))

    # Strip emoji from any remaining downloaded high-risk if missed
    for pid in [244, 175, 282, 270, 266]:  # rewritten already
        pass

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
