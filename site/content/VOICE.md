# Editorial voice + design pass (Aug 2026)

Source-of-truth HTML lives in `site/content/voice/`.

## Voice

Author voice (locked): [`VOICE-CARD.md`](./VOICE-CARD.md) (grilling, Aug 2026).  
Use that card for all new and revised blog copy. If it isn’t James’s style and vision, it doesn’t go live.

**Voice-card revamp (Aug 2026):** flagship hubs + **all non-story posts** under `site/content/voice/revamp/`.  
Story chapters (Jim’s shop / river) left alone.  
Deploy all: `WP_API_TOKEN=… python3 scripts/revamp-voice-all.py`  
Deploy first wave only: `WP_API_TOKEN=… python3 scripts/revamp-voice.py`

Short reminder: calm UK-plain for non-technical readers; sharp only at the click/transfer moment; jargon as plain action then `(mfa)`; empower with a self-check, not a sales ending. Remove conversion hype, repetition, unsupported claims, and stock AI-blog filler.

Deploy older demarket pass: `WP_API_TOKEN=… python3 scripts/demarket-voice.py`

## Design
Removed SaaS hub landings (atmos glows, feature pills, brand restamp on inner pages).
Home uses a quiet photo hero (`edrift-hero-simple`). Inner hubs use `edrift-product-hero`.
CSS: `site/theme/edrift-design-fixes.css` (inlined on hubs + reusable block 572).

Deploy design: `WP_API_TOKEN=… python3 scripts/fix-design.py`

Also append `edrift-design-fixes.css` into live `assets/edrift.css` via SFTP when possible
(theme PHP may still add `body.edrift-hub-landing` on some page IDs; the fixes neutralize it).

## Humanize pass (AI-style cleanup)

Detector note: polished editorial can still score “AI-assisted.” We strip stock tells
(emoji headers, “Remember this / A habit to keep” templates, “Final Thoughts”,
ever-evolving openers) and rewrite the worst older posts in plain Yorkshire-blog voice.

Deploy: `WP_API_TOKEN=… python3 scripts/humanize-content.py`

Story chapters (Jim’s shop / river) were left alone — they already read human.
