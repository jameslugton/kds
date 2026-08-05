# Editorial voice pass (Aug 2026)

Source-of-truth HTML after the demarketing pass lives in `site/content/voice/`.

Goals: keep Security e-Drift’s calm UK-plain tone; remove conversion hype, repetition,
unsupported claims (e.g. “coming soon” links that were already live), and stock AI-blog filler.

Deploy: `WP_API_TOKEN=… python3 scripts/demarket-voice.py` (uses files in `voice/`; prefer
manual deploy after local edits if posts were hand-fixed).

Flagship pages updated live: Home, About, Resources, Stories, Scams, AI hub.
Posts retitled/opened: 124, 140, 148, 150, 169, 191, 195, 200, 239, 261, 288, 318, 839.
