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

**Preferred:** install `security-edrift2` (merged CSS already in `assets/edrift.css`, version `2.0.0`).

Or on live `security-edrift`:

1. Open `assets/edrift.css`.
2. Append contents of `site/theme/edrift-patches.css` (or copy the merged file from `security-edrift2/assets/edrift.css`).
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

### E. Brand & shatterproof checklist

1. Site title **Security e-Drift**; home hero may stack the logo lockup; inner pages lead with the page H1.
2. Primary nav = **6 hubs only** (no article children) — see `site/content/nav-ia.md`.
3. Yoast → **SEO → General → Site representation**: Website name + alternate = `Security e-Drift`.
4. Users → James Lugton → bio: `Security e-Drift` casing.
5. Hide/retire `.edrift-reader-footer` (CSS in patches does this); keep one footer system.

### F. Theme package — Security e-Drift 2 (preferred)

Installable child theme: `site/theme/security-edrift2/`  
Upload zip: `site/theme/dist/security-edrift2.zip`

Includes merged CSS (`assets/edrift.css` = base + patches), Stories template, and Yoast `@drift` strip.

**Do not blind-activate on production** without overlaying live v1 PHP template-parts (series hubs, archive, etc.). See `site/theme/security-edrift2/README.md` and `COPY-FROM-V1.md`.

Preferred cutover: copy live `security-edrift` → `security-edrift2` on the host, overlay this package, merge `functions.php`, then activate.

### F2. Theme file drops onto live `security-edrift` (Issues 1–3, no rename)

Child theme path: `wp-content/themes/security-edrift/` (not writable via MCP — copy via SFTP/file manager). Package: `site/theme/security-edrift/`.

1. **Twitter `@drift` (Yoast):** Copy `functions-edrift-fixes.php` and append lines from `functions.php.append` into existing `functions.php`. Then **Yoast SEO → Settings → Social → Twitter** → delete `@drift` → Save. No correct handle exists in options/code.
2. **Stories template:** Copy `page-stories.php`. Page **Stories** already exists at `/stories/` (id 1006). Assign template **Stories** under Page Attributes. Then **Appearance → Menus → Stories** → URL `/stories/` (do not change the menu URL from code).
3. **Company field:** Was hardcoded honeypot HTML on Home + Resources (not a widget/shortcode). Removed and redeployed via `deploy-flagship.py`.
4. **CSS:** Replace `assets/edrift.css` with the merged file from `security-edrift2/assets/edrift.css` (or append `edrift-patches.css`) and bump `?ver=`.

## Verify

- Home hero shows brand-first title + two CTAs + atmospheric image.
- Primary nav has ~6 items.
- Footer shows Privacy / Terms / Affiliate / Contact / LinkedIn / RSS.
- Privacy page shows **Last updated: 30 July 2026**.
- Subscribe form includes honeypot field `company` (hidden).
- `curl -sI https://blog.lugton.co.uk/wp-json/easy-mcp-ai/v1/mcp` still returns **401** without a token.
