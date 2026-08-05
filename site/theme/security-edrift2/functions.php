<?php
/**
 * Security e-Drift 2 — Kadence child theme.
 *
 * Standalone activate: this file loads the bootstrap.
 * Overlay onto a copied v1 theme: keep that theme’s functions.php hooks and add:
 *   require_once get_stylesheet_directory() . '/inc/edrift2-bootstrap.php';
 * then remove or replace this root file’s require if it would double-load.
 *
 * @package security-edrift2
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

require_once get_stylesheet_directory() . '/inc/edrift2-bootstrap.php';

/*
 * Optional: hardened subscribe REST endpoint.
 * Uncomment only if nothing else already registers edrift/v1/subscribe.
 *
 * require_once get_stylesheet_directory() . '/inc/subscribe-endpoint.php';
 */
