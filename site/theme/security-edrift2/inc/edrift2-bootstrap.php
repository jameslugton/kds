<?php
/**
 * Security e-Drift 2 — overlay bootstrap.
 *
 * Prefer requiring this from a copied v1 functions.php so you keep live hooks:
 *
 *   require_once get_stylesheet_directory() . '/inc/edrift2-bootstrap.php';
 *
 * When using this file, comment out or remove the duplicate logic in the root
 * functions.php, or delete root functions.php enqueue blocks that conflict.
 *
 * @package security-edrift2
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

if ( ! defined( 'EDRIFT2_VERSION' ) ) {
	define( 'EDRIFT2_VERSION', '2.0.0' );
}

if ( ! function_exists( 'edrift2_enqueue_styles' ) ) {
	/**
	 * Enqueue parent + child styles and bundled e-Drift CSS.
	 */
	function edrift2_enqueue_styles() {
		$parent_handle = 'kadence-global';
		if ( ! wp_style_is( $parent_handle, 'registered' ) && ! wp_style_is( $parent_handle, 'enqueued' ) ) {
			$parent_handle = 'kadence-style';
			wp_enqueue_style(
				$parent_handle,
				get_template_directory_uri() . '/style.css',
				array(),
				wp_get_theme( get_template() )->get( 'Version' )
			);
		}

		wp_enqueue_style(
			'security-edrift2-fonts',
			'https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=Lora:ital,wght@0,400;0,600;1,400&display=swap',
			array(),
			null
		);

		wp_enqueue_style(
			'security-edrift2',
			get_stylesheet_uri(),
			array( $parent_handle ),
			EDRIFT2_VERSION
		);

		wp_enqueue_style(
			'security-edrift-css',
			get_stylesheet_directory_uri() . '/assets/edrift.css',
			array( 'security-edrift2' ),
			EDRIFT2_VERSION
		);
	}
	add_action( 'wp_enqueue_scripts', 'edrift2_enqueue_styles', 20 );
}

if ( ! function_exists( 'edrift2_body_classes' ) ) {
	/**
	 * @param string[] $classes Body classes.
	 * @return string[]
	 */
	function edrift2_body_classes( $classes ) {
		$classes[] = 'security-edrift-modern';
		$classes[] = 'security-edrift-reader';
		return $classes;
	}
	add_filter( 'body_class', 'edrift2_body_classes' );
}

if ( ! function_exists( 'edrift2_strip_invalid_twitter_site' ) ) {
	/**
	 * @param string $site Twitter site handle from Yoast.
	 * @return string
	 */
	function edrift2_strip_invalid_twitter_site( $site ) {
		$normalized = strtolower( ltrim( trim( (string) $site ), '@' ) );
		if ( '' === $normalized || 'drift' === $normalized ) {
			return '';
		}
		return $site;
	}
	add_filter( 'wpseo_twitter_site', 'edrift2_strip_invalid_twitter_site', 20 );
}

if ( ! function_exists( 'edrift2_register_stories_page_template' ) ) {
	/**
	 * @param array $templates Page templates.
	 * @return array
	 */
	function edrift2_register_stories_page_template( $templates ) {
		$templates['page-stories.php'] = __( 'Stories', 'security-edrift2' );
		return $templates;
	}
	add_filter( 'theme_page_templates', 'edrift2_register_stories_page_template' );
}
