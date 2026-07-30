# security-edrift child theme patches

Active theme on production: **security-edrift** (Kadence child) at  
`wp-content/themes/security-edrift/`.

PHP theme files are not writable over the public HTTP API (403). Copy these
files onto the server (SFTP, hosting file manager, or git deploy), then finish
the wp-admin steps below.

## Files to copy

| This package | Destination on server |
| --- | --- |
| `page-stories.php` | `wp-content/themes/security-edrift/page-stories.php` |
| `functions-edrift-fixes.php` | `wp-content/themes/security-edrift/functions-edrift-fixes.php` |
| Lines from `functions.php.append` | **Append** to existing `functions.php` (do not replace the whole file) |

## ISSUE 1 — Twitter `@drift`

1. Copy `functions-edrift-fixes.php` and append the require from `functions.php.append`.
2. In wp-admin: **Yoast SEO → Settings → Social → Twitter username** → delete `@drift` → Save.

No correct Twitter/X handle exists in site options or theme code; the filter strips `@drift` / empty values from `twitter:site` output.

## ISSUE 2 — Stories URL

1. Copy `page-stories.php` into the child theme.
2. **Pages → Add New** → title `Stories`, slug `stories` → Template: **Stories** → Publish.
3. **Appearance → Menus** → primary menu → **Stories** item → set URL to `/stories/` → Save Menu.

Do not change the menu URL from application code.

## ISSUE 3 — Company field

The subscribe form is **hardcoded HTML** in Home (page 870) and Resources (page 837), not a widget or shortcode. The Company input (old honeypot) is removed from those content files and redeployed via `scripts/deploy-flagship.py`.
