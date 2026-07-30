# Apply Security e-Drift marketing & trust fixes

This package implements the review actions for [blog.lugton.co.uk](https://blog.lugton.co.uk/).

**Brand title (match logo):** `Security e-Drift` — with tagline `the quiet compromise`.  
**Promise:** Cybersecurity that stays calm — so you can stay sharp.

## Flagship deploy (preferred)

```bash
export WP_API_TOKEN='…'   # never commit; rotate if shared
python3 scripts/deploy-flagship.py
```

Updates Home, Resources, About, site title/description, and AI hub callout.

## What’s included

| Item | Path |
| --- | --- |
| Homepage rewrite | `site/content/homepage.html` |
| Privacy policy (UK GDPR aligned) | `site/content/privacy-policy.html` |
| Nav IA (6 top-level items) | `site/content/nav-ia.md` |
| Footer HTML | `site/content/footer.html` |
| Brand casing / tagline | `site/brand.md` |
| Theme CSS patches (hero, CTAs, footer, motion) | `site/theme/edrift-patches.css` |
| Subscribe hardening PHP | `security/subscribe-endpoint.php` |
| Security checklist | `security/hardening-checklist.md` |
| MCP apply helper | `scripts/apply-via-mcp.py` |

## Apply (recommended order)

### A. With Easy MCP AI token (content)

```bash
export WP_API_TOKEN='your-token'   # never commit
python3 scripts/apply-via-mcp.py           # discover tools
python3 scripts/apply-via-mcp.py --apply   # write Home + Privacy if tools match
```

If tool names differ, copy HTML from `site/content/` into wp-admin manually (Pages → Home / Privacy Policy).

### B. Theme CSS

1. In the child theme `security-edrift`, open `assets/edrift.css`.
2. Append contents of `site/theme/edrift-patches.css`.
3. Bump version in `style.css` and the `edrift.css?ver=` enqueue (e.g. `1.5.5`).

### C. Navigation & footer

1. Appearance → Menus: rebuild primary menu from `site/content/nav-ia.md`.
2. Footer builder / HTML widget: paste `site/content/footer.html`.
3. Remove **Affiliate disclosure** from primary nav (keep in footer).

### D. Privacy / consent / security

1. Publish privacy HTML (page ID 251).
2. Confirm cookie consent banner UI is visible and wired to Site Kit Consent Mode.
3. Deploy `security/subscribe-endpoint.php` into child theme `functions.php` (or MU-plugin).
4. Complete `security/hardening-checklist.md` (HSTS, MCP lockdown, rotate token, fix Twitter `@drift`).

### E. Brand

1. Set WordPress **Site title** and Home page title to **Security e-Drift** (match the logo — see `site/brand.md`).
2. Keep logo tagline **the quiet compromise** with the brand lockup on home/footer/product headers.
3. Yoast → **SEO → General → Site representation**: Website name + alternate name = `Security e-Drift` (clears `og:site_name` / schema `WebSite.name` still stuck on `Security e-drift`).
4. Users → James Lugton → Biographical info: replace `e-drift` with `e-Drift`.
5. Optional: rename child theme `Theme Name` in `style.css` from `Security e-drift` → `Security e-Drift`.

## Verify

- Home hero shows brand-first title + two CTAs + atmospheric image.
- Primary nav has ~6 items.
- Footer shows Privacy / Terms / Affiliate / Contact / LinkedIn / RSS.
- Privacy page shows **Last updated: 30 July 2026**.
- Subscribe form includes honeypot field `company` (hidden).
- `curl -sI https://blog.lugton.co.uk/wp-json/easy-mcp-ai/v1/mcp` still returns **401** without a token.
