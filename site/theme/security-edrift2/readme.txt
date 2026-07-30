=== Security e-Drift 2 ===
Contributors: lugton
Requires at least: 6.3
Tested up to: 6.7
Requires PHP: 7.4
Stable tag: 2.0.0
License: GPLv2 or later
License URI: https://www.gnu.org/licenses/gpl-2.0.html
Template: kadence

Kadence child theme for https://blog.lugton.co.uk/ (Security e-Drift).

== Description ==

Version 2 packages the marketing CSS patches, Stories page template, body-class
hooks used by existing selectors, and Yoast twitter:site hygiene (@drift strip).

== Important ==

The production site still uses many PHP template-parts from security-edrift 1.x
(series hubs, archive hero, chapter nav, etc.). Those files are not bundled here
because they are not publicly readable. Prefer the overlay install in README.md
before activating this theme on production.

== Changelog ==

= 2.0.0 =
* New theme slug security-edrift2
* Bundled assets/edrift.css = edrift.css + edrift-patches.css
* Stories page template (page-stories.php)
* Strip invalid Yoast twitter:site @drift
* Body classes: security-edrift-modern, security-edrift-reader
