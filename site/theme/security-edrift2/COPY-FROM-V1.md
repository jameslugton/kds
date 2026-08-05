# Copy these from live `security-edrift` before production activate

Source (on server): `wp-content/themes/security-edrift/`  
Destination: `wp-content/themes/security-edrift2/`

Listed in the live theme `readme.txt` (v1). None of these are readable over HTTP (403).

## Required for parity with current production

```
page-series-hub.php
template-parts/content/series-hub.php
template-parts/content/series-chapter-nav.php
template-parts/content/archive.php
template-parts/content/home-hero.php
template-parts/content/series-spotlight.php
template-parts/content/series-intro.php
template-parts/content/single-entry.php
template-parts/content/entry.php
template-parts/content/entry_loop_header.php
```

Also copy any other `page-*.php`, `page-templates/`, or `template-parts/` present on the host that are not in this package.

## Do not blindly overwrite with this package

| Keep from v1 (merge) | Replace from this package |
| --- | --- |
| Existing `functions.php` hooks (series, REST, search, etc.) | `assets/edrift.css` (merged base + patches) |
| All `template-parts/**` | `style.css` (theme name/version/text domain) |
| `page-series-hub.php` and other page templates | Add `page-stories.php` |

After overlay, ensure `functions.php` still loads v1 behaviour **and** includes the v2 Twitter strip + Stories template registration (already in this package’s `functions.php` if you fully replace it — only safe if you first port every v1 hook into the new file).
