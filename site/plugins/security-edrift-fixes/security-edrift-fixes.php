<?php
/**
 * Plugin Name: Security e-Drift Fixes
 * Description: Strips invalid Yoast twitter:site @drift until cleared in Yoast Social settings. Optional if the same filter is loaded from the child theme functions-edrift-fixes.php.
 * Version: 1.0.0
 * Author: Lugton
 *
 * Install (optional alternate to theme include):
 *   wp-content/plugins/security-edrift-fixes/security-edrift-fixes.php → Activate
 *
 * Permanent Yoast fix:
 *   Yoast SEO → Settings → Social → Twitter username → delete @drift → Save
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

add_filter( 'wpseo_twitter_site', 'edrift_plugin_strip_invalid_twitter_site', 20 );

/**
 * @param string $site Handle from Yoast.
 * @return string
 */
function edrift_plugin_strip_invalid_twitter_site( $site ) {
	$normalized = strtolower( ltrim( trim( (string) $site ), '@' ) );
	if ( '' === $normalized || 'drift' === $normalized ) {
		return '';
	}
	return $site;
}
