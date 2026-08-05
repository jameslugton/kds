# Security e-Drift 2 (`security-edrift2`)

Installable Kadence child theme for [blog.lugton.co.uk](https://blog.lugton.co.uk/).

**Version:** 2.0.0  
**Parent:** `kadence`  
**Zip:** `site/theme/dist/security-edrift2.zip`

## What’s in this package

| File | Purpose |
| --- | --- |
| `style.css` | Theme header (`Template: kadence`, v2.0.0) |
| `functions.php` | Enqueue, body classes, `@drift` strip, Stories template register |
| `assets/edrift.css` | Base `edrift.css` **+** marketing `edrift-patches.css` |
| `page-stories.php` | Page template **Stories** (assign on page `/stories/`) |
| `inc/subscribe-endpoint.php` | Optional hardened REST subscribe (off by default) |

## Critical — do not blind-activate on production

Live **security-edrift** (1.5.4) also ships PHP overrides that this zip **cannot** include (HTTP 403 on theme PHP):

- `page-series-hub.php`
- `template-parts/content/archive.php`
- `template-parts/content/home-hero.php`
- `template-parts/content/series-*.php`
- `template-parts/content/single-entry.php`, `entry.php`, etc.

Activating a thin upload **without** those files will drop series hubs / archive customizations back to stock Kadence.

### Preferred cutover (overlay)

1. On the host (file manager or SFTP), **copy**  
   `wp-content/themes/security-edrift/` → `wp-content/themes/security-edrift2/`
2. Overlay this package’s files onto that copy (replace `style.css`, `functions.php` **carefully** — see below —, `assets/edrift.css`, add `page-stories.php`).
3. **functions.php merge:** keep any live-only hooks from v1 (series, subscribe, Relevanssi, etc.). Either:
   - Append the bodies of this package’s filters/enqueues into the copied v1 `functions.php`, **or**
   - Keep the copied v1 `functions.php` and add at the bottom:  
     `require_once get_stylesheet_directory() . '/inc/edrift2-bootstrap.php';`  
     (then rename this package’s `functions.php` logic into that include — see note below).
4. Appearance → Themes → activate **Security e-Drift 2**.
5. Pages → **Stories** (id 1006) → Template: **Stories** → Update.
6. Yoast → Social → Twitter → clear `@drift` → Save.

> Practical shortcut: if you only need CSS + Stories + Twitter strip **without** renaming the theme, keep activating `security-edrift` and overlay `assets/edrift.css` + `page-stories.php` + append the Twitter/Stories filters into the existing `functions.php` instead. Use this v2 theme when you want a clean slug/version bump.

### Upload-only (staging / rebuild)

1. Install + activate **Kadence**.
2. Appearance → Themes → Add New → Upload → `security-edrift2.zip` → Activate.
3. Copy the v1 template-parts listed in `COPY-FROM-V1.md` into this theme before relying on series pages in production.

## After activate checklist

- [ ] Site still shows series hub pages correctly
- [ ] Home / Resources / About look correct (patches now in theme CSS — inline `<style id="edrift-marketing-patches">` can be removed later)
- [ ] View source: no `twitter:site` `@drift`
- [ ] `/stories/` uses template Stories (or keep HTML cards until assigned)
- [ ] Primary menu Stories → `/stories/`

## Building the zip from this repo

```bash
cd site/theme
rm -f dist/security-edrift2.zip
zip -r dist/security-edrift2.zip security-edrift2 \
  -x 'security-edrift2/.DS_Store' 'security-edrift2/**/.DS_Store'
```
