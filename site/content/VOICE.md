# Editorial voice + design pass (Aug 2026)

Source-of-truth HTML lives in `site/content/voice/`.

## Voice
Keep Security e-Drift’s calm UK-plain tone; remove conversion hype, repetition,
unsupported claims, and stock AI-blog filler.

Deploy voice: `WP_API_TOKEN=… python3 scripts/demarket-voice.py`

## Design
Removed SaaS hub landings (atmos glows, feature pills, brand restamp on inner pages).
Home uses a quiet photo hero (`edrift-hero-simple`). Inner hubs use `edrift-product-hero`.
CSS: `site/theme/edrift-design-fixes.css` (inlined on hubs + reusable block 572).

Deploy design: `WP_API_TOKEN=… python3 scripts/fix-design.py`

Also append `edrift-design-fixes.css` into live `assets/edrift.css` via SFTP when possible
(theme PHP may still add `body.edrift-hub-landing` on some page IDs; the fixes neutralize it).
